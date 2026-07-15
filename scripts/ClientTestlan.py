from lan_comm import *
import time
def on_message(client,data):
    print(f"Received {data.decode()}")

print(get_local_ip())
Tcpc = TcpClient("192.168.31.201")
if Tcpc.connect():
    Tcpc.on_message = on_message
    while True:
        message = input("Enter message:")
        if message.lower() == "exit":
            break
        Tcpc.send(message.encode())

    