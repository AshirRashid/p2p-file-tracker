import socket, os

def start_server(host='0.0.0.0', port=5000, save_dir='received_chunks'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Listening as {host}:{port}...")

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
            client_socket.close()

if __name__ == "__main__":
    start_server()
