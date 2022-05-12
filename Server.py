import asyncio
import threading

from AssiNet import *
import socket
import pickle

SERVER = socket.gethostbyname(socket.gethostname())

ADDR = (SERVER, PORT)

connections: dict[str, list[socket.socket]] = {}

SUICIDE_TIMEOUT = 30

class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen()
        self.update()

    def update(self):

        while True:
            client, client_ip = self.server.accept()
            print(f"{client_ip} connected")
            name = recv(client).decode()

            match name:
                case "SEND":
                    t = threading.Thread(target=self.handle_sender, args=[client])
                    t.start()
                case "GET_USERS":
                    send(client, pickle.dumps(list(connections.keys())))
                case _:
                    if name in connections:
                        connections[name].append(client)
                    else:
                        connections[name] = [client]

    def handle_sender(self, client : socket.socket):

        def send_status(status):
            try:
                send(client, status.encode())
            except ConnectionError:
                pass

        header = pickle.loads(recv(client))



        sender_username, target_username, sizes = header

        if target_username not in connections or len(connections[target_username]) == 0:
            send_status("OFFLINE")
            return

        targets = connections[target_username]


        found = False
        for target in targets:
            try:
                send(target, b"PING")
                assert recv(target, SUICIDE_TIMEOUT) == b"PONG"
            except ConnectionError or AssertionError:
                connections[target_username].remove(target)
                continue

            send(target, pickle.dumps([sender_username, sizes]))
            found = True

        if not found:
            send_status("OFFLINE")
            return


        size_sum = 0
        total_size = sum([s[1] for s in sizes])
        while size_sum < total_size:
            packet = client.recv(4096)

            size_sum += len(packet)
            for target in targets:
                try:
                    target.send(packet)
                except ConnectionError:
                    send_status("DISCONNECT")
                    return


        send_status("OK")



    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.server.close()

with Server(): ...
