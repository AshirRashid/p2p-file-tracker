# Sharing the file
import socket
import os
import ast
from socket import *
from transfer import send_file_chunk
from globals import CHUNK_SIZE


def get_peers(client_socket):
    client_socket.send("get_peers\n".encode())
    peers_set = client_socket.recv(1024).decode()
    return peers_set


def divide_file_into_chunks(filename, output_dir='chunks'):
    """
    Divide a file into chunks and save each chunk as a separate file.

    Args:
        filename (str): Path to the source file to be divided.
        output_dir (str): Directory where chunk files will be saved.
        chunk_size (int): Size of each chunk in bytes.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    chunk_paths_list = []

    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break  # End of file reached
            chunk_filename = os.path.join(
                output_dir, f'{os.path.basename(filename)}_chunk_{len(chunk_paths_list)}')
            chunk_paths_list.append(chunk_filename)
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)

    return chunk_paths_list


def distribute_list_items(items, m):
    n = len(items)
    base = n // m
    remainder = n % m
    buckets = []
    start_index = 0

    for i in range(m):
        end_index = start_index + base + (1 if i < remainder else 0)
        buckets.append(items[start_index:end_index])
        start_index = end_index

    return buckets


sender_client_socket = socket(AF_INET, SOCK_STREAM)
tracker_name, tracker_port = "localhost", 12000
sender_client_socket.connect((tracker_name, tracker_port))
print("Connection Established")
peers = ast.literal_eval(get_peers(sender_client_socket))
print(peers)
sender_client_socket.send("close_connection\n".encode())
sender_client_socket.close()

chunk_paths = divide_file_into_chunks(
    "/Users/ashir/Desktop/networks/final_project/Networks_Project_Savaiz/alice_dir/file1")

# mapping from peer_port to the chunk paths to be sent to this port
peer_to_chunk_paths = dict(
    zip(peers, distribute_list_items(chunk_paths, len(peers))))


for peer_port in peer_to_chunk_paths:
    for chunk_path in peer_to_chunk_paths[peer_port]:
        send_file_chunk(chunk_path, "localhost", int(peer_port))
    print(f"Connecting to localhost:{peer_port}")
