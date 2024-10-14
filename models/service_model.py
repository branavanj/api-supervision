from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Service(Base):
    __tablename__ = "services"

    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)

    # Clé étrangère vers la table 'servers'
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)

    # Type de service (ping, http, snmp, etc.)
    service_type = Column(String(50), nullable=False)

    # Date et heure de la création
    created_at = Column(DateTime, default=datetime.now)

    # Relation avec la table 'servers'
    server = relationship("Server", back_populates="services")
