from collections import deque
from logging import getLogger

import asyncio
from h2 import events
from h2 import settings
from h2.connection import H2Connection
from h2.exceptions import NoSuchStreamError, StreamClosedError

__all__ = ['H2Protocol']
logger = getLogger(__package__)


@asyncio.coroutine
def _wait_for_events(*events_):
    while True:
        yield from asyncio.wait([event.wait() for event in events_])
        if all([event.is_set() for event in events_]):
            return


class _StreamEndedException(Exception):
    def __init__(self, bufs=None):
        if bufs is None:
            bufs = []
        self.bufs = bufs


class CallableEvent(asyncio.Event):
    def __init__(self, func, *, loop=None):
        super().__init__(loop=loop)
        self._func = func

    @asyncio.coroutine
    def wait(self):
        while not self._func():
            self.sync()
            yield from super().wait()

    def sync(self):
        if self._func():
            self.set()
        else:
            self.clear()

    def is_set(self):
        self.sync()
        return super().is_set()


class H2Stream:
    def __init__(self, stream_id, window_getter, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._stream_id = stream_id
        self._window_getter = window_getter

        self._wlock = asyncio.Lock(loop=loop)
        self._window_open = CallableEvent(self._is_window_open, loop=loop)

        self._rlock = asyncio.Lock(loop=loop)
        self._buffers = deque()
        self._buffer_size = 0
        self._buffer_ready = asyncio.Event(loop=loop)
        self._response = asyncio.Future(loop=loop)
        self._trailers = asyncio.Future(loop=loop)
        self._eof_received = False
        self._closed = False

    @property
    def id(self):
        return self._stream_id

    @property
    def window_open(self):
        return self._window_open

    @property
    def rlock(self):
        return self._rlock

    @property
    def wlock(self):
        return self._wlock

    @property
    def buffer_size(self):
        return self._buffer_size

    @property
    def response(self):
        return self._response

    @property
    def trailers(self):
        return self._trailers

    def _is_window_open(self):
        try:
            window = self._window_getter(self._stream_id)
        except NoSuchStreamError:
            self._closed = True
            return True
        else:
            return window > 0

    def feed_data(self, data):
        if data:
            self._buffers.append(data)
            self._buffer_size += len(data)
            self._buffer_ready.set()

    def feed_eof(self):
        self._eof_received = True
        self._buffer_ready.set()
        self.feed_trailers({})

    def feed_response(self, headers):
        self._response.set_result(headers)

    def feed_trailers(self, headers):
        if not self._trailers.done():
            self._trailers.set_result(headers)

    @asyncio.coroutine
    def read_frame(self):
        yield from self._buffer_ready.wait()
        rv = b''
        if self._buffers:
            rv = self._buffers.popleft()
            self._buffer_size -= len(rv)
        if not self._buffers:
            if self._eof_received:
                raise _StreamEndedException([rv])
            else:
                self._buffer_ready.clear()
        return rv

    @asyncio.coroutine
    def read_all(self):
        yield from self._buffer_ready.wait()
        rv = []
        rv.extend(self._buffers)
        self._buffers.clear()
        self._buffer_size = 0
        if self._eof_received:
            raise _StreamEndedException(rv)
        else:
            self._buffer_ready.clear()
            return rv

    @asyncio.coroutine
    def read(self, n):
        yield from self._buffer_ready.wait()
        rv = []
        count = 0
        while n > count and self._buffers:
            buf = self._buffers.popleft()
            count += len(buf)
            if n < count:
                rv.append(buf[:n - count])
                self._buffers.appendleft(buf[n - count:])
                count = n
            else:
                rv.append(buf)
        self._buffer_size -= count
        if not self._buffers:
            if self._eof_received:
                raise _StreamEndedException(rv)
            else:
                self._buffer_ready.clear()
        return rv, count


class H2Protocol(asyncio.Protocol):
    def __init__(self, client_side: bool, *, loop=None, concurrency=1024):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._conn = H2Connection(client_side=client_side)
        self._transport = None
        self._streams = {}
        self._inbound_requests = asyncio.Queue(concurrency, loop=loop)

        # Locks

        self._resumed = asyncio.Event(loop=loop)
        self._stream_creatable = CallableEvent(self._is_stream_creatable,
                                               loop=loop)

        # Dispatch table

        self._event_handlers = {
            events.RequestReceived: self._request_received,
            events.ResponseReceived: self._response_received,
            events.TrailersReceived: self._trailers_received,
            events.DataReceived: self._data_received,
            events.WindowUpdated: self._window_updated,
            events.RemoteSettingsChanged: self._remote_settings_changed,
            events.PingAcknowledged: self._ping_acknowledged,
            events.StreamEnded: self._stream_ended,
            events.StreamReset: self._stream_reset,
            events.PushedStreamReceived: self._pushed_stream_received,
            events.SettingsAcknowledged: self._settings_acknowledged,
            events.PriorityUpdated: self._priority_updated,
            events.ConnectionTerminated: self._connection_terminated,
        }

    # asyncio protocol

    def connection_made(self, transport):
        self._transport = transport
        self._conn.initiate_connection()
        self._conn.update_settings({
            settings.MAX_CONCURRENT_STREAMS: self._inbound_requests.maxsize})
        self._flush()
        self._stream_creatable.sync()
        self.resume_writing()

    def connection_lost(self, exc):
        self._conn = None
        self._transport = None
        self.pause_writing()

    def pause_writing(self):
        self._resumed.clear()

    def resume_writing(self):
        self._resumed.set()

    def data_received(self, data):
        events_ = self._conn.receive_data(data)
        self._flush()
        for event in events_:
            self._event_received(event)

    def eof_received(self):
        self._conn.close_connection()
        self._flush()

    # hyper-h2 event handlers

    def _event_received(self, event):
        self._event_handlers[type(event)](event)

    def _request_received(self, event: events.RequestReceived):
        self._inbound_requests.put_nowait((0, event.stream_id, event.headers))

    def _response_received(self, event: events.ResponseReceived):
        self._get_stream(event.stream_id).feed_response(event.headers)

    def _trailers_received(self, event: events.TrailersReceived):
        self._get_stream(event.stream_id).feed_trailers(event.headers)

    def _data_received(self, event: events.DataReceived):
        self._get_stream(event.stream_id).feed_data(event.data)
        if self._conn.inbound_flow_control_window < 1073741823:
            self._conn.increment_flow_control_window(
                2 ** 31 - 1 - self._conn.inbound_flow_control_window)
            self._flush()

    def _window_updated(self, event: events.WindowUpdated):
        if event.stream_id:
            self._get_stream(event.stream_id).window_open.sync()
        else:
            for stream in list(self._streams.values()):
                stream.window_open.sync()

    def _remote_settings_changed(self, event: events.RemoteSettingsChanged):
        if settings.INITIAL_WINDOW_SIZE in event.changed_settings:
            for stream in list(self._streams.values()):
                stream.window_open.sync()
        if settings.MAX_CONCURRENT_STREAMS in event.changed_settings:
            self._stream_creatable.sync()

    def _ping_acknowledged(self, event: events.PingAcknowledged):
        pass

    def _stream_ended(self, event: events.StreamEnded):
        self._get_stream(event.stream_id).feed_eof()
        self._stream_creatable.sync()

    def _stream_reset(self, event: events.StreamReset):
        self._get_stream(event.stream_id).window_open.set()
        self._stream_creatable.sync()

    def _pushed_stream_received(self, event: events.PushedStreamReceived):
        pass

    def _settings_acknowledged(self, event: events.SettingsAcknowledged):
        pass

    def _priority_updated(self, event: events.PriorityUpdated):
        pass

    def _connection_terminated(self, event: events.ConnectionTerminated):
        logger.warning('Remote peer sent GOAWAY [ERR: %s], disconnect now.',
                       event.error_code)
        self._transport.close()

    # Internals

    def _get_stream(self, stream_id):
        stream = self._streams.get(stream_id)
        if stream is None:
            stream = self._streams[stream_id] = H2Stream(
                stream_id, self._conn.local_flow_control_window,
                loop=self._loop)
        return stream

    def _flush(self):
        self._transport.write(self._conn.data_to_send())

    def _is_stream_creatable(self):
        return (self._conn.open_outbound_streams <
                self._conn.remote_settings.max_concurrent_streams)

    def _flow_control(self, stream_id):
        delta = (self._conn.local_settings.initial_window_size -
                 self._get_stream(stream_id).buffer_size -
                 self._conn.remote_flow_control_window(stream_id))
        if delta > 0:
            self._conn.increment_flow_control_window(delta, stream_id)
            self._flush()

    # APIs

    @asyncio.coroutine
    def start_request(self, headers, end_stream=False):
        yield from _wait_for_events(self._resumed, self._stream_creatable)
        stream_id = self._conn.get_next_available_stream_id()
        self._conn.send_headers(stream_id, headers, end_stream=end_stream)
        self._flush()
        return stream_id

    @asyncio.coroutine
    def send_data(self, stream_id, data, end_stream=False):
        try:
            with (yield from self._get_stream(stream_id).wlock):
                while True:
                    yield from _wait_for_events(
                        self._resumed, self._get_stream(stream_id).window_open)
                    data_size = len(data)
                    size = min(data_size,
                               self._conn.local_flow_control_window(stream_id),
                               self._conn.max_outbound_frame_size)
                    if data_size == 0 or size == data_size:
                        self._conn.send_data(stream_id, data,
                                             end_stream=end_stream)
                        self._flush()
                        data = b''
                        break
                    elif size > 0:
                        self._conn.send_data(stream_id, data[:size])
                        data = data[size:]
                        self._flush()
        except NoSuchStreamError:
            pass
        return data

    @asyncio.coroutine
    def send_headers(self, stream_id, headers, end_stream=False):
        yield from self._resumed.wait()
        self._conn.send_headers(stream_id, headers, end_stream=end_stream)
        self._flush()

    @asyncio.coroutine
    def end_stream(self, stream_id):
        with (yield from self._get_stream(stream_id).wlock):
            yield from self._resumed.wait()
            self._conn.end_stream(stream_id)
            self._flush()

    @asyncio.coroutine
    def recv_request(self):
        rv = yield from self._inbound_requests.get()
        return rv[1:]

    @asyncio.coroutine
    def recv_response(self, stream_id):
        return (yield from self._get_stream(stream_id).response)

    @asyncio.coroutine
    def recv_trailers(self, stream_id):
        return (yield from self._get_stream(stream_id).trailers)

    @asyncio.coroutine
    def read_stream(self, stream_id, size=None):
        rv = []
        try:
            with (yield from self._get_stream(stream_id).rlock):
                if size is None:
                    rv.append((
                        yield from self._get_stream(stream_id).read_frame()))
                    self._flow_control(stream_id)
                elif size < 0:
                    while True:
                        rv.extend((
                            yield from self._get_stream(stream_id).read_all()))
                        self._flow_control(stream_id)
                else:
                    while size > 0:
                        bufs, count = yield from self._get_stream(
                            stream_id).read(size)
                        rv.extend(bufs)
                        size -= count
                        self._flow_control(stream_id)
        except StreamClosedError:
            pass
        except _StreamEndedException as e:
            try:
                self._flow_control(stream_id)
            except StreamClosedError:
                pass
            rv.extend(e.bufs)
        return b''.join(rv)

    def update_settings(self, new_settings):
        self._conn.update_settings(new_settings)
        self._flush()
