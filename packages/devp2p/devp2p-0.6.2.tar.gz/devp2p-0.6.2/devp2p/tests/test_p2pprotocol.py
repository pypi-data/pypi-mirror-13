from devp2p.p2p_protocol import P2PProtocol
from devp2p.service import WiredService
from devp2p.app import BaseApp
import pytest
# notify peer of successfulll handshake!
# so other protocols get registered
# so other protocols can do their handshake


class PeerMock(object):
    packets = []
    config = dict(p2p=dict(listen_port=3000),
                  node=dict(id='\x00' * 64), client_version_string='devp2p 0.1.1')
    capabilities = [('p2p', 2), ('eth', 57)]
    stopped = False
    hello_received = False

    def receive_hello(self, proto, version, client_version_string, capabilities,
                      listen_port, remote_pubkey):
        for name, version in capabilities:
            assert isinstance(name, str)
            assert isinstance(version, int)
        self.hello_received = True

    def send_packet(self, packet):
        print 'sending', packet
        self.packets.append(packet)

    def stop(self):
        self.stopped = True

    def report_error(self, reason):
        pass


@pytest.mark.xfail
def test_protocol():
    peer = PeerMock()
    proto = P2PProtocol(peer, WiredService(BaseApp()))

    # ping pong
    proto.send_ping()
    ping_packet = peer.packets.pop()
    proto._receive_ping(ping_packet)
    pong_packet = peer.packets.pop()
    proto._receive_pong(pong_packet)
    assert not peer.packets

    # hello (fails same nodeid)
    proto.send_hello()
    hello_packet = peer.packets.pop()
    proto._receive_hello(hello_packet)
    disconnect_packet = peer.packets.pop()  # same nodeid
    assert disconnect_packet.cmd_id == P2PProtocol.disconnect.cmd_id
    assert not peer.stopped  # FIXME: @heikoheiko this fails currently

    # hello (works)
    proto.send_hello()
    hello_packet = peer.packets.pop()
    peer.config['node']['id'] = '\x01' * 64  # change nodeid
    proto._receive_hello(hello_packet)
    assert not peer.packets
    assert not peer.stopped  # FIXME: @heikoheiko this fails currently
    assert peer.hello_received

    # disconnect
    proto.send_disconnect(reason=proto.disconnect.reason.disconnect_requested)
    disconnect_packet = peer.packets.pop()
    proto._receive_disconnect(disconnect_packet)
    assert not peer.packets
    assert peer.stopped


def test_callback():
    peer = PeerMock()
    proto = P2PProtocol(peer, WiredService(BaseApp()))

    # setup callback
    r = []

    def cb(_proto, **data):
        assert _proto == proto
        r.append(data)
    proto.receive_pong_callbacks.append(cb)

    # trigger
    proto.send_ping()
    ping_packet = peer.packets.pop()
    proto._receive_ping(ping_packet)
    pong_packet = peer.packets.pop()
    proto._receive_pong(pong_packet)
    assert not peer.packets
    assert len(r) == 1
    assert r[0] == dict()
