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


from gi.repository import GLib, Gio
import socket


class Poller(object):
    def __init__(self, host, port, handle_read, handle_write, handle_error):
        self.host = host
        self.port = port
        self.handle_read = handle_read
        self.handle_write = handle_write
        self.handle_error = handle_error

    def close(self):
        pass


class PollerGLib(Poller):
    def __init__(self, *args, **kwargs):
        super(PollerGLib, self).__init__(*args, **kwargs)
        self.tcp_connection = self.socket = self.fd = None
        self.write_tag = self.other_tag = None
        self.cancel_connect = Gio.Cancellable.new()
        Gio.SocketClient.new().connect_to_host_async(self.host, self.port, self.cancel_connect, self.async_ready_cb)

    def close(self):
        super(PollerGLib, self).close()
        if self.cancel_connect:
            self.cancel_connect.cancel()
            self.cancel_connect = None
        if self.write_tag != None:
            GLib.source_remove(self.write_tag)
        if self.other_tag != None:
            GLib.source_remove(self.other_tag)
        if self.tcp_connection:
            self.tcp_connection.close()
        self.tcp_connection = self.socket = self.fd = None
        self.write_tag = self.other_tag = None

    def async_ready_cb(self, socket_client, task):
        self.cancel_connect = None
        try:
            self.tcp_connection = socket_client.connect_to_host_finish(task)
        except GLib.Error as error:
            self.handle_error(error.message)
            return
        self.socket = self.tcp_connection.get_socket()
        self.socket.set_blocking(False)
        self.fd = self.socket.get_fd()
        self.sock = socket.fromfd(self.fd, 0, 0)
        self.other_tag = GLib.io_add_watch(self.fd, GLib.IO_IN | GLib.IO_ERR | GLib.IO_HUP, self.callback_other)

    def callback_write(self, fd, condition):
        if self.handle_write(self.sock):
            return True
        else:
            self.write_tag = None
            return False

    def callback_other(self, fd, condition):
        if not condition & (GLib.IO_HUP | GLib.IO_ERR):
            if self.handle_read(self.sock):
                return True
        self.handle_error()
        self.other_tag = None
        return False

    def start_writing(self):
        if self.write_tag == None:
            self.write_tag = GLib.io_add_watch(self.fd, GLib.IO_OUT, self.callback_write)


class Scheduler(object):
    @staticmethod
    def connect_and_poll(host, port, handle_read, handle_write, handle_error):
        raise NotImplementedError

    @staticmethod
    def add_timeout(timeout, callback, parameter):
        raise NotImplementedError

    @staticmethod
    def remove_timeout(handler):
        raise NotImplementedError


class GLibScheduler(Scheduler):
    connect_and_poll = staticmethod(PollerGLib)
    add_timeout = staticmethod(GLib.timeout_add)
    remove_timeout = staticmethod(GLib.source_remove)
