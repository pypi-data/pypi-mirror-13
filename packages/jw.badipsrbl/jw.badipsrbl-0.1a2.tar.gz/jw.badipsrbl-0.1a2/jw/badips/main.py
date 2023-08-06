#!/usr/bin/env python
#
"""
Main program
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
from _socket import SOCK_DGRAM
from datetime import timedelta
from json import loads
import logging
import sys

from dnslib import DNSRecord, RR, QTYPE, A
from gevent.pool import Pool
from gevent.socket import socket
from pkg_resources import get_distribution
from urllib.request import urlopen
import time

__version__ = get_distribution('jw.badipsrbl').version
__author__ = "Johnny Wezel"

LOG_DEBUG2 = 9
LOG_DEBUG3 = 8

logging.addLevelName(LOG_DEBUG2, 'DEBUG2')
logging.addLevelName(LOG_DEBUG3, 'DEBUG3')
Logger = logging.getLogger(__name__)

VERSION = ("""
badipsrbl version {}
Copyright (c) 2015 {}
License: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software. You are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
""".strip().format(__version__, __author__)
)
LOG_LEVELS = (
    sorted(l for l in logging._levelNames if isinstance(l, int)) if sys.version_info[:2] < (3, 4)
    else sorted(logging._levelToName.keys())
)
INITIAL_LOG_LEVEL = logging.WARNING

PERIOD = 3600 * 24 * 30 * 6  # 6 months

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
            argp = ArgumentParser()
            argp.add_argument('arg', nargs='*')
            argp.add_argument('--port', '-p', nargs=1, action='store', default=53, help='specify port (default: 53)')
            argp.add_argument('--version', '-v', nargs=0, action=Version, help='display version and exit')
            self.args = argp.parse_args()
            self.pool = Pool()
            self.port = self.args.port
            self.socket = socket(type=SOCK_DGRAM)

        def run(self):
            """
            Run program
            """
            self.socket.bind(('', self.port))
            while True:
                request, address = self.socket.recvfrom(4096)
                dnsRequest = DNSRecord.parse(request)
                name = dnsRequest.get_q().get_qname().idna()
                print('query {} from {}'.format(name, address))
                sname = name.split('.')[3::-1]
                reply = dnsRequest.reply()
                for _ in ['once']:
                    if len(sname) != 4:
                        break
                    qname = '.'.join(sname)
                    data = loads(urlopen('https://www.badips.com/get/info/%s' % qname).read())
                    print(data)
                    if not data['Listed']:
                        print('Not listed')
                        break
                    reportCount = data['ReporterCount']['sum']
                    reportTime = max(data['LastReport'].values())
                    print('count:', reportCount, ', time:', reportTime)
                    if reportTime - time.time() > PERIOD:
                        print('Reported more than {} ago'.format(timedelta(0, PERIOD)))
                        break
                    if reportCount < 4 and (reportTime - time.time()) > reportCount * 3600 * 24 * 7:
                        print('Reported {0} times and reported more than {0} weeks ago'.format(reportCount))
                        break
                    reply.add_answer(RR(name, QTYPE.A, rdata=A('127.0.0.1'), ttl=60))
                print('reply:', reply)
                self.socket.sendto(reply.pack(), address)

    program = Program()
    sys.exit(program.run())

if __name__ == '__main__':
    Main()
