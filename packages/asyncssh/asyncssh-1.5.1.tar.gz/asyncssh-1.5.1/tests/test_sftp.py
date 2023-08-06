# Copyright (c) 2015-2016 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

"""Unit tests for AsyncSSH SFTP client and server"""

import asyncio
import asyncssh

from .util import asynctest, run, AsyncTestCase


class _TestSFTP(AsyncTestCase):
    """Unit tests for AsyncSSH SFTP client and server"""

    _server = None
    _server_addr = None
    _server_port = None

    # Pylint doesn't like mixed case method names, but this was chosen to
    # match the convention used in the unittest module.

    # pylint: disable=invalid-name

    @classmethod
    @asyncio.coroutine
    def asyncSetUpClass(cls):
        """Set up keys and an SSH server for the tests to use"""

        run('ssh-keygen -q -b 2048 -t rsa -N "" -f ckey')
        run('ssh-keygen -q -b 2048 -t rsa -N "" -f skey')

        cls._server = yield from asyncssh.listen(
            '', 0, server_host_keys=['skey'],
            authorized_client_keys='ckey.pub', sftp_factory=True)

        sock = cls._server.sockets[0]
        cls._server_addr, cls._server_port = sock.getsockname()[:2]

    @classmethod
    @asyncio.coroutine
    def asyncTearDownClass(cls):
        """Shut down server"""

        cls._server.close()

        # Give server a chance to clean up closing connections
        yield from asyncio.sleep(0.01)

    # pylint: enable=invalid-name

    @asyncio.coroutine
    def _start_sftp(self):
        """Open an SFTP client session"""

        conn = yield from asyncssh.connect(self._server_addr,
                                           self._server_port,
                                           known_hosts=None,
                                           client_keys=['ckey'])

        sftp = yield from conn.start_sftp_client()

        return conn, sftp

    @asynctest
    def test_sftp_connect(self):
        """Connect to SFTP server"""

        conn, sftp = yield from self._start_sftp()

        with conn:
            with sftp:
                pass

        yield from conn.wait_closed()
