import sqlite3

# Connexion à la base de données (ou création si elle n'existe pas)
conn = sqlite3.connect('db/users.db')

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

# Fermer la connexion
conn.close()

print("Base de données créée avec succès !")