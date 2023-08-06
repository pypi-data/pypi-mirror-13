"""
Reader implementations
"""
import os
from abc import ABCMeta, abstractmethod
import fcntl
from future.utils import with_metaclass
from gevent import spawn, sleep
from gevent.server import StreamServer, DatagramServer
from jw.util.python3hell import Bytes2Str, Open
import sys
from yaml import load
from zope import component
from eventview.parser import Parser


class Reader(with_metaclass(ABCMeta)):
    """
    Abstract base class for reader implementations
    """

    def __init__(self, format, queue):
        self.queue = queue
        self.parser = component.getUtility(Parser, format)

    @abstractmethod
    def run(self, group):
        """
        Run reader

        :param group: gevent group to spawn greenlets
        :type group: gevent.pool.Group

        Expected to read input and report it
        """

    def send(self, line):
        self.queue.put(self.parser.parsed(line))

class Tcp(Reader):
    """
    Reader for TCP stream
    """

    def __init__(self, initSpec, queue, pool):
        """
        Create Tcp object

        :param initSpec:
        :type initSpec: str
        :param queue: queue to write to
        :type queue: gevent.queue.Queue
        """
        assert len(initSpec) == 3, 'tcp input requires two argument: port, format'
        super(Tcp, self).__init__(initSpec[2], queue)
        self.port = int(initSpec[1])
        self.server = StreamServer(('', self.port), self.serve, spawn=pool)

    def run(self, group):
        """
        Run TCP reader
        """
        self.server.start()

    def serve(self, socket, address):
        """
        Socket server

        :param socket: socket
        :type socket: socket.socket
        :param address: unused
        :type address: str
        """
        ifile = socket.makefile(encoding='utf-8', errors='replace')
        while True:
            line = ifile.readline()
            if line:
                self.send(line)
            else:
                break
        print('Tcp.serve() terminated')

class Udp(Reader):
    """
    Reader for UDP stream
    """

    def __init__(self, initSpec, queue, pool):
        """
        Create Udp object

        :param initSpec:
        :type initSpec: str
        :param queue: queue to write to
        :type queue: gevent.queue.Queue
        """
        assert len(initSpec) == 3, 'udp input requires two arguments: port, format'
        super(Udp, self).__init__(initSpec[2], queue)
        self.port = int(initSpec[1])
        self.buffer = b''
        self.server = DatagramServer(('', self.port), self.serve, spawn=pool)

    def run(self):
        """
        Run TCP reader
        """
        self.server.start()

    def serve(self, data, address):
        """
        Socket server

        :type data: bytes
        :type address: str
        """
        p = 0
        while True:
            eol = data.find(b'\n', p)
            if eol < 0:
                self.buffer += data[p:]
                break
            else:
                self.send(Bytes2Str(self.buffer + data[p: eol]))
                self.buffer = b''
                p = eol + 1

def _Open(filename, *args, **kwargs):
    """
    Open file (wrapper for open())

    :param filename: filename
    :type filename: str
    :return: file
    """
    result = sys.stdin if filename == '-' else open(filename, *args, **kwargs)
    fcntl.fcntl(result, fcntl.F_SETFL, os.O_NONBLOCK)
    return result

class File(Reader):
    """
    Reader for file
    """

    def __init__(self, initSpec, queue, pool):
        """
        Create a File object
        """
        assert len(initSpec) == 3, 'File input needs two arguments: filename, format'
        super(File, self).__init__(initSpec[2], queue)
        self.pool = pool
        self.filename = initSpec[1]

    def run(self):
        """
        Run File reader
        """
        return self.pool.spawn(self.serve)

    def serve(self):
        """
        Feed input from file into queue
        """
        ifile = _Open(self.filename, mode='rU', encoding='utf-8', errors='replace')
        buffer = ''
        while True:
            line = ifile.readline()
            if line:
                if not line.endswith('\n'):
                    buffer += line
                else:
                    self.send(buffer + line)
                    buffer = ''
            else:
                sleep(.1)
