import sys
import os
from socket import *
from transfer import process_chunk
from globals import CHUNK_SIZE, TRACKER_PORT, TRACKER_HOST


class Peer():
    def __init__(self, port, dirpath):
        self.port = port
        self.dir = dirpath

        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def register_peer(self, client_socket):
        """Inform the tracker that self is a part of the network
        """
        client_socket.send(f"register_peer,{self.port}\n".encode())

    def initiate_client_socket_with_tracker(self):
        """Initiate a tcp client socket and connect with the tracker
        """
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((TRACKER_HOST, TRACKER_PORT))
        print("Connection Established")
        return client_socket

    def close_client_socket_with_tracker(self, client_socket):
        """Make sure the a socket connected with the tracker is properly closed on both sides
        """
        self.close_tracker_connection(client_socket)
        client_socket.close()
        print("Connection Closed")

    def close_tracker_connection(self, client_socket):
        """Informs the tracker that self is about to close the connection
        """
        client_socket.send("close_connection\n".encode())

    def register_chunk(self, chunk_filename):
        """Informs the tracker that self has a certain chunk
        """
        client_socket = peer.initiate_client_socket_with_tracker()
        client_socket.send(
            f"register_chunk,{self.port},{chunk_filename}\n".encode())
        peer.close_tracker_connection(client_socket)


port = int(sys.argv[1])
path = os.getcwd()
dirpath = os.path.abspath(os.path.join(path, sys.argv[2]))

peer = Peer(port, dirpath)
peer_client_socket = peer.initiate_client_socket_with_tracker()
peer.register_peer(peer_client_socket)
peer.close_client_socket_with_tracker(peer_client_socket)


print(peer.dir)
while True:
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', peer.port))
        server_socket.listen(1)

        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address} has been established.")

            received = client_socket.recv(1024).decode('utf-8')
            req_type, req_args = received.split(",", 1)
            print(received)

            print("Request Received of type", req_type)

            if req_type == "share_chunk":
                data = req_args
                filename = process_chunk(data, peer.dir)
                peer.register_chunk(filename)

            elif req_type == "request_chunk":
                filename = req_args
                filepath = os.path.join(peer.dir, filename)
                filesize = os.path.getsize(filepath)
                metadata = f"{filename}:{filesize}--meta-data--".encode(
                    'utf-8')
                with open(filepath, 'rb') as f:
                    bytes_read = f.read(4096)
                    client_socket.sendall(metadata + bytes_read)
                    print(f"File {filepath[62:]} has been sent.")
            client_socket.close()
