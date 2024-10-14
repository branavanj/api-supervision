from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from database import get_db
from models.server_model import Server
from models.service_model import Service
import logging
from datetime import datetime
from modules.ping_supervisor import supervise_ping
from modules.http_supervisor import supervise_http
from modules.snmp_supervisor import supervise_snmp

app = Flask(__name__)

# Configuration des logs
logging.basicConfig(filename='supervision.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fonction pour ajouter un serveur
def add_server(name, ip_address, service_types, db):
    try:
        # Créer un nouveau serveur
        new_server = Server(name=name, ip_address=ip_address)
        db.add(new_server)
        db.commit()
        db.refresh(new_server)

        # Vérifier si service_types est une liste ou une simple chaîne de caractères
        if isinstance(service_types, str):
            service_types = [service_types]  # Convertir en liste si c'est une chaîne unique

        # Ajouter des services associés au serveur
        for service_type in service_types:
            new_service = Service(service_type=service_type, server_id=new_server.id)
            db.add(new_service)
        db.commit()

        logging.info(f"Serveur ajouté avec succès - ID: {new_server.id}, Nom: {new_server.name}")
        return {
            "id": new_server.id,
            "name": new_server.name,
            "ip_address": new_server.ip_address,
            "services": service_types
        }
    except Exception as e:
        db.rollback()
        logging.error(f"Erreur lors de l'ajout du serveur : {str(e)}")
        raise Exception(f"Erreur lors de l'ajout du serveur : {str(e)}")

# Fonction pour mettre à jour un serveur
def update_server(server_id, name, ip_address, service_types, db):
    try:
        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            raise ValueError("Serveur non trouvé")

        # Mise à jour des informations du serveur
        server.name = name
        server.ip_address = ip_address
        db.commit()

        # Vérifier si service_types est une liste ou une simple chaîne de caractères
        if isinstance(service_types, str):
            service_types = [service_types]  # Convertir en liste si c'est une chaîne unique

        # Supprimer les anciens services et ajouter les nouveaux
        db.query(Service).filter(Service.server_id == server_id).delete()
        for service_type in service_types:
            new_service = Service(service_type=service_type, server_id=server.id)
            db.add(new_service)
        db.commit()

        logging.info(f"Serveur mis à jour avec succès - ID: {server.id}, Nom: {server.name}")
        return {
            "id": server.id,
            "name": server.name,
            "ip_address": server.ip_address,
            "services": service_types
        }
    except Exception as e:
        db.rollback()
        logging.error(f"Erreur lors de la mise à jour du serveur {server_id} : {str(e)}")
        raise Exception(f"Erreur lors de la mise à jour du serveur : {str(e)}")

# Route pour ajouter un serveur
@app.route("/add_server", methods=["POST"])
def add_server(name, ip_address, service_types, db):
    try:
        # Vérifier si l'adresse IP existe déjà
        existing_server = db.query(Server).filter(Server.ip_address == ip_address).first()
        if existing_server:
            raise ValueError(f"L'adresse IP {ip_address} est déjà utilisée par un autre serveur.")

        # Créer un nouveau serveur
        new_server = Server(name=name, ip_address=ip_address)
        db.add(new_server)
        db.commit()
        db.refresh(new_server)

        # Vérifier si service_types est une liste ou une simple chaîne de caractères
        if isinstance(service_types, str):
            service_types = [service_types]  # Convertir en liste si c'est une chaîne unique

        # Ajouter des services associés au serveur
        for service_type in service_types:
            new_service = Service(service_type=service_type, server_id=new_server.id)
            db.add(new_service)
        db.commit()

        logging.info(f"Serveur ajouté avec succès - ID: {new_server.id}, Nom: {new_server.name}")
        return {
            "id": new_server.id,
            "name": new_server.name,
            "ip_address": new_server.ip_address,
            "services": service_types
        }
    except Exception as e:
        db.rollback()
        logging.error(f"Erreur lors de l'ajout du serveur : {str(e)}")
        raise Exception(f"Erreur lors de l'ajout du serveur : {str(e)}")


# Route pour mettre à jour un serveur
@app.route("/update_server/<int:server_id>", methods=["PUT"])
def modify_server(server_id):
    data = request.get_json()
    required_keys = ["name", "ip_address", "service_types"]

    # Vérifier que les clés requises sont présentes dans la requête
    for key in required_keys:
        if key not in data:
            return jsonify({"error": f"Le champ '{key}' est requis"}), 400

    with get_db() as db:
        try:
            updated_server = update_server(server_id, data['name'], data['ip_address'], data['service_types'], db)
            return jsonify(updated_server), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

# Route pour superviser tous les services d'un serveur
@app.route("/supervise/<int:server_id>", methods=["POST"])
def supervise_all_services(server_id):
    with get_db() as db:
        server = db.query(Server).filter(Server.id == server_id).first()

        if not server:
            return jsonify({"error": "Serveur non trouvé"}), 404

        # Récupérer tous les services associés au serveur
        services = db.query(Service).filter(Service.server_id == server.id).all()

        results = []

        try:
            for service in services:
                if service.service_type == 'ping':
                    result = supervise_ping(server, db)
                elif service.service_type == 'http':
                    result = supervise_http(server, db)
                elif service.service_type == 'snmp':
                    result = supervise_snmp(server, db)
                else:
                    result = {"error": f"Type de service non pris en charge: {service.service_type}"}

                # Ajouter le résultat à la liste des résultats
                results.append({
                    "service_type": service.service_type,
                    "result": result
                })

                # Logger les résultats pour chaque service supervisé
                logging.info(f"Supervision - Serveur ID {server.id}, Service: {service.service_type} - {result}")

            return jsonify(results), 200

        except Exception as e:
            logging.error(f"Erreur lors de la supervision du serveur {server_id}: {str(e)}")
            return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
