from socket import *
import sys
import requests
import hashlib
import os


peer_port = int(sys.argv[1])
peer_dir = f"/Users/ashir/Desktop/networks/final_project/Networks_Project_Savaiz/peer{sys.argv[2]}_dir/"
peer_socket = socket(AF_INET, SOCK_STREAM)
# peer_socket.bind(('', peer_port))
# peer_socket.listen(1)

tracker_name, tracker_port = "localhost", 12000


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


def register_peer():
    peer_socket.send(f"register_peer,{peer_port}\n".encode())


def register_shareable_files():
    # for all files in shareable_files

    # List all files in a directory using os.scandir()
    with os.scandir(peer_dir) as entries:
        for entry in entries:
            if entry.is_file():  # Check if it's a file
                file_name = entry.name
                file_hash = hash_file(peer_dir + file_name)
                peer_socket.send(
                    f"register_file,{peer_port},{file_name},{file_hash}\n".encode())


def get_available_files():
    peer_socket.send("get_available_files\n".encode())


def close_connection():
    peer_socket.send("close_connection\n".encode())


while True:
    # connectionSocket, addr = peer_socket.accept()
    peer_socket.connect((tracker_name, tracker_port))
    print("Connection Established")
    register_peer()
    register_shareable_files()
    close_connection()
    # while True:
    #     cmd = input().lower()
    #     peer_socket.send("get_available_files")
    #     sentence = peer_socket.recv(1024).decode()
    #     print(sentence)
    peer_socket.close()
    print("Connection Closed")
    break
