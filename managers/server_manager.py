from sqlalchemy.orm import Session
from models.server_model import Server
from fastapi import HTTPException

# Fonction pour ajouter un serveur
def add_server(name: str, ip_address: str, service_type: str, db: Session):
    existing_server = db.query(Server).filter(Server.ip_address == ip_address).first()
    if existing_server:
        raise Exception("Le serveur existe déjà avec cette adresse IP")
    
    new_server = Server(name=name, ip_address=ip_address, service_type=service_type)
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    return {
        "id": new_server.id,
        "name": new_server.name,
        "ip_address": new_server.ip_address,
        "service_type": new_server.service_type
    }

# Fonction pour mettre à jour un serveur
def update_server(server_id: int, name: str, ip_address: str, service_type: str, db: Session):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise Exception("Serveur non trouvé")

    server.name = name
    server.ip_address = ip_address
    server.service_type = service_type
    db.commit()
    db.refresh(server)
    return {
        "id": server.id,
        "name": server.name,
        "ip_address": server.ip_address,
        "service_type": server.service_type
    }

# Fonction pour supprimer un serveur
def delete_server(server_id: int, db: Session):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise Exception("Serveur non trouvé")

    db.delete(server)
    db.commit()

# Fonction pour obtenir la liste des serveurs
def get_all_servers(db: Session):
    servers = db.query(Server).all()
    return [
        {
            "id": server.id,
            "name": server.name,
            "ip_address": server.ip_address,
            "service_type": server.service_type
        } for server in servers
    ]
