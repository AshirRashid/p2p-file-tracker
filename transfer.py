from socket import *
from globals import CHUNK_SIZE
import os


def get_chunks(peer_port, save_dir='received_chunks', host='localhost', func_after_chunk_transfer=(lambda filename: filename)):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind((host, peer_port))
        server_socket.listen()
        print(f"Listening as {host}:{peer_port}...")

        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address} has been established.")

            received = client_socket.recv(1024).decode('utf-8')

            filename = process_chunk(received, save_dir)
            func_after_chunk_transfer(filename)
            client_socket.close()


def process_chunk(data, save_dir):
    metadata, chunk_content = data.split("--meta-data--")
    if metadata:
        filename, filesize = metadata.split(':')
        filename = os.path.basename(filename)
        filesize = int(filesize)
        print(filesize)

    if chunk_content:
        path = os.path.join(save_dir, filename)
        with open(path, 'wb') as f:
            f.write(chunk_content.encode('utf-8'))

        print(f"File {filename} has been received successfully.")
    return filename


def send_file_chunk(filepath, target_host, target_port):
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    with socket(AF_INET, SOCK_STREAM) as s:
        print(f"Connecting to {target_host}:{target_port}")
        s.connect((target_host, target_port))
        req_type = "share_chunk"
        metadata = f"{req_type},{filename}:{filesize}--meta-data--".encode(
            'utf-8')

        with open(filepath, 'rb') as f:
            bytes_read = f.read(4096)
            s.sendall(metadata + bytes_read)
        print(f"File {filepath[62:]} has been sent.")
