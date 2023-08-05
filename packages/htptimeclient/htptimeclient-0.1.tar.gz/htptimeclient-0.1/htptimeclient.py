#!/usr/bin/env python

"""Example htptime client.

   This Python script is an example of a htptime client. It should
   not be considered the reference htptime client as it is missing
   many useful features. There are no command line options and all
   settings are hard-coded. The list of htptime servers to query
   is also hard-coded. Users are highly encouraged to implement
   improved version of htptime clients.

   The script will run as a daemon process and write timestamps
   to ntpd's shared memory (http://doc.ntp.org/4.2.6/drivers/driver28.html).
   It relies on the 'requests', 'daemon' and 'ntpdshm' Python modules. All
   can be found on http://pypi.python.org. 

   This htptime client operates in conjunction with ntpd. The following
   two lines must be added to ntp.conf:

     server 127.127.28.2
     fudge  127.127.28.2 refid HTTP stratum 5


   MJ, 18-Jan-2016

"""


NAME = 'htptimeclient'
VERSION = '0.1'
LICENSE = 'BSD License'
AUTHOR = 'Markus Juenemann'
EMAIL = 'info@htptime.org'
DESCRIPTION = 'Example client of the www.htptime.org project'
URL = 'https://github.com/mjuenema/htptime'


import time
import sys
import urlparse
import socket
import requests
import ntpdshm
import syslog
import daemon

TIMEOUT = 3.0	
POLL = 45

MAX_SERVERS = 10
"""Maximum number of servers to query."""

DEFAULT_URLS = ['http://%d.pool.htptime.org' % (i) for i in range(0, MAX_SERVERS)]
"""Default list of htptime servers/urls."""

WORST_OFFSET = float(sys.maxint)
WORST_DURATION = float(sys.maxint)

def normalise_url(server):
    e = urlparse.urlsplit(server)

    # Fix problem described here: http://stackoverflow.com/questions/3798269/combining-a-url-with-urlunparse
    #
    if not e.netloc:
        netloc, path = e.path, ''
    else:
        netloc, path = e.netloc, e.path

    if not e[0]:
        return urlparse.urlunsplit(('http', netloc, path, e.query, e.fragment))
    else:
        return urlparse.urlunsplit((e.scheme, netloc, path, e.query, e.fragment))


def sort_by_offset(htp_server1, htp_server2):
    if abs(htp_server1.offset) < abs(htp_server2.offset):
        return -1
    elif abs(htp_server1.offset) > abs(htp_server2.offset):
        return 1
    else:
        return 0


def sort_by_duration(htp_server1, htp_server2):
    if htp_server1.duration < htp_server2.duration:
        return -1
    elif htp_server1.duration > htp_server2.duration:
        return 1
    else:
        return 0


class HtpServer(object):
    def __init__(self, server):

        self.url = normalise_url(server)
        self.offset = float(sys.maxint)
        self.duration = float(sys.maxint)

    def __repr__(self):
        return 'HtpServer(url=%s, offset=%.6f, duration=%.6f)' % (
               self.url, self.offset, self.duration)

    def query(self):

        # Set all timestamps to None so we can determine inside the
        # exception handling how far we got with the request.
        #
        time_local1 = None
        time_local2 = None
        time_remote = None
        time_local = None

        try:
            with requests.Session() as session:

                # Set all timestamps to None so we can determine inside the
                # exception handling how far we got with the request.
                time_local1 = None
                time_local2 = None
                time_remote = None
                time_local = None

                session.head(self.url, timeout=TIMEOUT)

                time_local1 = time.time()
                response = session.get(self.url, timeout=TIMEOUT)
                time_local2 = time.time()

                response.raise_for_status()

                time_remote = response.json()['time']
                time_local = (time_local2+time_local1)/2.0

        # Catch any exception to ensure script does not abort.
        #
        except Exception as exc:
            syslog.syslog('%s - %s' % (type(exc), str(exc)))


        # Update self.offset and self.duration if possible.
        #
        if time_remote and time_local:
            self.offset = time_remote-time_local
        else:
            self.offset = WORST_OFFSET

        if time_local1 and time_local2:
            self.duration = time_local2 - time_local1
        else:
            self.duration = WORST_DURATION


def main():

    # Generate list of servers
    #
    htp_servers = [HtpServer(url) for url in DEFAULT_URLS][:MAX_SERVERS]

    ntpd_shm = ntpdshm.NtpdShm(2)
    ntpd_shm.mode = 0            
    ntpd_shm.precision = -3      
    ntpd_shm.leap = 0 

    with daemon.DaemonContext():

        while True:

            for server in htp_servers: 
                server.query()
            htp_servers.sort(sort_by_duration)

            time_local = time.time()
            time_remote = time_local + htp_servers[0].offset

            try:
                ntpd_shm.update(time_remote, time_local)
            except TypeError,e :
                syslog.syslog("TypeError: %s %f %f" % (e, time_remote, time_local))

            time.sleep(POLL)

if __name__ == '__main__':
    main()

