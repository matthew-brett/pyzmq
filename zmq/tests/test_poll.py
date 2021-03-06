#
#    Copyright (c) 2010 Brian E. Granger
#
#    This file is part of pyzmq.
#
#    pyzmq is free software; you can redistribute it and/or modify it under
#    the terms of the Lesser GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    pyzmq is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    Lesser GNU General Public License for more details.
#
#    You should have received a copy of the Lesser GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

import time
from unittest import TestCase

import zmq
from zmq.tests import PollZMQTestCase

#-----------------------------------------------------------------------------
# Tests
#-----------------------------------------------------------------------------

class TestPoll(PollZMQTestCase):

    def test_p2p(self):
        s1, s2 = self.create_bound_pair(zmq.P2P, zmq.P2P)

        # Sleep to allow sockets to connect.
        time.sleep(1.0)

        poller = zmq.Poller()
        poller.register(s1, zmq.POLLIN|zmq.POLLOUT)
        poller.register(s2, zmq.POLLIN|zmq.POLLOUT)

        # Now make sure that both are send ready.
        socks = dict(poller.poll())
        self.assertEquals(socks[s1], zmq.POLLOUT)
        self.assertEquals(socks[s2], zmq.POLLOUT)

        # Now do a send on both, wait and test for zmq.POLLOUT|zmq.POLLIN
        s1.send('msg1')
        s2.send('msg2')
        time.sleep(1.0)
        socks = dict(poller.poll())
        self.assertEquals(socks[s1], zmq.POLLOUT|zmq.POLLIN)
        self.assertEquals(socks[s2], zmq.POLLOUT|zmq.POLLIN)

        # Make sure that both are in POLLOUT after recv.
        s1.recv()
        s2.recv()
        socks = dict(poller.poll())
        self.assertEquals(socks[s1], zmq.POLLOUT)
        self.assertEquals(socks[s2], zmq.POLLOUT)

        poller.unregister(s1)
        poller.unregister(s2)

        # Wait for everything to finish.
        time.sleep(1.0)

    def test_reqrep(self):
        s1, s2 = self.create_bound_pair(zmq.REP, zmq.REQ)

        # Sleep to allow sockets to connect.
        time.sleep(1.0)

        poller = zmq.Poller()
        poller.register(s1, zmq.POLLIN|zmq.POLLOUT)
        poller.register(s2, zmq.POLLIN|zmq.POLLOUT)

        # Make sure that s1 is in state 0 and s2 is in POLLOUT
        socks = dict(poller.poll())
        self.assertEquals(socks.has_key(s1), 0)
        self.assertEquals(socks[s2], zmq.POLLOUT)

        # Make sure that s2 goes immediately into state 0 after send.
        s2.send('msg1')
        socks = dict(poller.poll())
        self.assertEquals(socks.has_key(s2), 0)

        # Make sure that s1 goes into POLLIN state after a time.sleep().
        time.sleep(0.5)
        socks = dict(poller.poll())
        self.assertEquals(socks[s1], zmq.POLLIN)

        # Make sure that s1 goes into POLLOUT after recv.
        s1.recv()
        socks = dict(poller.poll())
        self.assertEquals(socks[s1], zmq.POLLOUT)

        # Make sure s1 goes into state 0 after send.
        s1.send('msg2')
        socks = dict(poller.poll())
        self.assertEquals(socks.has_key(s1), 0)

        # Wait and then see that s2 is in POLLIN.
        time.sleep(0.5)
        socks = dict(poller.poll())
        self.assertEquals(socks[s2], zmq.POLLIN)

        # Make sure that s2 is in POLLOUT after recv.
        s2.recv()
        socks = dict(poller.poll())
        self.assertEquals(socks[s2], zmq.POLLOUT)

        poller.unregister(s1)
        poller.unregister(s2)

        # Wait for everything to finish.
        time.sleep(1.0)

    def test_pubsub(self):
        s1, s2 = self.create_bound_pair(zmq.PUB, zmq.SUB)
        s2.setsockopt(zmq.SUBSCRIBE, '')

        # Sleep to allow sockets to connect.
        time.sleep(1.0)

        poller = zmq.Poller()
        poller.register(s1, zmq.POLLIN|zmq.POLLOUT)
        poller.register(s2, zmq.POLLIN|zmq.POLLOUT)

        # Now make sure that both are send ready.
        socks = dict(poller.poll())
        self.assertEquals(socks[s1], zmq.POLLOUT)
        self.assertEquals(socks.has_key(s2), 0)

        # Make sure that s1 stays in POLLOUT after a send.
        s1.send('msg1')
        socks = dict(poller.poll())
        self.assertEquals(socks[s1], zmq.POLLOUT)

        # Make sure that s2 is POLLIN after waiting.
        time.sleep(1.0)
        socks = dict(poller.poll())
        self.assertEquals(socks[s2], zmq.POLLIN)

        # Make sure that s2 goes into 0 after recv.
        s2.recv()
        socks = dict(poller.poll())
        self.assertEquals(socks.has_key(s2), 0)

        poller.unregister(s1)
        poller.unregister(s2)

        # Wait for everything to finish.
        time.sleep(1.0)
