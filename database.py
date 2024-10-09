from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


# Récupérer l'URL de la base de données à partir des variables d'environnement
DATABASE_URL = "mysql+pymysql://root:9559@localhost/supervision"

if DATABASE_URL is None:
    raise ValueError("La variable DATABASE_URL est introuvable. Assurez-vous que le fichier .env est bien configuré.")

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour la déclaration des modèles
Base = declarative_base()

# Gestion de la session de base de données pour chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
