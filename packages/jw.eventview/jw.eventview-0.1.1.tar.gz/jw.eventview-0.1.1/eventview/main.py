#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Real-time event viewer
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import next
import json

from functools import partial
from future import standard_library
from gevent import spawn, sleep
import yaml

from zope import component

from jw.ui.base import Ui
from .parser import Parser

standard_library.install_aliases()

import logging
from gevent.server import StreamServer
from pkg_resources import get_distribution, iter_entry_points
import sys

__version__ = get_distribution('jw.eventview').version
__author__ = "Johnny Wezel"
LOG_DEBUG2 = 9
LOG_DEBUG3 = 8

logging.addLevelName(LOG_DEBUG2, 'DEBUG2')
logging.addLevelName(LOG_DEBUG3, 'DEBUG3')
Logger = logging.getLogger(__name__)

VERSION = ("""
Version %s
Copyright (c) 2015 %s
License: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software. You are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
""" % (__version__, __author__)).strip()
LOG_LEVELS = (
    sorted(l for l in logging._levelNames if isinstance(l, int)) if sys.version_info[:2] < (3, 4)
    else sorted(logging._levelToName.keys())
)
INITIAL_LOG_LEVEL = logging.WARNING

_Logger = logging.getLogger(__name__)

def Parsed(line):
    """
    Parse a log line into a dict

    :param line: input line
    :type line: str
    :return: parsed line
    :rtype: dict
    """
    etype, _, event = line.partition(':')
    return component.getUtility(Parser, etype).parse(event)  # TODO: refactor into memoized function

def Converted(config, data):
    """
    Convert fields in input according to configuration
    """
    return {key: config.get(key, lambda _: _)(value) for key, value in data.items()}

class ReportLevel(object):
    """
    Report level
    """

    def __init__(self, ui, config, topic=None, parent=None, status=None):
        """
        Create a ReportLevel object

        Creates the report level hierarchy
        """
        self.ui = ui
        self.parent = parent
        self.controls = {}
        self.topic = topic
        self.config = config
        self.status = status if status is not None else {}
        self.levels = {
            n: ReportLevel(ui, l, n, self, self.status.setdefault(n, {}))
            for n, l in config.get('levels', {}).items()
        }

    def report(self, message, parentControl=None, status=None, show=False):
        try:
            controlClass = self.ui.widgetClass(self.config['display'])
        except KeyError:
            rcontrol = None
        else:
            if parentControl not in self.controls:
                control = controlClass(parentControl, topic=self.topic, status=self.status, **self.config)
                self.controls[parentControl] = control
            else:
                control = self.controls[parentControl]
            rcontrol = control.report(message, show=show)
            status = None
        topics = 0
        if len(self.levels) == 1:
            # If only one element on level, it can only be that one
            next(iter(self.levels.values())).report(message, rcontrol, status, show)
        else:
            # Find element on level matching any event topic
            for topic, level in self.levels.items():
                if topic in message:
                    topics += 1
                    level.report(message, rcontrol, status, show)
            # If no topics found, look for 'default' entries
            if not topics:
                for l in self.levels.values():
                    if l.config.get('default', False):
                        l.report(message, rcontrol, status, show)

    def collectStatus(self):
        for c in self.controls.values():
            c.collectStatus()
        for l in self.levels.values():
            l.collectStatus()

def Main():
    import sys
    from argparse import ArgumentParser, Action

    class Version(Action):
        def __call__(self, *args, **kwargs):
            print(VERSION)
            sys.exit(0)

    class Program(object):
        """
        Program
        """

        def __init__(self):
            argp = ArgumentParser(description="Real-time event viewer")
            argp.add_argument('--port', '-p', action='store', type=int, default=7777, help='specify port')
            argp.add_argument('--config', '-c', action='store', type=open, help='specify configuration file')
            argp.add_argument(
                '--ui', '-i',
                action='store',
                choices=('tk',),
                default='tk',
                help='specify user interface'
            )
            argp.add_argument(
                '--version', '-v',
                nargs=0,
                default=__version__,
                action=Version,
                help='display version and exit'
            )
            self.args = argp.parse_args()
            config = list(yaml.load_all(self.args.config))
            assert config, 'Empty configuration'
            self.reporterConfig = config[0]
            if len(config) > 1:
                modules = {}
                if 'import' in config[1]:
                    for m in config[1]['import']:
                        print('import', m)
                        modules[m] = __import__(m)
                self.conversionConfig = {
                    k: eval('lambda _: ' + v, modules) for k, v in config[1].get('convert', {}).items()
                }
            else:
                self.conversionConfig = {}
            assert self.conversionConfig
            uiEntryPoint = next(iter_entry_points('jw.eventview.ui', self.args.ui), None)
            if not uiEntryPoint:
                raise RuntimeError('No GUI found with name "%s"' % self.args.ui)
            ep = uiEntryPoint.load()
            assert ep, 'Could not load GUI "%s"' % self.args.ui
            self.ui = component.getUtility(Ui, 'tk')
            assert self.ui, 'GUI "%s" did not load' % self.args.ui
            try:
                self.uiStatus = json.load(open('/tmp/s'))  # HACK: do proper status loading
            except:
                self.uiStatus = {}
            self.reporter = ReportLevel(self.ui, self.reporterConfig, status=self.uiStatus)
            self.timeouts = []
            self.loading = True

        def run(self):
            """
            Run program
            """
            self.ui.setup(config=self.args.config)
            spawn(self.ui.run, partial(self.stop))
            self.server = StreamServer(('', self.args.port), self.serve, backlog=10)
            self.running = True
            spawn(self.timeOutHandler)
            self.server.serve_forever()
            self.reporter.collectStatus()
            json.dump(self.uiStatus, open('/tmp/s', 'w'))  # HACK: do proper status saving
            print('App terminated')

        def stop(self):
            print('App terminating')
            self.server.stop(10)
            self.running = False

        def timeOutHandler(self):
            while True:
                for t in self.timeouts:
                    if t[0] > 0:
                        t[0] -= 1
                        if t[0] < 1:
                            t[1]()
                sleep(1)

        def endLoading(self):
            print('Ending loading')
            self.loading = False

        def serve(self, socket, address):
            """
            Greenlet: Serve connection

            :param socket: connection
            :type socket: gevent.socket.socket
            :param address: connection address
            :type address: tuple
            """
            input = socket.makefile('r')
            ok = True
            self.timeouts.append([0, self.ui.minimizeAll])
            minimizeTimeOut = len(self.timeouts) - 1
            self.timeouts.append([0, self.endLoading])
            loadingTimeOut = len(self.timeouts) - 1
            while ok and self.running:
                line = input.readline()
                if line:
                    self.reporter.report(
                        Converted(self.conversionConfig, Parsed(line)),
                        status=self.uiStatus,
                        show=not self.loading
                    )
                    if not self.loading:
                        self.ui.update()
                    self.timeouts[minimizeTimeOut][0] = 20
                else:
                    ok = False
                self.timeouts[loadingTimeOut][0] = 5

    program = Program()
    sys.exit(program.run())

if __name__ == '__main__':
    Main()
