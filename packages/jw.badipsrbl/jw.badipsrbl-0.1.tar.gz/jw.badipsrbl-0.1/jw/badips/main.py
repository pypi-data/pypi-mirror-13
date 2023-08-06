#!/usr/bin/env python
#
"""
Main program
"""
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
from jw.util.python3hell import Bytes2Str

standard_library.install_aliases()
from builtins import object
from _socket import SOCK_DGRAM
from datetime import timedelta
from json import loads
import logging
import sys

from dnslib import DNSRecord, RR, QTYPE, A, SOA
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

RESERVED_IPS = (
    ((0, 0, 0, 0), (0, 255, 255, 255)),
    ((10, 0, 0, 0), (10, 255, 255, 255)),
    ((100, 64, 0, 0), (100, 127, 255, 255)),
    ((127, 0, 0, 0), (127, 255, 255, 255)),
    ((169, 254, 0, 0), (169, 254, 255, 255)),
    ((172, 16, 0, 0), (172, 31, 255, 255)),
    ((192, 0, 0, 0), (192, 0, 0, 255)),
    ((192, 0, 2, 0), (192, 0, 2, 255)),
    ((192, 88, 99, 0), (192, 88, 99, 255)),
    ((192, 168, 0, 0), (192, 168, 255, 255)),
    ((198, 18, 0, 0), (198, 19, 255, 255)),
    ((198, 51, 100, 0), (198, 51, 100, 255)),
    ((203, 0, 113, 0), (203, 0, 113, 255)),
    ((224, 0, 0, 0), (239, 255, 255, 255)),
    ((240, 0, 0, 0), (255, 255, 255, 254)),
)

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
            argp.add_argument(
                '--port', '-p',
                action='store',
                type=int,
                default=53,
                help='specify port (default: 53)'
            )
            argp.add_argument('--version', '-v', nargs=0, action=Version, help='display version and exit')
            self.args = argp.parse_args()
            self.pool = Pool()
            self.port = self.args.port
            self.socket = socket(type=SOCK_DGRAM)
            level = LOG_LEVELS[max(1, LOG_LEVELS.index(INITIAL_LOG_LEVEL) - self.args.debug)]
            logging.basicConfig(
                stream=sys.stderr,
                level=level,
                format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            Logger.debug('Arguments: %s', self.args)

        def run(self):
            """
            Run program
            """
            self.socket.bind(('', self.port))
            while True:
                request, address = self.socket.recvfrom(4096)
                dnsRequest = DNSRecord.parse(request)
                name = dnsRequest.get_q().get_qname().idna()
                Logger.info('Query %s from %s', name, address)
                sname = name.split('.')[3::-1]
                reply = dnsRequest.reply()
                for _ in ['once']:
                    if len(sname) != 4:
                        Logger.info('Invalid IP (not 4 elements)')
                        break
                    try:
                        ip = tuple(int(b) for b in sname)
                    except ValueError:
                        Logger.info('Invalid IP (non-integers')
                        break
                    if any(l <= ip <= u for l, u in RESERVED_IPS):
                        Logger.info('Reserved IP')
                        reply.add_answer(RR(name, QTYPE.A, rdata=A('127.0.0.2'), ttl=60))
                        break
                    qname = '.'.join(sname)
                    data = loads(Bytes2Str(urlopen('https://www.badips.com/get/info/%s' % qname).read()))
                    Logger.debug('From badips.com: %s', data)
                    if not data['Listed']:
                        Logger.info('Not listed')
                        break
                    reportCount = data['ReporterCount']['sum']
                    reportTime = max(data['LastReport'].values())
                    Logger.debug('count: %s, time: %s', reportCount, time.strftime('%F %T', time.localtime(reportTime)))
                    if reportTime - time.time() > PERIOD:
                        print('Reported more than %s ago', timedelta(0, PERIOD))
                        break
                    if reportCount < 4 and (reportTime - time.time()) < reportCount * 3600 * 24 * 7:
                        Logger.info(
                            'Reported %(count)d times and reported more than %(count)d weeks ago',
                            dict(count=reportCount)
                        )
                        break
                    reply.add_answer(RR(name, QTYPE.A, rdata=A('127.0.0.1'), ttl=60))
                reply.add_auth(
                    RR(
                        'rbl.wezel.info',
                        QTYPE.SOA,
                        ttl=60,
                        rdata=SOA(
                            'rbl.wezel.info',
                            'admin.wezel.info',
                            (int(time.time()), 60, 60, 60, 60)
                        )
                    )
                )
                Logger.debug('Reply sent: %s', reply)
                self.socket.sendto(reply.pack(), address)

    program = Program()
    sys.exit(program.run())

if __name__ == '__main__':
    Main()
