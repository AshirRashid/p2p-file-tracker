from socket import *
import sys
import requests
import hashlib
import os

# Savaiz created: list of tuples (path, name, hash) for easier reference
file_directories = []


def get_testing_init_values():
    port = int(sys.argv[1])
    path = os.getcwd()
    dirpath = os.path.join(path, f"/peer{sys.argv[2]}_dir/")

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
                    file_directories.append(
                        self.dir+file_name, file_name, file_hash)
                    client_socket.send(
                        f"register_file,{self.port},{file_name},{file_hash}\n".encode())

    def get_available_files(self, client_socket):
        client_socket.send("get_available_files\n".encode())
        available_files = client_socket.recv(1024).decode()
        return available_files

    def get_peer_with_file_by_hash(self, client_socket, file_hash):  # Savaiz added
        client_socket.send(
            f"get_peer_with_file_by_hash,{file_hash}\n".encode())

    def send_file_to_peer(self, client_socket, peer_port, target_file_hash):  # Savaiz added
        for path, file_name, file_hash in file_directories:
            if file_hash == target_file_hash:
                target_file_path = path
                target_file_name = file_name
                print(target_file_path)
                break
        chunk_number = divide_file_into_chunks(target_file_path)
        for i in range(chunk_number):
            chunk_filename = os.path.join(
                f'{os.path.basename(target_file_path)}_chunk_{i}')
            with socket(AF_INET, SOCK_STREAM) as s:
                print(f"Connecting to {'127.0.0.1'}:{peer_port}")
                s.connect(('127.0.0.1', peer_port))
                s.send(f"{chunk_filename}:{os.path.getsize(chunk_filename)}\n".encode(
                    'utf-8'))  # Notice the newline character

                with open(chunk_filename, 'rb') as f:
                    while True:
                        bytes_read = f.read(4096)
                        if not bytes_read:
                            break
                        s.sendall(bytes_read)
                print(f"File {chunk_filename} has been sent.")
        print(f"{target_file_name} has been sent")

    def close_connection(self, client_socket):
        client_socket.send("close_connection\n".encode())


while True:
    peer = Peer(*get_testing_init_values())
    client_socket = peer.initiate_client_socket_with_tracker()
    # connectionSocket, addr = peer_socket.accept()
    available_files = peer.get_available_files(client_socket)
    # sentence = client_socket.recv(1024).decode()
    # print(sentence)
    break
