import logging
import os
import pickle
import winreg

from AssiNet import *
import socket
from Settings import root, ip, username, version_path, executable_path
from Toaster import notify
from urllib.request import urlretrieve, urlopen

class Client:

    @staticmethod
    def update_users():
        logging.info("Updating users")
        def delete_subkeys(key0, current_key):
            # stolen from https://stackoverflow.com/questions/38205784/python-how-to-delete-registry-key-and-subkeys-from-hklm-getting-error-5
            with (winreg.OpenKey(key0, current_key, 0, winreg.KEY_ALL_ACCESS)) as key:
                info_key = winreg.QueryInfoKey(key)
                for x in range(info_key[0]):
                    sub_key = winreg.EnumKey(key, 0)
                    try:
                        winreg.DeleteKey(key, sub_key)
                    except OSError:
                        delete_subkeys(key0, "\\".join([current_key, sub_key]))

        def add(path, u, arg='%1'):
            with (winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{path}\shell\MILC2\shell\SendTo{u}")) as key:
                winreg.SetValue(key, "", winreg.REG_SZ, f"Send to {u}")
                winreg.SetValueEx(key, "Icon", None, winreg.REG_EXPAND_SZ, rf"%appdata%\MILC2\MILC2.ico")
            with (
            winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{path}\shell\MILC2\shell\SendTo{u}\command")) as key:
                winreg.SetValueEx(key, "", None, winreg.REG_EXPAND_SZ,
                                  f'%appdata%\MILC2\MILC2.exe "send" "{u}" "{arg}"')

        def get_users():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as getter:
                getter.connect((ip, PORT))
                send(getter, b"GET_USERS")
                return pickle.loads(recv(getter))

        delete_subkeys(winreg.HKEY_CLASSES_ROOT, r"*\shell\MILC2\shell")
        delete_subkeys(winreg.HKEY_CLASSES_ROOT, r"Directory\shell\MILC2\shell")
        delete_subkeys(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\MILC2\shell")

        for u in get_users():
            add("*", u)
            add("Directory", u)
            add("Directory\\Background", u, '%w')

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, PORT))
        send(self.client, username.encode())

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def listen(self):
        def on_click():
            dst = root + '\\' + os.path.dirname(path).replace('//', '/').replace('/', '\\')
            os.system(f"explorer {dst}")

        while True:
            ping = recv(self.client)
            assert ping == b"PING"
            send(self.client, b"PONG")
            for sender, path, file in recv_files(self.client):
                folder = os.path.dirname(path)
                os.makedirs(root + "/" + folder, exist_ok=True)
                with open(f"{root}/{path}", 'wb') as f:
                    f.write(file)

                notify(f'Received new file from {sender}\n\"{path}\"', on_click)
