from socket import *
import requests
import os

tracker_port = 12000
tracker_socket = socket(AF_INET, SOCK_STREAM)
tracker_socket.bind(('', tracker_port))
tracker_socket.listen(1)

peer_db = []
peer_to_file_data = {}  # peer_port -> [file_name, file_hash]

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
            if req_type == "register_peer":
                peer_port = req_args[0]
                peer_db.append(peer_port)
                print(peer_db)
            elif req_type == "register_file":
                peer_port, file_name, file_hash = req_args
                peer_to_file_data[peer_port] = [file_name, file_hash]
                print(peer_to_file_data)
            elif req_type == "get_available_files":
                connectionSocket.send("here are the available files".encode())
            elif req_type == "close_connection":
                is_connection_close_req_recieved = True
                break
        if is_connection_close_req_recieved:
            break

    print("Connection Closed")
    connectionSocket.close()
