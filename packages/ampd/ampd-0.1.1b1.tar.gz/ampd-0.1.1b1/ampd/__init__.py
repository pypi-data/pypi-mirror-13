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


'''
Asynchronous MPD client library

Uses the GLib main event loop and python generators for asynchronous communication with a Music Player Daemon server.

A Client connects to an MPD server.
MPD commands are executed by a Worker (or several), which is created by calling a worker function and is executed by the main loop.
A Worker can be started either directly within the Client, or, for more complex applications, within a WorkerGroup.
'''


import os
import logging


__version__ = '0.1.1b1'


_logger = logging.getLogger('ampd')
_logger.setLevel(os.environ.get('LOGLEVEL_AMPD', os.environ.get('LOGLEVEL', 'INFO')))
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(fmt='%(levelname)s: %(name)s: %(message)s (%(pathname)s %(lineno)d)'))
_logger.addHandler(_handler)


__all__ = []

from ._client import Client
from ._worker import worker, Worker, WorkerGroup
__all__ += ['Client', 'worker', 'Worker', 'WorkerGroup']

from ._request import commands as commands_, conditions
globals().update(commands_)
globals().update(conditions)

__all__ += ['commands_', 'conditions']
__all__ += commands_.keys()
__all__ += conditions.keys()
