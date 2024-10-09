from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from managers.server_manager import add_server, update_server, delete_server, get_all_servers
from modules.ping_supervisor import supervise_ping
from modules.http_supervisor import supervise_http
from modules.snmp_supervisor import supervise_snmp
import models.server_model as models
import asyncio

# Créer une instance de FastAPI
app = FastAPI()

# Créer les tables à partir des modèles
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=get_db().bind)

# Route pour ajouter un serveur
@app.post("/add_server")
def create_server(name: str, ip_address: str, service_type: str, db: Session = Depends(get_db)):
    try:
        return add_server(name, ip_address, service_type, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route pour mettre à jour un serveur
@app.put("/update_server/{server_id}")
def modify_server(server_id: int, name: str, ip_address: str, service_type: str, db: Session = Depends(get_db)):
    try:
        return update_server(server_id, name, ip_address, service_type, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route pour supprimer un serveur
@app.delete("/delete_server/{server_id}")
def remove_server(server_id: int, db: Session = Depends(get_db)):
    try:
        return delete_server(server_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route pour obtenir la liste des serveurs
@app.get("/servers")
def list_servers(db: Session = Depends(get_db)):
    try:
        return get_all_servers(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Route pour superviser un serveur
@app.post("/supervise/{server_id}")
def supervise_server(server_id: int, db: Session = Depends(get_db)):
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Serveur non trouvé")
    
    if server.service_type == 'ping':
        return supervise_ping(server, db)
    elif server.service_type == 'http':
        return supervise_http(server, db)
    elif server.service_type == 'snmp':
        return supervise_snmp(server, db)
    else:
        raise HTTPException(status_code=400, detail="Type de service non pris en charge")

# Fonction de supervision automatique des serveurs
async def automatic_supervision():
    while True:
        db = next(get_db())
        servers = db.query(models.Server).all()
        for server in servers:
            if server.service_type == 'ping':
                supervise_ping(server, db)
            elif server.service_type == 'http':
                supervise_http(server, db)
            elif server.service_type == 'snmp':
                supervise_snmp(server, db)
        await asyncio.sleep(60)  # Supervision toutes les 60 secondes

# Lancer la supervision automatique lors du démarrage de l'application
@app.on_event("startup")
async def startup_supervision():
    asyncio.create_task(automatic_supervision())

# Lancer le serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)