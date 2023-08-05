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


import inspect

from . import _request, error


def worker(f):
    '''
    Decorator for worker functions.

    The first argument of a function decorated by @worker ('self', when decorating a method) must be either
    a. A Client.
    b. A WorkerGroup.
    c. An object with a WorkerGroup attribute named 'ampd_worker_group'.

    A worker function returns a Worker.
    '''

    argspec = inspect.getargspec(f)
    g = eval('lambda {0}: Worker(f({0}), {1}.ampd_worker_group)'.format(inspect.formatargspec(*argspec[:3])[1:-1], argspec.args[0]), {'Worker': Worker, 'f': f})
    g.__defaults__ = f.__defaults__
    g.__name__ = f.__name__
    g.__doc__ = f.__doc__
    return g


class Worker(object):
    '''
    AMPD worker.

    Created by a worker function, namely, a python generator decorated by @worker:

       @worker
       def worker_example(arg1, ...):
           ...
           reply = yield request1(a, b)
           ...
           reply = yield request2()
           ...

    The first argument for the worker function (self, if a method) must be one of:

    a. A Client.
    b. A WorkerGroup.
    c. An object with a WorkerGroup attribute named 'ampd_worker_group'.

    The function returns a new Worker immediately.
    Its code is later executed by the main loop.
    A statement of the form:

        reply = yield request

    suspends execution until something happens and a reply is available.
    The request can be:

    a. An MPD command (other than 'idle' and 'noidle').
       Returns when the server's reply arrives:

           yield play(5)
           reply = yield status()

    b. A passive request, emulating MPD's 'idle' command, with some improvements.
       Returns as soon as one of the conditions is satisfied, with a list of the satisfied conditions:

           reply = yield condition, ... | iterable

       Conditions can be:

       - A SUBSYSTEM name (in uppercase) or ANY to match any subsystem.
       - TIMEOUT(ms) - satisfied after 'ms' milliseconds.
       - CONNECT - client is connected to server.
       - IDLE - client is idle.
       - WORKER(worker, ... | iterable) - all workers are done.

    c. Special request:

           yield _self()

       Returns the executing Worker.

    d. A request list.
       Emulates MPD's command list, returns a list of replies:

           yield request, ... | iterable

    For MPD commands and subsystems see http://www.musicpd.org/doc/protocol/command_reference.html
    '''

    def __init__(self, gen, group):
        self._gen = gen
        self.name = gen.gi_code.co_name
        self._group = group
        self._atexit = []
        if group.workers == None:
            raise RuntimeError('Attempting to start a Worker in a closed WorkerGroup')
        group.workers.append(self)
        group.client._execute(self)

    def _close(self, close_generator=True):
        if self._gen:
            if close_generator:
                self._gen.close()
            self._group.workers.remove(self)
            for f in self._atexit:
                f()
            self._gen = self._group = self._atexit = None
            self.name += ' (closed)'

    def kill(self):
        '''
        Stop execution.
        '''
        if self._group:
            self._group.client._kill_worker(self)

    def add_atexit(self, f):
        '''
        Add a cleanup function to be called when the Worker exits.
        '''
        self._atexit.append(f)

    def __repr__(self):
        return self.name


class WorkerGroup(object):
    def __init__(self, client):
        self.client = client
        self.workers = []
        client._worker_groups.append(self)

    def close(self):
        if not self.client:
            return
        self.client._worker_groups.remove(self)
        while self.workers:
            self.client._kill_worker(self.workers[0])
        self.client = None

    @property
    def ampd_worker_group(self):
        return self

    @worker
    def connect_loop(self, connect_cb=None, disconnect_cb=None, connect_failed_cb=None):
        '''
        Convenience function for hooking into connect and disconnect events.
        Calls connect_cb() upon connect, disconnect_cb() upon disconnect, and connect_failed_cb() upon failed connect.
        '''
        while True:
            try:
                yield _request.ConditionConnect
            except error.ConnectionError:
                connect_failed_cb and connect_failed_cb()
                continue
            connect_cb and connect_cb()
            try:
                yield _request.RequestPassive()
            except error.ConnectionError:
                disconnect_cb and disconnect_cb()

    def get_is_connected(self):
        return self.client.is_connected

    def get_protocol_version(self):
        return self.client.protocol_version
