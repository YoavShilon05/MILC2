"""
TODO:
- uninstaller
- massive test

"DONE":
- send crash error on discord

DONE:
- hebrew?
- log stuff
- the updater "doesn't send notifications"
- user is offline when they aren't
- updater
- make updating users possible without restarting MILC2
- but also make it easier to restart MILC2 than to have to kill it and then launch it through tasks
- basically make tray is what ori is trying to say here 😢
- also make it so that you can launch MILC2 through search
- server doesn't work after crash
- don't request admin on send
- installer doesn't work when launching without cmd :(
"""
import os
import threading
import time
from AssiNet import *
import socket
import pickle
import logging

def handle_error(e):
    if str(e) != "[Errno 98] Address already in use":
        logging.error(e)
        msg = f"MILC server has just crashed!\nTime of crash: {time.strftime('%b %d %Y %H:%M:%S')}\n\nException: {e}\n\nView the log on the server for more info\nIf you wish to restart the server, please do so manually through the server.".replace(
            ' ', '╥').replace('\n', '╙')
        os.system(f"python3.10 DiscordSender.py {msg}")
    else:
        print("address already in use 😠")

SERVER = socket.gethostbyname(socket.gethostname())

ADDR = (SERVER, PORT)

connections: dict[str, list[socket.socket]] = {}
SUICIDE_TIMEOUT = 30

class Server:

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.server.listen()
        logging.info(f"Server is listening on address {ADDR}...")

    def update(self):

        while True:
            client, client_ip = self.server.accept()
            logging.info(f"{client_ip} connected")
            cmd = recv(client).decode()
            logging.info(f"received command {cmd}")

            match cmd:
                case "SEND":
                    t = threading.Thread(target=self.handle_sender, args=[client])
                    t.start()
                    logging.info("started new handle_sender thread due to SEND")
                case "GET_USERS":
                    users = list(connections.keys())
                    logging.info(f"users list requested, sending {users}")
                    send(client, pickle.dumps(users))
                    logging.info("users list sent successfully")
                case _:
                    name = cmd # client connected, username was sent
                    if name in connections:
                        logging.info(f"client {name} connected, appending to existing connection(s)")
                        connections[name].append(client)
                    else:
                        logging.info(f"client {name} connected, creating new connection")
                        connections[name] = [client]

    def handle_sender(self, client : socket.socket):
        logging.info("entered handle_sender thread")
        def send_status(status):
            try:
                logging.info(f"trying to send status {status}")
                send(client, status.encode())
                logging.info("sent status successfully")
            except ConnectionError as e:
                logging.warning(f"unable to send status, error: {e}. the code just passes so this might be okay")
                pass

        try:
            peer = client.getpeername()
            logging.info(f"waiting to receive header from client {peer}")
            header = pickle.loads(recv(client))
            logging.info(f"got header {header} from client {peer}")

            sender_username, target_username, sizes = header
            logging.info(f"{sender_username} sent {target_username} (client {peer}) {sizes} bytes of files")

            logging.info(f"checking whether {target_username} is online")

            if target_username not in connections or len(connections[target_username]) == 0:
                logging.info(f"{target_username} was offline, send aborted")
                send_status("OFFLINE")
                return

            targets = connections[target_username]

            logging.info(f"found connection for {target_username} in memory, checking if active")

            found = False
            for i, target in enumerate(targets.copy()):
                try:
                    logging.info(f"trying to ping target number {i} of {target_username}")
                    send(target, b"PING")
                    ping_answer = recv(target, SUICIDE_TIMEOUT)
                    assert ping_answer == b"PONG";
                except ConnectionError as e:
                    connections[target_username].remove(target)
                    logging.info(f"target number {i} of {target_username} did not answer, removing from memory")
                    logging.warning(e)
                    continue
                except AssertionError:
                    connections[target_username].remove(target)
                    # noinspection PyUnboundLocalVariable
                    logging.info(f"target number {i} of {target_username} answered '{ping_answer.decode()}' instead of 'PONG', removing from memory")
                logging.info(f"target number {i} of {target_username} was active, sending header: {[sender_username, sizes]}")
                send(target, pickle.dumps([sender_username, sizes]))
                logging.info("sent header successfully")
                found = True

            if not found:
                logging.info(f"{target_username} was offline, aborting")
                send_status("OFFLINE")
                return

            logging.info(f"{target_username} was online, starting to send...")

            size_sum = 0
            total_size = sum([s[1] for s in sizes])
            logging.info(f"total size of all packets being sent from {sender_username} to {target_username} is {total_size}")
            while size_sum < total_size:
                packet = client.recv(4096)

                size_sum += len(packet)
                for target in targets:
                    try:
                        target.send(packet)
                    except ConnectionError as e:
                        logging.warning(e)
                        logging.info(f"{target_username} disconnected during send, aborting")
                        send_status("DISCONNECT")
                        return

            logging.info(f"files sent successfully from {sender_username} to {target_username}, actual size of packets was {size_sum}")

            send_status("OK")

        except Exception as e:
            handle_error(e)

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.server.close()

if __name__ == "__main__":

    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', filename='log.log', filemode='w', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler()) # add console output

    try:
        with Server() as server:
            server.update()
    except Exception as e:
        handle_error(e)