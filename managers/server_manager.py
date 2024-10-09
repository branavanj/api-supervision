from sqlalchemy.orm import Session
from models.server_model import Server
from fastapi import HTTPException

# Fonction pour ajouter un serveur
def add_server(name: str, ip_address: str, service_type: str, db: Session):
    # Vérifier si le serveur existe déjà
    existing_server = db.query(Server).filter(Server.ip_address == ip_address).first()
    if existing_server:
        raise HTTPException(status_code=400, detail="Le serveur existe déjà avec cette adresse IP")
    
    # Créer un nouveau serveur
    new_server = Server(name=name, ip_address=ip_address, service_type=service_type)
    db.add(new_server)
    db.commit()
    db.refresh(new_server)
    return new_server

# Fonction pour mettre à jour un serveur
def update_server(server_id: int, name: str, ip_address: str, service_type: str, db: Session):
    # Rechercher le serveur à mettre à jour
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Serveur non trouvé")
    
    # Mise à jour des informations du serveur
    server.name = name
    server.ip_address = ip_address
    server.service_type = service_type
    db.commit()
    db.refresh(server)
    return server

# Fonction pour supprimer un serveur
def delete_server(server_id: int, db: Session):
    # Rechercher le serveur à supprimer
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Serveur non trouvé")
    
    # Supprimer le serveur
    db.delete(server)
    db.commit()
    return {"message": "Serveur supprimé avec succès"}

# Fonction pour obtenir la liste des serveurs
def get_all_servers(db: Session):
    return db.query(Server).all()
