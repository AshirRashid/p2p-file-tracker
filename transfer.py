from socket import *
import os


def get_chunks(peer_port, save_dir='received_chunks', host='', func_after_chunk_transfer=(lambda filename: filename)):
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
            metadata, _, partial_content = received.partition('\n')
            filename, filesize = metadata.split(':', 1)
            filename = os.path.basename(filename)
            filesize = int(filesize)

            path = os.path.join(save_dir, filename)
            with open(path, 'wb') as f:
                f.write(partial_content.encode('utf-8'))
                filesize -= len(partial_content)
                while filesize > 0:
                    data = client_socket.recv(4096)
                    f.write(data)
                    filesize -= len(data)

            print(f"File {filename} has been received successfully.")
            # peer.register_chunk(filename)
            func_after_chunk_transfer(filename)
            client_socket.close()


def send_file_chunk(filepath, target_host, target_port):
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    with socket(AF_INET, SOCK_STREAM) as s:
        print(f"Connecting to {target_host}:{target_port}")
        s.connect((target_host, target_port))
        # Notice the newline character
        s.send(f"{filename}:{filesize}\n".encode('utf-8'))

        with open(filepath, 'rb') as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
        print(f"File {filepath[62:]} has been sent.")
