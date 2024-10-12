from flask import Flask, request, jsonify
from database import get_db
from managers.server_manager import add_server, update_server, delete_server, get_all_servers
from modules.ping_supervisor import supervise_ping
from modules.http_supervisor import supervise_http
from modules.snmp_supervisor import supervise_snmp
import models.server_model as models

app = Flask(__name__)

# Créer les tables à partir des modèles au démarrage
with app.app_context():
    db = next(get_db())  # Utiliser next() pour obtenir la session DB depuis le générateur
    try:
        models.Base.metadata.create_all(bind=db.bind)  # Créer les tables en utilisant la session de base de données
    finally:
        db.close()  # Fermer la session proprement

# Route pour ajouter un serveur
@app.route("/add_server", methods=["POST"])
def create_server():
    data = request.get_json()
    db = next(get_db())
    try:
        new_server = add_server(data['name'], data['ip_address'], data['service_type'], db)
        return jsonify(new_server)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

# Route pour mettre à jour un serveur
@app.route("/update_server/<int:server_id>", methods=["PUT"])
def modify_server(server_id):
    data = request.get_json()
    db = next(get_db())
    try:
        updated_server = update_server(server_id, data['name'], data['ip_address'], data['service_type'], db)
        return jsonify(updated_server)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

# Route pour supprimer un serveur
@app.route("/delete_server/<int:server_id>", methods=["DELETE"])
def remove_server(server_id):
    db = next(get_db())
    try:
        delete_server(server_id, db)
        return jsonify({"message": "Serveur supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

# Route pour obtenir la liste des serveurs
@app.route("/servers", methods=["GET"])
def list_servers():
    db = next(get_db())
    try:
        servers = get_all_servers(db)
        return jsonify(servers)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

@app.route("/supervise/<int:server_id>", methods=["POST"])
def supervise_server(server_id):
    db = next(get_db())
    server = db.query(models.Server).filter(models.Server.id == server_id).first()
    if not server:
        db.close()
        return jsonify({"error": "Serveur non trouvé"}), 404

    try:
        if server.service_type == 'ping':
            result = supervise_ping(server, db)
        elif server.service_type == 'http':
            result = supervise_http(server, db)
        elif server.service_type == 'snmp':
            result = supervise_snmp(server, db)
        else:
            return jsonify({"error": "Type de service non pris en charge"}), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
