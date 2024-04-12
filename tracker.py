from socket import *
import requests
import os

tracker_port = 12000
tracker_socket = socket(AF_INET, SOCK_STREAM)
tracker_socket.bind(('', tracker_port))
tracker_socket.listen(1)

peer_db = []
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
            if req_type == "register_peer":
                peer_port = req_args[0]
                peer_db.append(peer_port)
                print(peer_db)
            elif req_type == "register_file":  # Savaiz changed for having multiple files in same port
                peer_port, file_name, file_hash = req_args
                if peer_port in peer_to_file_data:
                    peer_to_file_data[peer_port].append((file_name, file_hash))
                else:
                    peer_to_file_data[peer_port] = [(file_name, file_hash)]
                print(peer_to_file_data)
            elif req_type == "get_available_files":  # Savaiz wrote
                files_message = "Here are the available files:\n"
                for i, peer_port in enumerate(peer_db, start=1):
                    files = peer_to_file_data.get(str(peer_port), [])
                    if files:
                        files_message += f"Files with peer {peer_port}:\n"
                        for file_name, file_hash in files:
                            files_message += f"- {file_name} (hash: {file_hash})\n"
                    else:
                        files_message += f"No files found for peer {peer_port}.\n"
                connectionSocket.send(files_message.encode())
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
