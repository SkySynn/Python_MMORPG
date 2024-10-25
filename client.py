import pygame
import socket
import select

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

# Couleurs
blanc = (255, 255, 255)
noir = (0, 0, 0)
gris = (128, 128, 128)
vert = (0, 255, 0)
rouge = (255, 0, 0)

# Police de caractères
font = pygame.font.Font(None, 30)

# Fonction pour afficher du texte
def afficher_texte(texte, couleur, x, y):
    surface = font.render(texte, True, couleur)
    screen.blit(surface, (x, y))

# Classe pour les zones de texte
class TextBox:
    def __init__(self, x, y, largeur, hauteur):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.actif = False
        self.texte = ""
        self.couleur_inactive = gris
        self.couleur_active = blanc

    def gérer_événements(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.actif = not self.actif
            else:
                self.actif = False
        if event.type == pygame.KEYDOWN:
            if self.actif:
                if event.key == pygame.K_BACKSPACE:
                    self.texte = self.texte[:-1]
                elif event.key == pygame.K_RETURN:
                    # Ignorer la touche Entrée pour éviter de valider la connexion
                    pass
                else:
                    # Convertir la touche en caractère et l'ajouter au texte
                    self.texte += event.unicode

    def afficher(self):
        couleur = self.couleur_active if self.actif else self.couleur_inactive
        pygame.draw.rect(screen, couleur, self.rect, 2)
        surface = font.render(self.texte, True, noir)
        screen.blit(surface, (self.rect.x + 5, self.rect.y + 5))

# Créer les zones de texte
username_box = TextBox(300, 200, 200, 30)
password_box = TextBox(300, 250, 200, 30)

# Position initiale du joueur
x, y = 100, 100
vitesse = 5

# Création du socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 12345))  # Remplacez 'localhost' par l'adresse IP du serveur si besoin

# Dictionnaire pour stocker les positions des autres joueurs
autres_joueurs = {}

# Horloge pour limiter le nombre d'images par seconde
clock = pygame.time.Clock()
fps = 60

# Fonctions pour le login et l'inscription
def login(username, password):
    client_socket.send(f"login {username} {password}".encode())
    reponse = client_socket.recv(1024).decode()
    if reponse == "login_ok":
        print("Connexion réussie !")
        return True
    else:
        print("Échec de la connexion.")
        return False

def register(username, password):
    client_socket.send(f"register {username} {password}".encode())
    reponse = client_socket.recv(1024).decode()
    if reponse == "register_ok":
        print("Inscription réussie !")
        return True
    else:
        print("Échec de l'inscription.")
        return False

# Activer la saisie de texte
pygame.key.start_text_input()

# Boucle principale
running = True
logged_in = False  # Variable pour savoir si le joueur est connecté
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        username_box.gérer_événements(event)
        password_box.gérer_événements(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not logged_in:  # Appuyer sur Entrée pour se connecter
                logged_in = login(username_box.texte, password_box.texte)

    # Appel de pygame.event.pump() pour traiter les événements de saisie
    pygame.event.pump()

    # Efface l'écran
    screen.fill((0, 0, 0))

    # Afficher les zones de texte et les labels
    if not logged_in:
        username_box.afficher()
        password_box.afficher()
        afficher_texte("Nom d'utilisateur:", blanc, 150, 205)
        afficher_texte("Mot de passe:", blanc, 150, 255)

        # Afficher les boutons (simplifiés pour l'instant)
        afficher_texte("Connexion (appuyez sur Entrée)", blanc, 250, 300)
        afficher_texte("Inscription (non implémentée)", gris, 250, 350)  # Inscription non implémentée pour l'instant

    # Si le joueur est connecté, afficher le jeu
    if logged_in:
        # Gestion des touches ZQSD
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:  # Z - Haut
            y -= vitesse
        if keys[pygame.K_s]:  # S - Bas
            y += vitesse
        if keys[pygame.K_q]:  # Q - Gauche
            x -= vitesse
        if keys[pygame.K_d]:  # D - Droite
            x += vitesse

        # Envoi de la position au serveur
        data = f"{x},{y}".encode()
        try:
            client_socket.send(data)
        except:
            print("[ERREUR] Envoi de données au serveur a échoué.")

        # Utiliser select pour vérifier si des données sont disponibles
        ready_to_read, _, _ = select.select([client_socket], [], [], 0)
        if ready_to_read:
            try:
                data = client_socket.recv(1024).decode()
                if data:
                    # Séparer l'adresse de l'autre joueur de sa position
                    addr, pos = data.split(':')
                    x_autre, y_autre = map(int, pos.split(','))
                    autres_joueurs[addr] = (x_autre, y_autre)
            except:
                print("[ERREUR] Réception de données du serveur a échoué.")

        # Dessiner les autres joueurs
        for addr, (x_autre, y_autre) in autres_joueurs.items():
            joueur_autre = pygame.Rect(x_autre, y_autre, 30, 30)
            pygame.draw.rect(screen, vert, joueur_autre)  # Couleur verte pour les autres joueurs

        # Dessine le carré du joueur
        joueur = pygame.Rect(x, y, 30, 30)
        pygame.draw.rect(screen, rouge, joueur)

    # Mettre à jour l'affichage
    pygame.display.flip()

    # Limiter le nombre d'images par seconde
    clock.tick(fps)

pygame.quit()