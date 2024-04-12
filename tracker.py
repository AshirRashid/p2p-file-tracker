from socket import *
import requests
import os

tracker_port = 12000
tracker_socket = socket(AF_INET, SOCK_STREAM)
tracker_socket.bind(('', tracker_port))
tracker_socket.listen(1)

peer_to_file_data = {}  # peer_port -> [file_name, file_hash]\

print("The server is ready to receive")
while True:
    print("Attempting to Connect")
    connectionSocket, addr = tracker_socket.accept()
    print("Connection Established")
    is_connection_close_req_recieved = False
    while True:
        reqs = connectionSocket.recv(1024).decode().split()
        for req in reqs:
            req_split = req.split(",")
            req_type = req_split[0]
            req_args = req_split[1:]
            if req_type == "register_file":  # Savaiz changed for having multiple files in same port
                peer_port, file_name, file_hash = req_args
                if peer_port in peer_to_file_data:
                    if not (file_hash in [registered_file_data[1] for registered_file_data in peer_to_file_data[peer_port]]):
                        peer_to_file_data[peer_port].append(
                            (file_name, file_hash))
                else:
                    peer_to_file_data[peer_port] = [(file_name, file_hash)]
                print(peer_to_file_data)
            elif req_type == "get_available_files":  # Savaiz wrote
                peer_port_to_str_file_data = {peer_port: ",".join(
                    [",".join(file_data) for file_data in peer_to_file_data[peer_port]]) for peer_port in peer_to_file_data}
                connectionSocket.send(str(peer_port_to_str_file_data).encode())
            elif req_type == "get_peers_with_file_by_hash":  # Savaiz wrote, sends the peer port
                file_hash = req_args  # not sure about this line
                for peer_port, files in peer_to_file_data.items():
                    for _, file_hash in files:
                        if file_hash == file_hash:
                            connectionSocket.send(f"{peer_port}\n".encode())
                            break
            elif req_type == "close_connection":
                is_connection_close_req_recieved = True
                break
        if is_connection_close_req_recieved:
            break

    print("Connection Closed")
    connectionSocket.close()
