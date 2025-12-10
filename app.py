import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
#from data_processor import sync_activity_to_notion # NOUVEL IMPORT

load_dotenv()
app = Flask(__name__)

STRAVA_VERIFY_TOKEN = os.getenv("STRAVA_VERIFY_TOKEN")

# --- ROUTE 1 : VALIDATION DE L'ABONNEMENT (GET) ---

@app.route("/webhook/strava", methods=["GET"])
def strava_webhook_validation():
    """ Gère le processus d'abonnement de Strava. """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == STRAVA_VERIFY_TOKEN:
        print("✅ Validation du Webhook réussie. Envoi du challenge...")
        return jsonify({"hub.challenge": challenge}), 200
    else:
        print("❌ Validation du Webhook échouée : Token ou mode invalide.")
        return "Forbidden", 403

# --- ROUTE 2 : RÉCEPTION DES ÉVÉNEMENTS (POST) ---

@app.route("/webhook/strava", methods=["POST"])
def strava_webhook_handler():
    """ Gère la réception de la notification d'une nouvelle activité. """
    try:
        data = request.json
        object_type = data.get('object_type')
        aspect_type = data.get('aspect_type')
        activity_id = data.get('object_id')

        print("\n--- ÉVÉNEMENT WEBHOOK POST REÇU ---")
        print(f"Type: {object_type}, Événement: {aspect_type}, ID: {activity_id}")
        
        if object_type == 'activity':
            if aspect_type == 'create' or aspect_type == 'update':
                # Appel du processeur pour sync Strava -> Notion
                sync_activity_to_notion(activity_id, is_update=(aspect_type == 'update'))
            
            elif aspect_type == 'delete':
                print(f"🗑️ Événement 'delete' ignoré pour l'activité {activity_id}.")

        return "ACTIVITY RECEIVED", 200

    except Exception as e:
        print(f"❌ Erreur interne lors du traitement du webhook: {e}")
        return "Internal Error", 200 

if __name__ == "__main__":
    app.run(port=8000, debug=True)