import socket, os
from chunker import divide_file_into_chunks

def send_file_chunk(filepath, target_host, target_port):
    filesize = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to {target_host}:{target_port}")
        s.connect((target_host, target_port))
        s.send(f"{filename}:{filesize}\n".encode('utf-8'))  # Notice the newline character

        with open(filepath, 'rb') as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                s.sendall(bytes_read)
        print(f"File {filepath[62:]} has been sent.")

if __name__ == "__main__":
    PATH = os.getcwd()
    base_file = os.path.join(PATH, "test1.txt")
    chunk_number = divide_file_into_chunks(base_file)
    for i in range(chunk_number):
        chunk_filename = os.path.join(PATH, f'chunks/{os.path.basename(base_file)}_chunk_{i}')
        peer_address = ('127.0.0.1', 5000)
        send_file_chunk(chunk_filename, *peer_address)