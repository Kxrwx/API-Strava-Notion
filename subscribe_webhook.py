import os
import requests
from dotenv import load_dotenv

load_dotenv()

# --- AJOUTEZ CES LIGNES DE TEST ---
print(f"DEBUG: ID: {os.getenv('STRAVA_CLIENT_ID')}")
print(f"DEBUG: Secret: {os.getenv('STRAVA_CLIENT_SECRET')[:5]}...") # Affiche les 5 premiers caractères
print(f"DEBUG: Verify Token: {os.getenv('STRAVA_VERIFY_TOKEN')}")
# --- FIN DE L'AJOUT ---

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
VERIFY_TOKEN = os.getenv("STRAVA_VERIFY_TOKEN")

# ... le reste du code

STRAVA_SUBSCRIPTION_URL = "https://api.strava.com/api/v3/push_subscriptions"

def register_webhook():
    """ Crée un nouvel abonnement Webhook Strava via l'API. """
    
    # L'utilisateur DOIT saisir l'URL ngrok + le chemin /webhook/strava
    callback_url = input("Veuillez entrer l'URL publique complète de ngrok (ex: https://XXXXX.ngrok-free.app/webhook/strava) : ")
    
    if not callback_url.startswith("https://") or not callback_url.endswith("/webhook/strava"):
        print("❌ Erreur : L'URL doit commencer par 'https://' et se terminer par '/webhook/strava'.")
        return

    print("\n--- TENTATIVE D'ENREGISTREMENT DU WEBHOOK ---")
    
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'callback_url': callback_url,
        'verify_token': VERIFY_TOKEN
    }

    try:
        response = requests.post(STRAVA_SUBSCRIPTION_URL, data=payload)
        
        if response.status_code == 201:
            print("\n✅ Succès : Le webhook a été créé avec succès !")
            print(f"ID de l'abonnement créé : {response.json().get('id')}")
        elif response.status_code == 400:
            print(f"\n❌ Échec : Vérifiez les tokens. Réponse de Strava: {response.json()}")
        else:
            print(f"\n❌ Échec de la création. Statut HTTP : {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion : {e}")

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET or not VERIFY_TOKEN:
        print("Erreur : Veuillez définir CLIENT_ID, CLIENT_SECRET et STRAVA_VERIFY_TOKEN dans votre fichier .env.")
    else:
        register_webhook()