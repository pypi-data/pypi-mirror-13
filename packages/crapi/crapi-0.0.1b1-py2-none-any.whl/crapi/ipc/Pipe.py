# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Part of the ipc module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
# Python native libraries.
from abc import ABCMeta
from enum import Enum
import random
# Python 3rd party libraries.
import win32api as w32api
import win32pipe as w32p
import win32file as w32f
import win32event as w32ev
import pywintypes as WinT
import winerror as werr

from crapi.ipc.PipeError import PipeError
from crapi.ipc.PipeTimeoutError import PipeTimeoutError


class Pipe(object):

    __metaclass__ = ABCMeta

    class Type(Enum):
        ANONYMOUS = 'anonymous'
        NAMED = 'named'
        TRANSACTIONAL = 'transactional'

    class Mode(Enum):

        DUPLEX = 'duplex'
        READ_ONLY = 'read_only'
        WRITE_ONLY = 'write_only'

    class Channel(Enum):

        BYTE = 'byte'
        MESSAGE = 'message'

    class Transport(Enum):

        SYNCHRONOUS = 'synchronous'
        ASYNCHRONOUS = 'asynchronous'
        TRANSACTIONAL = 'transactional'

    class View(Enum):

        SERVER = 'server'
        CLIENT = 'client'

    # TODO: Check buffer ends by overflowing them!
    def __init__(self, name='', ptype=Type.NAMED, mode=Mode.DUPLEX,
                 channel=Channel.MESSAGE, transport=Transport.ASYNCHRONOUS,
                 view=View.SERVER, instances=0, buf_sz=[0, 0], sa=None):

        if name == '':
            self.name = 'pipe' + str(random.randint(9999, 9999999))
        else:
            self.name = name

        self.ptype = ptype
        if self.ptype == Pipe.Type.NAMED:
            pass
        else:
            raise NotImplementedError('Sorry! This pipe type is a WIP!')

        self.mode = mode
        if self.mode == Pipe.Mode.DUPLEX:
            self.__mode = w32p.PIPE_ACCESS_DUPLEX
        else:
            raise NotImplementedError('Sorry! This pipe modes is a WIP!')

        self.channel = channel
        if self.channel == Pipe.Channel.MESSAGE:
            self.__channel = w32p.PIPE_TYPE_MESSAGE
            # This will enable the ERROR_MORE_DATA exception although we
            # could handle the case of having more data in the buffer
            # without it.
            self.__channel |= w32p.PIPE_READMODE_MESSAGE
        else:
            raise NotImplementedError('Sorry! This channel mode is a WIP!')

        self.transport = transport
        if self.transport == Pipe.Transport.TRANSACTIONAL:
            raise NotImplementedError('Sorry! This transport mode is a WIP!')
        self.view = view
        # Using PIPE_NOWAIT in overlapped mode is deprecated and will cause
        # an ERROR_PIPE_LISTENING exception when using ConnectNamedPipe.
        # To avoid inefficient polling, which is CPU-stressing we make use of
        # events (aka signals!).
        # NOTE: If FILE_FLAG_OVERLAPPED is specified with PIPE_WAIT then
        #       ConnectNamedPipe will not raise an ERROR_PIPE_LISTENING
        #       exception however any read/write operation in the pipe stream
        #       will cause that.
        if self.view == Pipe.View.SERVER:
            if self.transport == Pipe.Transport.ASYNCHRONOUS:
                self.__open_mode = self.__mode | w32f.FILE_FLAG_OVERLAPPED
            else:
                self.__open_mode = self.__mode
            self.__open_mode2 = 0
            self.__pipe_mode = self.__channel | w32p.PIPE_WAIT
        else:
            self.__open_mode = w32f.OPEN_EXISTING
            self.__open_mode2 = w32f.FILE_FLAG_OVERLAPPED
            if self.__mode == w32p.PIPE_ACCESS_DUPLEX:
                self.__pipe_mode = w32f.GENERIC_READ | w32f.GENERIC_WRITE

        if instances < 0:
            raise ValueError(
                'Invalid # of instances: Only positive numbers are allowed!'
            )
        elif instances == 0:
            self.__instances = w32p.PIPE_UNLIMITED_INSTANCES
            self.instances = float('inf')
        else:
            self.__instances = instances
            self.instances = instances
        for sz in buf_sz:
            if sz < 0:
                raise ValueError(
                    'Buffer size cannot be negative!'
                )

        if self.ptype == Pipe.Type.NAMED:
            if self.view == Pipe.View.SERVER:
                self.__hPipe = w32p.CreateNamedPipe(
                    '\\\\.\\pipe\\' + self.name,
                    self.__open_mode,
                    self.__pipe_mode,
                    self.__instances,
                    buf_sz[1],
                    buf_sz[0],
                    0,  # 50ms per MSDN documentation
                    sa
                )
            else:
                self.__hPipe = w32f.CreateFile(
                    '\\\\.\\pipe\\' + self.name,
                    self.__pipe_mode,
                    0,
                    None,
                    self.__open_mode,
                    self.__open_mode2,
                    None
                )

    # FIXME: Access with properties ;)
    def _getOverlappedStruct(self):
        # We should use a new overlapped object for each asynchronous
        # operation since the MSDN site states:
        # "A common mistake is to reuse an OVERLAPPED structure before the
        #  previous asynchronous operation has been completed. You should
        #  use a separate structure for each request. You should also create
        #  an event object for each thread that processes data. If you store
        #  the event handles in an array, you could easily wait for all events
        #  to be signaled using the WaitForMultipleObjects function."
        #
        # Source URL:
        #   https://msdn.microsoft.com/en-us/library/windows/desktop/ms684342(v=vs.85).aspx
        # Additional URLs:
        #   https://msdn.microsoft.com/en-us/library/windows/desktop/aa365683(v=vs.85).aspx
        # Also, it is suggested to initialize all offset fields to 0.
        stream = WinT.OVERLAPPED()
        # Named pipes and communications devices don't use this but in order to
        # follow a uniform strategy we manually update this value in such
        # situations.
        # Source URL:
        #   docs.activestate.com/activepython/3.4/pywin32/PyOVERLAPPED.html
        stream.Offset = 0
        stream.OffsetHigh = 0
        stream.hEvent = w32ev.CreateEvent(None, False, False, None)

        return stream

    def __waitForEvent(self, stream, evTimeout):
        # Asynchronous I/O operations may complete in the
        # blink of an eye giving the false impression that
        # it completed as a synchronous I/O. As such, we
        # have to wait for the event to be signaled by the
        # read operation.
        # This is also required if GetOverlappedResult does
        # not wait for data to become available (bWait is
        # set to False) otherwise it will complain that the
        # event handler is in a non-signaled state.
        evCode = w32ev.WaitForSingleObject(
            stream.hEvent, evTimeout
        )
        if evCode == w32ev.WAIT_TIMEOUT:
            raise PipeTimeoutError(
                    'Connection timeout while awaiting pipe activity!',
                    'timeout',
                    evTimeout,
                    'event',
                    evCode
            )
        elif evCode != w32ev.WAIT_OBJECT_0:
            raise PipeError(
                'Unexpected pipe signal code event!',
                'event',
                evCode
            )

    def __expandBufferPipe(self, buf_sz):
        buf_sz = buf_sz*2
        return w32f.AllocateReadBuffer(buf_sz)

    def connect(self, timeout=0, buf_sz=0):
        if self.transport == Pipe.Transport.ASYNCHRONOUS:
            if int(timeout) == 0:
                evTimeout = w32ev.INFINITE
            else:
                evTimeout = int(timeout)
            stream = self._getOverlappedStruct()
            # Asynchronous named pipes return immediately!
            status_code = w32p.ConnectNamedPipe(
                self.__hPipe, stream
            )
            # From the MSDN docs:
            #   https://msdn.microsoft.com/en-us/library/windows/desktop/aa365146(v=vs.85).aspx
            # If a client connects before the function is called, the function
            # returns zero and GetLastError returns ERROR_PIPE_CONNECTED.
            if status_code == werr.ERROR_PIPE_CONNECTED:
                w32ev.SetEvent(stream.hEvent)
            elif status_code != werr.ERROR_IO_PENDING:
                raise PipeError(
                    'Failed to create unsynchronous named pipe connection!',
                    'status_code',
                    status_code
                )
            else:
                self.__waitForEvent(stream, evTimeout)
        else:
            status_code = w32p.ConnectNamedPipe(self.__hPipe, None)
            if status_code != 0:
                raise PipeError(
                    'Failed to create synchronous named pipe connection!',
                    'status_code',
                    status_code
                )
        return 0

    # Some notes about the read operation when in server view mode:
    # Status Code, GetLastError() - some possible scenarios are listed:
    # 0, 0 from start to finish. May cause ERROR_BROKEN_PIPE.
    # 997, 997 in start and finish of I/O operation.
    # 234, 234 after the first I/O; buffer is too small and while growing
    # it we reach a 0, 234 with a possibility of ERROR_BROKEN_PIPE
    # (recoverable).
    # Unlike the MS ReadWrite/WriteFile variants, these one return 0,
    # ERROR_IO_PENDING or ERROR_MORE_DATA making use of the GetLastError()
    # quite unnecessary.
    # TODO: ERROR_MORE_DATA in synchronous I/O only?
    def read(self, timeout=0, buf_sz=0):
        if self.transport == Pipe.Transport.ASYNCHRONOUS:
            if int(timeout) == 0:
                evTimeout = 50  # 50ms is the default value per MSDN docs.
            else:
                evTimeout = int(timeout)
            stream = self._getOverlappedStruct()
            if buf_sz <= 0:
                buf_sz = 2048
            ov_buf = w32f.AllocateReadBuffer(buf_sz)
            pipe_data = ''
            while True:
                try:
                    pipe_status, pipe_buffer = w32f.ReadFile(
                        self.__hPipe, ov_buf, stream
                    )
                except WinT.error, e:
                    if e.args[0] == werr.ERROR_BROKEN_PIPE:
                        return 1, stream.Offset, pipe_data
                    else:
                        raise
                if pipe_status == 0 or \
                   pipe_status == werr.ERROR_IO_PENDING:
                    if pipe_status == werr.ERROR_IO_PENDING:
                        self.__waitForEvent(stream, evTimeout)
                    try:
                        read_bytes = w32f.GetOverlappedResult(
                            self.__hPipe, stream, False
                        )
                    except WinT.error, e:
                        if e.args[0] == werr.ERROR_MORE_DATA:
                            ov_buf = self.__expandBufferPipe(buf_sz)
                            stream.Offset += len(pipe_buffer)
                            pipe_data += pipe_buffer
                            continue
                        elif e.args[0] == werr.ERROR_BROKEN_PIPE:
                            return 1, stream.Offset, pipe_data
                        else:
                            raise
                elif pipe_status == werr.ERROR_MORE_DATA:
                    ov_buf = self.__expandBufferPipe(buf_sz)
                    stream.Offset += len(pipe_buffer)
                    pipe_data += pipe_buffer
                    continue
                else:
                    raise PipeError(
                        'Pipe encountered a fatal error!',
                        'error_code',
                        w32api.GetLastError()
                    )
                stream.Offset += read_bytes
                pipe_data += pipe_buffer[:read_bytes]
                if read_bytes < len(pipe_buffer):
                    return 0, stream.Offset, pipe_data

        else:
            pipe_status, pipe_content = w32f.ReadFile(
                self.__hPipe, buf_sz, None
            )
            return 0, len(pipe_content), pipe_content

    # TODO: Investigate why pipes require double the size of the string
    #       since it uses a space between every character :@
    #       Also, attempt to send a zero-sized write! :P
    # TODO: Simulate an ERROR_IO_PENDING since the ActiveState docs state
    #       that this is a possiblity...
    def write(self, payload, timeout=0, buf_sz=0):
        if self.transport == Pipe.Transport.ASYNCHRONOUS:
            if int(timeout) == 0:
                evTimeout = 50  # 50ms is the default value per MSDN docs.
            else:
                evTimeout = int(timeout)
            stream = self._getOverlappedStruct()
            if buf_sz > 0:
                str_buf = buffer(payload, 0, payload[:buf_sz]*2)
            else:
                str_buf = buffer(payload, 0, 2048)
            # FIXME: ERROR_NO_DATA with Ctrl-C in server
            status_code, written_bytes = w32f.WriteFile(
                self.__hPipe, str_buf, stream
            )
            self.__waitForEvent(stream, evTimeout)
            return status_code, written_bytes
        else:
            return w32f.WriteFile(
                self.__hPipe, payload, None
            )

    def close(self):
        if self.view == Pipe.View.SERVER:
            w32f.FlushFileBuffers(self.__hPipe)
            w32p.DisconnectNamedPipe(self.__hPipe)
        else:
            self.__hPipe.Close()

    def shutdown(self):
        if self.view == Pipe.View.SERVER:
            self.__hPipe.Close()
