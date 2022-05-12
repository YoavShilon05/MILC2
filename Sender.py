import glob
import os
import pickle

from AssiNet import *
from Settings import ip, username
from Toaster import notify

class Sender:

    def __init__(self):
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sender.connect((ip, PORT))
        send(self.sender, b"SEND")  # send name

    def send(self, path, target):
        if os.path.isdir(path):  # kusomo
            tree = list(map(lambda s: s.replace('\\', '/'), glob.glob(path + "/**/*.*", recursive=True)))
            send_files(self.sender, username, target, tree, path)


        elif os.path.isfile(path):
            send_files(self.sender, username, target, [path], path)

        result = recv(self.sender)

        match result:
            case b"OFFLINE":
                notify(f"{target} is currently offline")
            case b"LOGOFF":
                notify(f"{target} logged out during file transfer")
            case b"OK":
                notify("files sent successfully!")

    def __enter__(self): return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sender.close()
