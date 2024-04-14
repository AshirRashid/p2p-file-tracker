from socket import *
from transfer import process_chunk
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


class Peer():
    def __init__(self, port, dirpath):
        self.port = port
        self.dir = dirpath

        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

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
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind(('', peer.port))
        server_socket.listen(1)

        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address} has been established.")

            received = client_socket.recv(1024).decode('utf-8')
            req_type, req_args = received.split(",", 1)
            print(received)

            print("Request Received of type", req_type)

            if req_type == "share_chunk":
                data = req_args
                filename = process_chunk(data, peer.dir)
                peer.register_chunk(filename)

            elif req_type == "request_chunk":
                filename = req_args
                filepath = os.path.join(peer.dir, filename)
                filesize = os.path.getsize(filepath)
                metadata = f"{filename}:{filesize}--meta-data--".encode(
                    'utf-8')
                with open(filepath, 'rb') as f:
                    bytes_read = f.read(4096)
                    client_socket.sendall(metadata + bytes_read)
                    print(f"File {filepath[62:]} has been sent.")
            client_socket.close()
