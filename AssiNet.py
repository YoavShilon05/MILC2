import socket
from typing import TYPE_CHECKING
from math import ceil

PORT = 5926
MSG_SIZE = 12
def recv(conn: socket.socket, timeout=None) -> bytes:
    socket.setdefaulttimeout(timeout)

    try:
        ss = conn.recv(MSG_SIZE).decode()
    except socket.timeout:
        if not timeout:
            raise socket.timeout
        else: return

    size = int(ss)  # {MSG_SIZE} because yoav is mentally sane
    return conn.recv(size)



def send(conn: socket.socket, msg: bytes):
    size = f"{len(msg):0{MSG_SIZE}}" # {MSG_SIZE} because yoav is mentally sane
    conn.send(size.encode() + msg)