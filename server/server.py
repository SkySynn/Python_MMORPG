import socket
import threading
import sqlite3
import bcrypt  # Pour hacher les mots de passe

clients = {}  # Dictionnaire pour stocker les sockets des clients et leurs positions

def gérer_client(client_socket, addr):
    print(f"[NOUVEAU] {addr} connecté.")
    clients[addr] = {'socket': client_socket, 'x': 100, 'y': 100}  # Position initiale

    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Séparer la commande des arguments
            commande, *args = data.split()

            if commande == "login":
                username, password = args
                # Vérifier les informations d'identification dans la base de données
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username=?", (username,))
                resultat = cursor.fetchone()
                conn.close()

                if resultat and bcrypt.checkpw(password.encode(), resultat[0]):
                    client_socket.send("login_ok".encode())
                else:
                    client_socket.send("login_failed".encode())

            elif commande == "register":
                username, password = args
                # Hacher le mot de passe
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

                # Insérer le nouvel utilisateur dans la base de données
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                    conn.commit()
                    client_socket.send("register_ok".encode())
                except sqlite3.IntegrityError:
                    client_socket.send("register_failed".encode())
                conn.close()

            else:  # Traitement des positions
                x, y = map(int, data.split(','))
                clients[addr]['x'] = x
                clients[addr]['y'] = y
                print(f"Position du joueur {addr} : ({x}, {y})")

                # Retransmettre la position aux autres clients
                for other_addr, other_client in clients.items():
                    if other_addr != addr:
                        try:
                            other_client['socket'].send(f"{addr}:{x},{y}".encode())
                        except:
                            print(f"[ERREUR] Envoi de données à {other_addr} a échoué.")

        except:
            break

    del clients[addr]
    client_socket.close()
    print(f"[DÉCONNEXION] {addr} déconnecté.")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 12345))
server_socket.listen(5)
print("[DÉMARRAGE] Le serveur est en attente de connexions...")

while True:
    client_socket, addr = server_socket.accept()
    client_thread = threading.Thread(target=gérer_client, args=(client_socket, addr))
    client_thread.start()