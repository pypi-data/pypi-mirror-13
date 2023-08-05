# coding: utf-8

# Asynchronous Music Player Daemon client library for Python

# Copyright (C) 2015 Itaï BEN YAACOV

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys

from .error import *
from . import scheduler, _request, _worker, _logger


_DEFAULT_CODING = None if sys.version_info >= (3, 0) else 'utf-8'

class Client(object):
    '''
    AMPD client object

    Establishes connection with the MPD server.

    Keeps track of:
    - The worker groups.
    - The active queue: requests send to server and waiting for a reply.
    - The passive list: 'idle' commands waiting for some conditions to hold.
    - The execution queue: workers for which a reply has arrived.
    '''

    def __init__(self, scheduler_=scheduler.GLibScheduler, coding=_DEFAULT_CODING, coding_server='utf-8', excepthook=None):
        '''
        Initialize a client.

        excepthook - override sys.excepthook for exceptions raised in workers.
        '''
        self._scheduler = scheduler_
        self._coding = coding
        self._coding_server = coding_server
        self._excepthook = excepthook
        self._passive_list = []
        self._execute_queue = []
        self._execute_timeout = None
        self._worker_groups = []
        self._poller = None
        self.is_connected = False
        self.protocol_version = None
        self.ampd_worker_group = _worker.WorkerGroup(self)

    def close(self):
        '''
        Close all workers and worker groups, disconnect from server.
        '''
        while self._worker_groups:
            self._worker_groups[0].close()
        self.disconnect()
        if self._execute_timeout:
            self._scheduler.remove_timeout(self._execute_timeout)
            self._run_execute_queue()

    def connect(self, host=None, port=6600, password=None):
        '''
        Connect to server.

        host     - '[password@]hostname[:port]'.  Default to $MPD_HOST or 'localhost'.
        port     - Ignored if given in the 'host' argument.
        password - Ignored if given in the 'host' argument.
        '''

        if not host:
            host = os.environ.get('MPD_HOST', 'localhost')
        if ':' in host:
            host, port = host.split(':', 1)
        if '@' in host:
            password, host = host.split('@', 1)

        if self._poller:
            self.disconnect()

        self._buff_in = self._buff_out = b''
        self._is_idle = False
        self._active_queue = []
        self._connect_worker()
        self._poller = self._scheduler.connect_and_poll(host, port, self._handle_read, self._handle_write, self._handle_error)
        self.password = password

    def disconnect(self):
        '''
        Disconnect from server.
        '''
        if self._poller:
            try:
                self._poller.sock.send('close')
            except:
                pass
            self._poller.close()
            self._poller = None
            self.is_connected = False
            self.protocol_version = None
            requests = self._active_queue + self._passive_list
            del self._buff_in, self._buff_out, self._active_queue
        else:
            requests = self._passive_list

        # Move everything to the execute queue with ConnectionError() reply
        self._execute_queue = [(worker, ConnectionError()) for worker, reply in self._execute_queue]
        for request in requests:
            request._execute(ConnectionError())

    def connect_loop(self, connect_cb=None, disconnect_cb=None, connect_failed_cb=None):
        return self.ampd_worker_group.connect_loop(connect_cb, disconnect_cb, connect_failed_cb)

    connect_loop.__doc__ = _worker.WorkerGroup.connect_loop.__doc__

    def _execute(self, worker, reply=None):
        self._execute_queue.append((worker, reply))
        if not self._execute_timeout:
            self._execute_timeout = self._scheduler.add_timeout(0, self._run_execute_queue)

    def _run_execute_queue(self):
        while self._execute_queue:
            worker, reply = self._execute_queue.pop(0)
            if not worker._gen:
                continue
            try:
                try:
                    request = worker._gen.throw(reply) if isinstance(reply, Exception) else worker._gen.send(reply)
                except:
                    del reply # If we threw an exception and got it back, python3 creates a reference cycle with the traceback.
                    worker._close()
                    raise
            except (StopIteration, ConnectionError):
                continue
            except:
                (self._excepthook or sys.excepthook)(*sys.exc_info())
                continue
            try:
                request = _request.Request.new(request)
                request._setup(worker, self)
            except Exception as reply:
                self._execute(worker, reply)

        self._execute_timeout = None

        if self.is_connected and not self._is_idle and not self._active_queue:
            self._idle_worker()

    def _kill_worker(self, worker):
        worker._close()
        try:
            self._execute_queue.remove(worker)
        except:
            for request in self._passive_list:
                if request.worker == worker:
                    request._execute(None)
                    break

    def _handle_error(self, message=None):
        self.disconnect()

    def _handle_write(self, sock):
        n = sock.send(self._buff_out)
        _logger.debug('Write: {}'.format(self._buff_out[:n]))
        self._buff_out = self._buff_out[n:]
        return len(self._buff_out) > 0

    def _handle_read(self, sock):
        data = sock.recv(10000)
        _logger.debug('Read: {}'.format(data))
        if not data:
            return False
        lines = (self._buff_in + data).split(b'\n')
        for line in lines[:-1]:
            line = line.decode(self._coding_server)
            if self._coding:
                line = line.encode(self._coding)
            if self._active_queue:
                self._active_queue[0]._process_line(line)
            else:
                raise ProtocolError('Unexpected data: ', line)
        self._buff_in = lines[-1]
        return True

    @_worker.worker
    def _connect_worker(self):
        self.protocol_version = yield _request.RequestWelcome()
        self.is_connected = True
        if self.password:
            yield _request.commands['password'](self.password)
        for request in list(self._passive_list):
            request._test(['connect'])

    @_worker.worker
    def _idle_worker(self):
        for request in self._passive_list:
            if request._test(['idle']):
                return
        _logger.debug('Going idle')
        subsystems = yield _request.RequestCommandIdle()
        for request in list(self._passive_list):
            request._test(subsystems)
