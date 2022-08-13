# import glob
import logging
import os
import pickle
import sys

from AssiNet import *
from Settings import ip, username
from Toaster import notify, open_explorer_on_click


def glob(path): # this name has no meaning!
    for file in os.listdir(path):
        full_path = os.path.join(path, file)
        if os.path.isfile(full_path):
            yield full_path
        else:
            yield from glob(full_path)


class Sender:

    def __init__(self):
        logging.info(f"Initiating a new Sender...")
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.info(f"Connecting sender to {(ip, PORT)}")
        self.sender.connect((ip, PORT))

        logging.info(f"Sending server username SEND (to indicate a send client)")
        send(self.sender, b"SEND")  # send name

    def send(self, path, target):
        logging.info(f"Sending a new file or folder at {path} to {target}")
        if os.path.isdir(path):  # kusomo
            files = [x for x in glob(path)]
            send_files(self.sender, username, target, files, path)


        elif os.path.isfile(path):
            send_files(self.sender, username, target, [path], path)

        logging.info(f"Receiving result of send...")
        result = recv(self.sender)

        match result:
            case b"OFFLINE":
                logging.info(f"Target was reported offline")
                notify(f"{target} is currently offline")
            case b"LOGOFF":
                logging.info(f"Target was reported logging off during the file transfer")
                notify(f"{target} logged out during file transfer")
            case b"OK":
                logging.info(f"Reported files sent OK")
                notify("files sent successfully!", on_click=open_explorer_on_click(path))

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info(f"Closing sender...")
        self.sender.close()
