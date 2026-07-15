import time
from lan_comm import *
Tcps = TcpServer()
Tcps.start()

print(get_local_ip())

def on_message(client_sock: socket.socket, data: bytes) -> None:
    print(f"Received from {client_sock.getpeername()}: {data.decode()}")

Tcps.on_message = on_message
while True:
    message = input("Enter message to broadcast (or 'exit' to quit): ")
    if message.lower() == 'exit':
        break
    Tcps.broadcast(message.encode())
    print(Tcps._clients)