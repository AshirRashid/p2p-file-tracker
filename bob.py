from socket import *
from transfer import process_chunk
import ast

serverName = "localhost"
serverPort = 12000


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
    print(data)
    filename = process_chunk(
        data, "/Users/ashir/Desktop/networks/final_project/Networks_Project_Savaiz/bob_dir")


clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

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


breakpoint()


# Retreiving the file

# if cmd == "get":
#     # get the peer_port and file data in the form of a string and convert it to a dictionary using the ast module
#     peer_port_to_str_file_data = ast.literal_eval(
#         peer.get_available_files(client_socket))
#     print(peer_port_to_str_file_data)
#     peer_port_to_file_data = {}
#     for peer_port, files_string in peer_port_to_str_file_data.items():
#         file_entries = files_string.split(',')
#         peer_port_to_file_data[int(peer_port)] = [file_entries[i:i+2]
#                                                   for i in range(0, len(file_entries), 2)]

#     peer.close_client_socket_with_tracker(client_socket)
#     breakpoint()
#     # peer.initiate_client_socket_with_peer()

#     # TODO 2
#     # Prompt the user for which file they want from peer_port_to_file_data and from which peer
#     # use peer.initiate_client_socket_with_peer to communicate with the chosen peer to get the chosen file
#     # request a file from the chosen peer server
#     # download the file in the peer folder
