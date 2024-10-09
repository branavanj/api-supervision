import ping3
from sqlalchemy.orm import Session
from models.supervision_results_model import SupervisionResult
from models.server_model import Server
from datetime import datetime

# Fonction de supervision par Ping
def supervise_ping(server: Server, db: Session):
    try:
        latency = ping3.ping(server.ip_address)
        status = "Up" if latency is not None else "Down"
    except Exception as e:
        latency = None
        status = "Down"
        response_data = str(e)
    else:
        response_data = None

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
