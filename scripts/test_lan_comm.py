import os
import sys
import time
import threading
import unittest

# Ensure the scripts directory is importable
sys.path.insert(0, os.path.dirname(__file__))

from lan_comm import TcpServer, TcpClient


class TestTcpServerClient(unittest.TestCase):
    def test_echo(self):
        server = TcpServer(host='127.0.0.1', port=0)
        events = {}
        client_got = threading.Event()
        server_got = threading.Event()

        def on_message(sock, data):
            events['server_received'] = data
            try:
                sock.sendall(b'ACK:' + data)
            except OSError:
                pass
            server_got.set()

        server.on_message = on_message
        server.start()
        # allow server to bind
        time.sleep(0.1)
        actual_port = server._socket.getsockname()[1]

        client = TcpClient(server_host='127.0.0.1', server_port=actual_port)

        def on_connected():
            events['connected'] = True

        def on_msg(data):
            events['client_received'] = data
            client_got.set()

        client.on_connected = on_connected
        client.on_message = on_msg

        connected = client.connect(timeout=2.0)
        assert connected, 'Client failed to connect'

        sent = client.send(b'hello')
        assert sent, 'Client failed to send'

        # wait for server and client events
        client_got.wait(2.0)
        server_got.wait(2.0)

        assert 'server_received' in events
        assert 'client_received' in events
        assert events['server_received'] == b'hello'
        assert events['client_received'].startswith(b'ACK:')

        client.disconnect()
        server.stop()


if __name__ == '__main__':
    unittest.main()