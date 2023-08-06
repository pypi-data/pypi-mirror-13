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
import time

from collections import deque
from functools import partial
from future import standard_library
from gevent import spawn, sleep, kill, joinall
from gevent.pool import Group, Pool
from gevent.queue import Queue
import yaml
from zope import component
from jw.ui.base import Ui
from jw.util.extension import ResourceNotFound, LoadClass

standard_library.install_aliases()

import logging
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
RECV_BUFFER_SIZE = 4096
DEFAULT_MINIMIZE_TIMEOUT = 10
TIMESTAT_SIZE = 5

_Logger = logging.getLogger(__name__)

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
            argp.add_argument(
                '--input', '-i',
                action='append',
                nargs='+',
                help='specify input'
            )
            argp.add_argument(
                '--config', '-c',
                action='store',
                type=open,
                required=True,
                help='specify configuration file'
            )
            argp.add_argument(
                '--ui', '-u',
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
                        modules[m] = __import__(m)
                self.conversionConfig = {
                    k: eval('lambda _: ' + v, modules) for k, v in config[1].get('convert', {}).items()
                }
            else:
                self.conversionConfig = {}
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
            self.loading = False
            self.readers = []
            self.queue = Queue()
            self.minimizeTimeOut = config[1].get('minimizeAfter', DEFAULT_MINIMIZE_TIMEOUT)
            self.withdraw = config[1].get('withdraw', False)
            #print(self.args);sys.exit(1)

        def run(self):
            """
            Run program
            """
            self.ui.setup(config=self.args.config)
            self.pool = Pool()
            self.pool.spawn(self.ui.run, partial(self.stop))
            for inp in self.args.input:
                try:
                    readerClass = LoadClass('jw.eventview.reader', inp[0])
                except ResourceNotFound:
                    print('No such input type: %s' % inp[0])
                else:
                    reader = readerClass(inp, self.queue, self.pool)
                    reader.run()
                    self.readers.append(reader)
            if not self.readers:
                raise RuntimeError('No input sources')
            self.pool.spawn(self.timeOutHandler)
            self.pool.spawn(self.server)
            self.pool.join()
            self.reporter.collectStatus()
            json.dump(self.uiStatus, open('/tmp/s', 'w'))  # HACK: do proper status saving
            print('App terminated')

        def stop(self):
            print('App terminating')
            self.pool.kill()

        def timeOutHandler(self):
            while True:
                for t in self.timeouts:
                    if t[0] > 0:
                        t[0] -= 1
                        if t[0] < 1:
                            t[1]()
                sleep(1)

        def endLoading(self):
            print('End loading')
            self.loading = False

        def server(self):
            """
            """

            self.timeouts.append([0, self.ui.withdrawAll if self.withdraw else self.ui.minimizeAll])
            minimizeTimeOut = len(self.timeouts) - 1
            self.timeouts.append([0, self.endLoading])
            loadingTimeOut = len(self.timeouts) - 1
            timeStat = deque(maxlen=TIMESTAT_SIZE)
            while True:
                timeStat.append(time.time())
                self.reporter.report(
                    Converted(self.conversionConfig, self.queue.get()),
                    status=self.uiStatus,
                    show=not self.loading
                )
                if not self.loading:
                    self.ui.update()
                self.timeouts[minimizeTimeOut][0] = self.minimizeTimeOut
                if len(timeStat) == TIMESTAT_SIZE and timeStat[-1] - timeStat[0] < 1:
                    self.timeouts[loadingTimeOut][0] = TIMESTAT_SIZE
                    self.loading = True
                    print('Loading', timeStat[-1], timeStat[0])

    program = Program()
    sys.exit(program.run())

if __name__ == '__main__':
    Main()
