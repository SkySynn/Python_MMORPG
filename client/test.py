import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))

client_socket.send("register testuser testpassword".encode())
reponse = client_socket.recv(1024).decode()
print(reponse)

client_socket.close()