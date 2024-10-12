import ping3
from sqlalchemy.orm import Session
from models.supervision_results_model import SupervisionResult
from models.server_model import Server
from datetime import datetime

# Fonction de supervision par Ping
def supervise_ping(server: Server, db: Session):
    try:
        # Effectuer le ping vers l'adresse IP spécifiée
        latency = ping3.ping(server.ip_address, timeout=5)

        # Vérifier si le ping a réussi ou non
        if latency is not None:
            status = "Up"
            response_data = f"Latency: {latency} ms"
        else:
            status = "Down"
            response_data = "Impossible de joindre l’hôte de destination"
    except Exception as e:
        # En cas d'exception, marquer le serveur comme "Down" et enregistrer l'erreur
        latency = None
        status = "Down"
        response_data = str(e)

    # Enregistrer le résultat de la supervision dans la base de données
    supervision_result = SupervisionResult(
        server_id=server.id,
        status=status,
        latency=latency,
        response_data=response_data,
        timestamp=datetime.now()
    )
    db.add(supervision_result)
    db.commit()
    db.refresh(supervision_result)

    # Retourner les données de supervision sous forme de dictionnaire
    return {
        "server_id": supervision_result.server_id,
        "status": supervision_result.status,
        "latency": supervision_result.latency,
        "response_data": supervision_result.response_data,
        "timestamp": supervision_result.timestamp.isoformat()
    }
