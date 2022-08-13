import logging
import winreg

from AssiNet import *
import socket
from Settings import root, ip, username
from Toaster import notify, open_explorer_on_click

class Client:

    def __init__(self):
        logging.info("Starting client...")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"Connecting socket to {(ip, PORT)}")
        self.client.connect((ip, PORT))
        logging.info(f"Sending username ({username}) to server")
        send(self.client, username.encode())

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info(f"Closing client...")
        self.client.close()

    def listen(self):
        logging.info("Client started listening...")

        while True:
            logging.info(f"Waiting for PING from server (will only receive after file has been sent)")
            ping = recv(self.client)
            logging.info(f"Received {ping.decode()}, should be PING")
            assert ping == b"PING"
            logging.info(f"Asserted ping == PING, sending PONG")
            send(self.client, b"PONG")

            logging.info(f"Listening for files...")
            for sender, local_path, file in recv_files(self.client):
                logging.info(f"Received a new file from {sender}, destined path: {local_path}")
                folder = os.path.dirname(local_path)

                logging.info(f"Attempting to make folder {folder} for file {local_path}. {root=}. "
                             f"new_folder_path: {root + '/' + folder} (exist_ok)")
                os.makedirs(root + "/" + folder, exist_ok=True)

                with open(f"{root}/{local_path}", 'wb') as f:
                    f.write(file)

                logging.info(f"Finished writing file {local_path}, size: {len(file)}")
                notify(f'Received new file from {sender}\n\"{local_path}\"', open_explorer_on_click(local_path))
