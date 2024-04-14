from socket import *
from transfer import process_chunk
import ast


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
        data, "/Users/ashir/Desktop/networks/final_project/Networks_Project_Savaiz/bob_dir")


clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((tracker_host, tracker_port))

peer_port_to_filenames = get_available_files(clientSocket)
clientSocket.send("close_connection\n".encode())
clientSocket.close()

port_to_matching_filenames = get_matching_files(
    peer_port_to_filenames, "file1")


for peer_port, filenames in port_to_matching_filenames.items():
    for filename in filenames:
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect(('', peer_port))
            print("Connection Established with", peer_port)
            request_chunk_from_peer(
                client_socket, filename)
