import sqlite3
import os

try:
    # Connexion à la base de données (ou création si elle n'existe pas)
    conn = sqlite3.connect('server/db/users.db')

    # Création d'un curseur
    cursor = conn.cursor()

    # Création de la table "users"
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # Valider les modifications
    conn.commit()

    conn.close()
    print("Opérations sur la base de données terminées avec succès !")

except sqlite3.OperationalError as e:
    print(f"Erreur d'accès à la base de données : {e}")
    print(f"Répertoire de travail actuel : {os.getcwd()}")