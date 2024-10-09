from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ip_address = Column(String(255), unique=True, nullable=False)
    service_type = Column(Enum('ping', 'http', 'snmp', name='service_types'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())