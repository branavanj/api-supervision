import requests
from sqlalchemy.orm import Session
from models.supervision_results_model import SupervisionResult
from models.server_model import Server
from datetime import datetime

# Fonction de supervision HTTP
def supervise_http(server: Server, db: Session):
    try:
        # Envoyer une requête HTTP GET vers l'adresse spécifiée par le serveur
        response = requests.get(server.ip_address, timeout=5)

        # Si le code de statut est 200, le serveur est considéré comme "Up"
        status = "Up" if response.status_code == 200 else "Down"
        response_data = f"HTTP Status Code: {response.status_code}"

    except requests.RequestException as e:
        # En cas d'exception, marquer le serveur comme "Down" et enregistrer l'erreur
        status = "Down"
        response_data = str(e)
        latency = None
    else:
        # Mesurer la latence en millisecondes
        latency = response.elapsed.total_seconds() * 1000  # Convertir en millisecondes

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

    # Retourner le résultat de la supervision
    return {
        "server_id": server.id,
        "status": status,
        "latency": latency,
        "response_data": response_data,
        "timestamp": supervision_result.timestamp
    }
