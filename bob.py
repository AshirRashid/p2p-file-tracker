from socket import *

serverName = "localhost"
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

while True:
    sentence = input("Input lowercase sentence:")
    clientSocket.send(sentence.encode())
    modifiedSentence = clientSocket.recv(1024)
    if sentence == "exit":
        break
    print("From Server:", modifiedSentence.decode())
clientSocket.close()


# Retreiving the file
def get_available_files(self, client_socket):
    client_socket.send("get_available_files\n".encode())
    available_files = client_socket.recv(1024).decode()
    return available_files

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
