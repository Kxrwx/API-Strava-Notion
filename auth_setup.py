import os
import requests
import urllib.parse
from dotenv import load_dotenv
import webbrowser
import http.server
import socketserver

load_dotenv()

print(f"DEBUG: CLIENT_ID chargé: {os.getenv('STRAVA_CLIENT_ID')}")

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_CONFIG_DB_ID = os.getenv("NOTION_CONFIG_DB_ID")

REDIRECT_URI = "http://localhost:8000/strava_auth_callback"
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
SCOPE = "activity:read_all,profile:read_all"

def save_token_to_notion(key, value):
    """Sauvegarde ou met à jour la clé/valeur (le refresh token) dans la DB Notion 'Config'."""
    print(f"\nTentative d'enregistrement de la clé '{key}' dans Notion...")
    
    search_url = f"https://api.notion.com/v1/databases/{NOTION_CONFIG_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    filter_payload = {
        "filter": {
            "property": "Key",
            "title": {
                "equals": key
            }
        }
    }
    
    search_response = requests.post(search_url, headers=headers, json=filter_payload)
    results = search_response.json().get("results", [])
    
    properties_payload = {
        "Key": {"title": [{"text": {"content": key}}]},
        "Value": {"rich_text": [{"text": {"content": value}}]}
    }
    
    if results:
        # MISE À JOUR
        page_id = results[0]["id"]
        update_url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.patch(update_url, headers=headers, json={"properties": properties_payload})
        if response.status_code == 200:
            print(f"✅ Token '{key}' mis à jour avec succès dans Notion (page ID: {page_id}).")
        else:
            print(f"❌ Erreur lors de la mise à jour : {response.text}")
            
    else:
        # CRÉATION
        create_url = "https://api.notion.com/v1/pages"
        create_payload = {
            "parent": {"database_id": NOTION_CONFIG_DB_ID},
            "properties": properties_payload
        }
        response = requests.post(create_url, headers=headers, json=create_payload)
        if response.status_code == 200:
            print(f"✅ Token '{key}' créé avec succès dans Notion.")
        else:
            print(f"❌ Erreur lors de la création : {response.text}")


class StravaCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Gère la réponse de Strava après l'autorisation."""
    
    def do_GET(self):
        if self.path.startswith("/strava_auth_callback"):
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code = query_components.get('code', [None])[0]

            if code:
                payload = {
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'code': code,
                    'grant_type': 'authorization_code'
                }

                token_response = requests.post(STRAVA_TOKEN_URL, data=payload)
                token_data = token_response.json()

                if 'refresh_token' in token_data:
                    refresh_token = token_data['refresh_token']
                    print("\n--- AUTHENTIFICATION RÉUSSIE ---")
                    save_token_to_notion("strava_refresh_token", refresh_token)

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Authentification Strava reussie !</h1><p>Le refresh token a ete stocke dans Notion. Vous pouvez fermer cette fenetre.</p></body></html>")
                    self.server.shutdown()
                else:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Erreur lors de l'echange du code contre les tokens.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Code d'autorisation manquant.")


if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET or not NOTION_API_KEY or not NOTION_CONFIG_DB_ID:
        print("Erreur: Veuillez vérifier les variables dans .env.")
    else:
        auth_params = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'scope': SCOPE,
            'approval_prompt': 'force'
        }
        auth_url = f"{STRAVA_AUTH_URL}?{urllib.parse.urlencode(auth_params)}"

        print("--- ÉTAPE 1 : Autorisation Strava ---")
        webbrowser.open(auth_url)

        PORT = 8000
        with socketserver.TCPServer(("", PORT), StravaCallbackHandler) as httpd:
            print(f"\n--- ÉTAPE 2 : Attente du Callback sur port {PORT} ---")
            httpd.serve_forever()
        
        print("\n--- FIN DU PROCESSUS D'AUTHENTIFICATION INITIALE ---")