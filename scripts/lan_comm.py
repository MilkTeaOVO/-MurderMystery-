"""局域网通信模块。
提供简单的 TCP/UDP 通信客户端与服务器。
"""

import socket
import threading
import time
from typing import Callable, Optional


def get_local_ip() -> str:
    """获取本机局域网 IP 地址。"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except OSError:
            return '127.0.0.1'


class TcpServer:
    """简单 TCP 服务器。"""

    def __init__(self, host: str = '0.0.0.0', port: int = 5000, backlog: int = 5):
        self.host = host
        self.port = port
        self.backlog = backlog
        self._socket: Optional[socket.socket] = None
        self._clients: list[socket.socket] = []
        self._running = False
        self.on_message: Optional[Callable[[socket.socket, bytes], None]] = None
        self.on_client_connect: Optional[Callable[[socket.socket, tuple], None]] = None
        self.on_client_disconnect: Optional[Callable[[socket.socket], None]] = None

    def start(self) -> None:
        if self._running:
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._socket.listen(self.backlog)
        self._running = True

        threading.Thread(target=self._accept_loop, daemon=True).start()

    def stop(self) -> None:
        self._running = False
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
        for client in self._clients[:]:
            try:
                client.close()
            except OSError:
                pass
        self._clients.clear()

    def _accept_loop(self) -> None:
        assert self._socket is not None
        while self._running:
            try:
                client_sock, addr = self._socket.accept()
                self._clients.append(client_sock)
                if self.on_client_connect:
                    self.on_client_connect(client_sock, addr)
                threading.Thread(target=self._client_loop, args=(client_sock,), daemon=True).start()
            except OSError:
                break

    def _client_loop(self, client_sock: socket.socket) -> None:
        while self._running:
            try:
                data = client_sock.recv(4096)
                if not data:
                    break
                if self.on_message:
                    self.on_message(client_sock, data)
            except OSError:
                break
        if client_sock in self._clients:
            self._clients.remove(client_sock)
        if self.on_client_disconnect:
            self.on_client_disconnect(client_sock)
        try:
            client_sock.close()
        except OSError:
            pass

    def broadcast(self, message: bytes) -> None:
        for client in self._clients[:]:
            try:
                client.sendall(message)
            except OSError:
                pass


class TcpClient:
    """简单 TCP 客户端。"""

    def __init__(self, server_host: str, server_port: int = 5000):
        self.server_host = server_host
        self.server_port = server_port
        self._socket: Optional[socket.socket] = None
        self._running = False
        self.on_message: Optional[Callable[[bytes], None]] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None

    def connect(self, timeout: float = 5.0) -> bool:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)
        try:
            self._socket.connect((self.server_host, self.server_port))
            self._running = True
            self._socket.settimeout(None)
            if self.on_connected:
                self.on_connected()
            threading.Thread(target=self._receive_loop, daemon=True).start()
            return True
        except OSError:
            self._socket.close()
            self._socket = None
            return False

    def disconnect(self) -> None:
        self._running = False
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
        if self.on_disconnected:
            self.on_disconnected()

    def send(self, message: bytes) -> bool:
        if not self._socket:
            return False
        try:
            self._socket.sendall(message)
            return True
        except OSError:
            return False

    def _receive_loop(self) -> None:
        assert self._socket is not None
        while self._running:
            try:
                data = self._socket.recv(4096)
                if not data:
                    break
                if self.on_message:
                    self.on_message(data)
            except OSError:
                break
        self.disconnect()


class UdpDiscoveryServer:
    """UDP 广播发现服务。"""

    def __init__(self, port: int = 5001, response_message: str = 'LAN_SERVICE'):
        self.port = port
        self.response_message = response_message
        self._socket: Optional[socket.socket] = None
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('0.0.0.0', self.port))
        self._running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop(self) -> None:
        self._running = False
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None

    def _listen_loop(self) -> None:
        assert self._socket is not None
        while self._running:
            try:
                data, addr = self._socket.recvfrom(4096)
            except OSError:
                break
            if not data:
                continue
            try:
                self._socket.sendto(self.response_message.encode('utf-8'), addr)
            except OSError:
                pass


class UdpDiscoveryClient:
    """UDP 广播发现客户端。"""

    def __init__(self, port: int = 5001, message: str = 'DISCOVER_LAN_SERVICE', timeout: float = 3.0):
        self.port = port
        self.message = message
        self.timeout = timeout

    def discover(self) -> list[tuple[str, int, str]]:
        results: list[tuple[str, int, str]] = []
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(self.timeout)
            s.sendto(self.message.encode('utf-8'), ('<broadcast>', self.port))
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    data, addr = s.recvfrom(4096)
                    results.append((addr[0], addr[1], data.decode('utf-8', errors='ignore')))
                except socket.timeout:
                    break
                except OSError:
                    break
        return results


def example_server() -> TcpServer:
    server = TcpServer(port=5000)

    def on_connect(sock: socket.socket, addr: tuple) -> None:
        print(f'客户端已连接: {addr}')

    def on_message(sock: socket.socket, data: bytes) -> None:
        print(f'收到消息: {data.decode("utf-8", errors="ignore")}')
        try:
            sock.sendall('已收到'.encode('utf-8'))
        except OSError:
            pass

    server.on_client_connect = on_connect
    server.on_message = on_message
    server.start()
    print(f'TCP 服务器已启动: {get_local_ip()}:{server.port}')
    return server


def example_client(server_host: str) -> TcpClient:
    client = TcpClient(server_host=server_host, server_port=5000)

    def on_connected() -> None:
        print('已连接到服务器')

    def on_message(data: bytes) -> None:
        print(f'收到服务器回应: {data.decode("utf-8", errors="ignore")}')

    client.on_connected = on_connected
    client.on_message = on_message
    if not client.connect():
        raise RuntimeError('无法连接服务器')
    return client


if __name__ == '__main__':
    server = example_server()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
