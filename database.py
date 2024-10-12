from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Charger l'URL de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Créer l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

# Fonction pour obtenir la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
