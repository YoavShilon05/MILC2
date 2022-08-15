import logging
import os
import pickle
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

def recv_files(conn:socket.socket):

    ### HEADER

    logging.info("attempting to receive header")
    header = recv(conn)
    logging.info(f"received header")
    sender, sizes = pickle.loads(header)
    logging.info(f"header contents: {sender} sent {sizes}")
    ### FILES

    data = b''
    result_size = sum([s[1] for s in sizes])

    total_size = 0
    current_file = 0

    while total_size < result_size:
        packet = conn.recv(4096)
        total_size += len(packet)
        data += packet

        while current_file < len(sizes) and len(data) >= sizes[current_file][1]:
            yield [sender, sizes[current_file][0], data[:sizes[current_file][1]]]
            data = data[sizes[current_file][1]:]
            current_file += 1


def send(conn: socket.socket, msg: bytes):
    size = f"{len(msg):0{MSG_SIZE}}" # {MSG_SIZE} because yoav is mentally sane
    conn.send(size.encode() + msg)

def send_files(conn: socket.socket, sender, target, paths, parent_dir=None):

    sizes = [
        # path : size of file
    ]

    data = b''
    for i, p in enumerate(paths):
        with open(p, 'rb') as f:
            content = f.read()
            data += content

            target_path = os.path.basename(parent_dir) + ('/' if parent_dir != p else "") + p.replace('\\',
                                                                                                      '/').replace(
            parent_dir.replace('\\', '/'), "")  # parent_folder + any directories in between + basename

            sizes.append((target_path, len(content)))

    send(conn, pickle.dumps([sender, target, sizes]))

    conn.send(data)