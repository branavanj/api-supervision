import ping3
from sqlalchemy.orm import Session
from models.server_model import Server
from datetime import datetime
import json
import os

# Chemin du fichier local pour enregistrer les résultats de supervision
SUPERVISION_FILE_PATH = "supervision_results.json"

# Fonction de supervision par Ping
def supervise_ping(server: Server, db: Session):
    try:
        # Effectuer le ping vers l'adresse IP spécifiée
        latency = ping3.ping(server.ip_address, timeout=5)

        # Vérifier si le ping a réussi ou non
        if latency is not None:
            status = "Up"
            response_data = f"Latency: {latency:.2f} ms"
        else:
            status = "Down"
            response_data = "Impossible de joindre l’hôte de destination"
            latency = None

    except Exception as e:
        # En cas d'exception, marquer le serveur comme "Down" et enregistrer l'erreur
        status = "Down"
        response_data = f"Erreur lors de la supervision par ping : {str(e)}"
        latency = None

    # Créer le dictionnaire de résultat
    supervision_result = {
        "server_id": server.id,
        "status": status,
        "response_data": response_data,
        "timestamp": datetime.now().isoformat()
    }

    # Ajouter la latence seulement si le serveur est "Up"
    if latency is not None:
        supervision_result["latency"] = round(latency, 2)

    # Enregistrer le résultat dans le fichier local JSON
    try:
        # Lire les résultats existants s'ils existent
        if os.path.exists(SUPERVISION_FILE_PATH):
            with open(SUPERVISION_FILE_PATH, "r") as file:
                data = json.load(file)
        else:
            data = []

        # Ajouter le nouveau résultat de supervision
        data.append(supervision_result)

        # Écrire les résultats dans le fichier JSON
        with open(SUPERVISION_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

    except Exception as file_error:
        raise Exception(f"Erreur lors de l'enregistrement du résultat dans le fichier local : {str(file_error)}")

    # Retourner les données de supervision sous forme de dictionnaire
    return supervision_result
