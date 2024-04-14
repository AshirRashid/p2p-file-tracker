from socket import *
import requests
import os

tracker_port = 12000
tracker_socket = socket(AF_INET, SOCK_STREAM)
tracker_socket.bind(('', tracker_port))
tracker_socket.listen(1)

peer_db = set()
peer_to_file_data = {}  # peer_port -> [file_name, file_hash]\

print("The server is ready to receive")
while True:
    print("Accepting Connections")
    connectionSocket, addr = tracker_socket.accept()
    print("Connection Established")
    is_connection_close_req_recieved = False
    while True:
        reqs = connectionSocket.recv(1024).decode().split()
        for req in reqs:
            req_split = req.split(",")
            req_type = req_split[0]
            req_args = req_split[1:]
            print("Request Recieved:", req_type)
            if req_type == "register_peer":
                peer_port = req_args[0]
                peer_db.add(peer_port)
                print(f"{peer_port} Registered as a Peer")
                print("Peer DB:", peer_db)
            elif req_type == "get_peers":
                connectionSocket.send(str(peer_db).encode())
            elif req_type == "register_chunk":  # Savaiz changed for having multiple files in same port
                peer_port, file_name = req_args
                peer_to_file_data[peer_port] = peer_to_file_data.get(
                    peer_port, set()).union({file_name})
                print(peer_to_file_data)
            elif req_type == "get_available_files":  # Savaiz wrote
                peer_port_to_str_file_data = {peer_port: ",".join(
                    peer_to_file_data[peer_port]) for peer_port in peer_to_file_data}
                connectionSocket.send(str(peer_port_to_str_file_data).encode())
            elif req_type == "close_connection":
                is_connection_close_req_recieved = True
                break
        if is_connection_close_req_recieved:
            break

    print("Connection Closed")
    connectionSocket.close()
