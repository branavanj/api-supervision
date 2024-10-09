from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class SupervisionResult(Base):
    __tablename__ = "supervision_results"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    status = Column(String(50), nullable=False)
    latency = Column(Float, nullable=True)
    response_data = Column(String, nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())

    # Relation avec le modèle Server
    server = relationship("Server")