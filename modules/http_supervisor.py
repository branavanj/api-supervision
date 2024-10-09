import requests
from sqlalchemy.orm import Session
from models.supervision_results_model import SupervisionResult
from models.server_model import Server
from datetime import datetime

# Fonction de supervision HTTP
def supervise_http(server: Server, db: Session):
    try:
        response = requests.get(server.ip_address, timeout=5)
        status = "Up" if response.status_code == 200 else "Down"
        response_data = f"HTTP Status Code: {response.status_code}"
    except Exception as e:
        status = "Down"
        response_data = str(e)
        latency = None
    else:
        latency = response.elapsed.total_seconds() * 1000  # Convertir en millisecondes

    # Enregistrer le résultat de la supervision
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
    return supervision_result