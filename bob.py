# CLI argumentd
# command: options | get_file {filename}
from socket import *
from transfer import process_chunk
import ast
import os
import sys


bob_dir = "/Users/ashir/Desktop/networks/final_project/Networks_Project_Savaiz/bob_dir"
tracker_host, tracker_port = "localhost", 12000


def get_available_files(client_socket):
    client_socket.send("get_available_files\n".encode())
    available_files_str = client_socket.recv(1024).decode()
    data_dict = ast.literal_eval(available_files_str)

    # Reverse the string concatenation of filenames
    peer_port_to_file_data = {int(port): set(filenames.split(','))
                              for port, filenames in data_dict.items()}
    return peer_port_to_file_data


def get_matching_files(port_to_filenames, file_to_search):
    search_pattern = file_to_search + "_chunk_"
    port_to_matching_files = {}

    for port, filenames in port_to_filenames.items():
        # Filter filenames that start with the base filename followed by "_chunk_"
        matched = {
            filename for filename in filenames if filename.startswith(search_pattern)}
        if matched:
            port_to_matching_files[port] = matched

    return port_to_matching_files


def request_chunk_from_peer(client_socket, filename):
    client_socket.send(f"request_chunk,{filename}".encode())
    data = client_socket.recv(1024).decode()
    filename = process_chunk(
        data, bob_dir)


def reconstruct_file(directory, base_filename):
    # List to hold tuples of chunk number and file path
    chunks = []

    # Define the start of the file name to match
    filename_start = f"{base_filename}_chunk_"

    # Walk through the directory and add matching files to the list
    for filename in os.listdir(directory):
        if filename.startswith(filename_start):
            chunk_part = filename[len(filename_start):]
            try:
                # Convert the remaining part to an integer
                chunk_number = int(chunk_part)
                chunks.append(
                    (chunk_number, os.path.join(directory, filename)))
            except ValueError:
                # If conversion fails, skip the file
                continue

    # Sort chunks by chunk number
    chunks.sort()

    # Check if chunks list is empty (i.e., no chunks were found)
    if not chunks:
        print(f"No chunks found for {base_filename}.")
        return

    # Open the output file to write concatenated chunks
    output_path = os.path.join(directory, base_filename)
    with open(output_path, 'wb') as output_file:
        for _, chunk_path in chunks:
            with open(chunk_path, 'rb') as f:
                output_file.write(f.read())
        print(f"Created complete file: {output_path}")


cmd = sys.argv[1]

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((tracker_host, tracker_port))

peer_port_to_filenames = get_available_files(clientSocket)
clientSocket.send("close_connection\n".encode())
clientSocket.close()

if cmd == "options":
    # prints options of files that can be downloaded
    base_filenames = set()
    for chunks in peer_port_to_filenames.values():
        for filename in chunks:
            base_name = filename.rsplit('_chunk_', 1)[0]
            base_filenames.add(base_name)
    print(*base_filenames)

elif cmd == "get":
    base_filename = sys.argv[2]
    port_to_matching_filenames = get_matching_files(
        peer_port_to_filenames, base_filename)

    for peer_port, filenames in port_to_matching_filenames.items():
        for filename in filenames:
            with socket(AF_INET, SOCK_STREAM) as client_socket:
                client_socket.connect(('', peer_port))
                print("Connection Established with", peer_port)
                request_chunk_from_peer(
                    client_socket, filename)

    reconstruct_file(bob_dir, base_filename)
