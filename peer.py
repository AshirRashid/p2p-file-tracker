from socket import *
from transfer import get_chunks
from globals import CHUNK_SIZE
import sys
import requests
import hashlib
import os
import ast

# Savaiz created: list of tuples (path, name, hash) for easier reference
file_directories = []


def get_testing_init_values():
    port = int(sys.argv[1])
    path = os.getcwd()
    dirpath = os.path.abspath(os.path.join(path, f"peer{sys.argv[2]}_dir/"))
    print(dirpath)

    return port, dirpath


def hash_file(filepath):
    """Generate SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:  # Open the file in binary mode
            for chunk in iter(lambda: f.read(4096), b""):
                # Update the hash with the chunk of file
                hash_sha256.update(chunk)
    except Exception as e:
        return f"An error occurred: {e}"

    return hash_sha256.hexdigest()


def divide_file_into_chunks(filename, output_dir='chunks', chunk_size=32768):  # Savaize added
    os.makedirs(output_dir, exist_ok=True)
    chunk_number = 0
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break  # End of file reached
            chunk_filename = os.path.join(
                output_dir, f'{os.path.basename(filename)}_chunk_{chunk_number}')
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)
            chunk_number += 1
    print(
        f'File divided into {chunk_number} chunks and saved in {output_dir}.')
    return chunk_number


class Peer():
    def __init__(self, port, dirpath):
        self.port = port
        self.dir = dirpath

    def register_peer(self, client_socket):
        client_socket.send(f"register_peer,{self.port}\n".encode())

    def initiate_client_socket_with_tracker(self):
        # Initiate a tcp client socket and connect with the tracker
        # Register peer and their files with the tracker
        client_socket = socket(AF_INET, SOCK_STREAM)
        tracker_name, tracker_port = "localhost", 12000
        client_socket.connect((tracker_name, tracker_port))
        print("Connection Established")
        return client_socket

    def close_client_socket_with_tracker(self, client_socket):
        self.close_tracker_connection(client_socket)
        client_socket.close()
        print("Connection Closed")

    def close_tracker_connection(self, client_socket):
        client_socket.send("close_connection\n".encode())

    def create_peer_server_socket(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(1)
        print("Peer Server Listening at", self.port)
        return server_socket

    def register_chunk(self, chunk_filename):
        client_socket = peer.initiate_client_socket_with_tracker()
        client_socket.send(
            f"register_chunk,{self.port},{chunk_filename}\n".encode())
        peer.close_tracker_connection(client_socket)


peer = Peer(*get_testing_init_values())
peer_client_socket = peer.initiate_client_socket_with_tracker()
peer.register_peer(peer_client_socket)
peer.close_client_socket_with_tracker(peer_client_socket)

print(peer.dir)
while True:
    get_chunks(peer.port, peer.dir,
               func_after_chunk_transfer=peer.register_chunk)
