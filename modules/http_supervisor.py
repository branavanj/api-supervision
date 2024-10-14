import requests
from sqlalchemy.orm import Session
from models.server_model import Server
from datetime import datetime

# Fonction de supervision HTTP
def supervise_http(server: Server, db: Session):
    try:
        # Effectuer une requête GET vers le serveur
        response = requests.get(f"http://{server.ip_address}", timeout=5)

        # Vérifier le statut de la réponse
        if response.status_code == 200:
            status = "Up"
            response_data = f"HTTP Status Code: {response.status_code} - OK"
        else:
            status = "Down"
            response_data = f"HTTP Status Code: {response.status_code} - {response.reason}"

    except requests.exceptions.RequestException as e:
        # En cas d'erreur de connexion, marquer comme "Down"
        status = "Down"
        response_data = f"Erreur de connexion HTTP : {str(e)}"

    # Créer le dictionnaire de résultat
    supervision_result = {
        "server_id": server.id,
        "status": status,
        "response_data": response_data,
        "timestamp": datetime.now().isoformat()
    }

    # Retourner les données de supervision sous forme de dictionnaire
    return supervision_result
