from socket import *
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

    def register_chunk(self, client_socket, file_hash, chunk_filename):
        client_socket.send(
            f"register_chunk,{self.port},{file_hash},{chunk_filename}\n".encode())


peer = Peer(*get_testing_init_values())
peer_client_socket = peer.initiate_client_socket_with_tracker()
peer.register_peer(peer_client_socket)
peer.close_client_socket_with_tracker(peer_client_socket)


def get_chunks(peer_port, save_dir='received_chunks', host=''):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind((host, peer_port))
        server_socket.listen()
        print(f"Listening as {host}:{peer_port}...")

        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address} has been established.")

            received = client_socket.recv(1024).decode('utf-8')
            metadata, _, partial_content = received.partition('\n')
            filename, filesize = metadata.split(':', 1)
            filename = os.path.basename(filename)
            filesize = int(filesize)

            path = os.path.join(save_dir, filename)
            with open(path, 'wb') as f:
                f.write(partial_content.encode('utf-8'))
                filesize -= len(partial_content)
                while filesize > 0:
                    data = client_socket.recv(4096)
                    f.write(data)
                    filesize -= len(data)

            print(f"File {filename} has been received successfully.")
            client_socket.close()


while True:
    # peer_server_socket = peer.create_peer_server_socket()
    # print("Accepting Connections")
    # connection_socket, addr = peer_server_socket.accept()
    # print("Connection Established")
    get_chunks(peer.port)
    # while True:
    #     sentence = connection_socket.recv(1024).decode()
    #     print(sentence)

    print("Connection Established")

    # received = connection_socket.recv(1024).decode()
    # metadata, _, partial_content = received.partition('\n')
    # chunk_filename, filesize = metadata.split(':', 1)
    # chunk_filename = os.path.basename(chunk_filename)

    # path = os.path.join(peer.dir, chunk_filename)
    # with open(path, 'wb') as f:
    #     f.write(partial_content.encode())
    #     filesize -= len(partial_content)
    #     while filesize > 0:
    #         data = connection_socket.recv(4096)
    #         f.write(data)
    #         filesize -= len(data)

    # print(f"File {chunk_filename} has been received successfully.")
    # connection_socket.close()

    # peer_client_socket = peer.initiate_client_socket_with_tracker()
    # peer.register_chunk(peer_client_socket, )
    # peer.close_client_socket_with_tracker(peer_client_socket)


# def start_server(host='0.0.0.0', port=5000, save_dir='received_chunks'):
#     if not os.path.exists(save_dir):
#         os.makedirs(save_dir)
