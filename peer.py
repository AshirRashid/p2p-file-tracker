from socket import *
import sys
import requests
import hashlib
import os


def get_testing_init_values():
    port = int(sys.argv[1])
    dirpath = f"/Users/ashir/Desktop/networks/final_project/Networks_Project_Savaiz/peer{sys.argv[2]}_dir/"

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

    def initiate_client_socket_with_tracker(self):
        # Initiate a tcp client socket and connect with the tracker
        # Register peer and their files with the tracker
        client_socket = socket(AF_INET, SOCK_STREAM)
        tracker_name, tracker_port = "localhost", 12000
        client_socket.connect((tracker_name, tracker_port))
        print("Connection Established")
        self.register_peer(client_socket)
        self.register_shareable_files(client_socket)
        return client_socket

    def close_client_socket_with_tracker(self, client_socket):
        self.close_connection(client_socket)
        client_socket.close()
        print("Connection Closed")

    def register_peer(self, client_socket):
        client_socket.send(f"register_peer,{self.port}\n".encode())

    def register_shareable_files(self, client_socket):
        # List all files in a directory using os.scandir()
        with os.scandir(self.dir) as entries:
            for entry in entries:
                if entry.is_file():  # Check if it's a file
                    file_name = entry.name
                    file_hash = hash_file(self.dir + file_name)
                    client_socket.send(
                        f"register_file,{self.port},{file_name},{file_hash}\n".encode())

    def get_available_files(self, client_socket):
        client_socket.send("get_available_files\n".encode())

    def close_connection(self, client_socket):
        client_socket.send("close_connection\n".encode())


while True:
    peer = Peer(*get_testing_init_values())
    client_socket = peer.initiate_client_socket_with_tracker()
    # connectionSocket, addr = peer_socket.accept()
    peer.get_available_files(client_socket)
    sentence = client_socket.recv(1024).decode()
    print(sentence)
    break
