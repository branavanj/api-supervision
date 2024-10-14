from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Server(Base):
    __tablename__ = "servers"

    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)

    # Nom du serveur
    name = Column(String(255), nullable=False)

    # Adresse IP du serveur
    ip_address = Column(String(45), nullable=False)

    # Date et heure de la création
    created_at = Column(DateTime, default=datetime.now)

    # Relation avec la table 'services'
    services = relationship("Service", back_populates="server", cascade="all, delete-orphan")
