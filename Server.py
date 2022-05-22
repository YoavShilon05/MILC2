import threading
import time
from AssiNet import *
import socket
import pickle
import logging

SERVER = socket.gethostbyname(socket.gethostname())

ADDR = (SERVER, PORT)

connections: dict[str, list[socket.socket]] = {}
SUICIDE_TIMEOUT = 30

class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen()
        logging.info("Server is listening...")

    def update(self):

        while True:
            client, client_ip = self.server.accept()
            logging.info(f"{client_ip} connected")
            cmd = recv(client).decode()

            match cmd:
                case "SEND":
                    t = threading.Thread(target=self.handle_sender, args=[client])
                    t.start()
                case "GET_USERS":
                    users = list(connections.keys())
                    logging.info(f"users list requested, sending {users}")
                    send(client, pickle.dumps(users))
                case _:
                    name = cmd # client connected, username was sent
                    if name in connections:
                        logging.info(f"client {name} connected, appending to existing connection(s)")
                        connections[name].append(client)
                    else:
                        logging.info(f"client {name} connected, creating new connection")
                        connections[name] = [client]

    def handle_sender(self, client : socket.socket):

        def send_status(status):
            try:
                send(client, status.encode())
            except ConnectionError:
                pass

        header = pickle.loads(recv(client))

        sender_username, target_username, sizes = header
        logging.info(f"{sender_username} sent {target_username} {sizes} bytes of files")

        if target_username not in connections or len(connections[target_username]) == 0:
            logging.info(f"{target_username} was offline, send aborted")
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
            logging.info(f"{target_username} was offline, aborting")
            send_status("OFFLINE")
            return

        logging.info(f"{target_username} was online, starting to send...")

        size_sum = 0
        total_size = sum([s[1] for s in sizes])
        while size_sum < total_size:
            packet = client.recv(4096)

            size_sum += len(packet)
            for target in targets:
                try:
                    target.send(packet)
                except ConnectionError:
                    logging.info(f"{target_username} disconnected during send, aborting")
                    send_status("DISCONNECT")
                    return

        logging.info(f"files sent successfully from {sender_username} to {target_username}")

        send_status("OK")



    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.server.close()



if __name__ == "__main__":

    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename='log.log', filemode='w', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler()) # add console output

    try:
        with Server() as server:
            server.update()
    except Exception as e:
        if str(e) != "[Errno 98] Address already in use":
            logging.error(e)
            msg = f"MILC server has just crashed!\nTime of crash: {time.strftime('%b %d %Y %H:%M:%S')}\n\nException: {e}\n\nView the log on the server for more info".replace(' ', '╥').replace('\n', '╙')
            os.system(f"python3.10 DiscordSender.py {msg}")
