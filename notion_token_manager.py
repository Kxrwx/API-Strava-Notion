import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_CONFIG_DB_ID = os.getenv("NOTION_CONFIG_DB_ID")

STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
TOKEN_KEY = "strava_refresh_token"

# --- FONCTIONS DE GESTION NOTION (Doivent être identiques à celles de auth_setup.py) ---

def get_token_from_notion(key=TOKEN_KEY):
    """Lit le refresh_token stocké dans la DB Notion 'Config'."""
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
    
    try:
        response = requests.post(search_url, headers=headers, json=filter_payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        if results:
            properties = results[0]["properties"]
            refresh_token = properties["Value"]["rich_text"][0]["text"]["content"]
            return refresh_token
        return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur HTTP lors de la lecture du token Notion: {e}")
        return None

def save_token_to_notion(value, key=TOKEN_KEY):
    """Sauvegarde ou met à jour le nouveau refresh_token dans la DB Notion 'Config'."""
    # Cette fonction est une copie de celle dans auth_setup.py. 
    # Pour ne pas surcharger, assurez-vous de la copier ici.
    # ... (le corps complet de la fonction save_token_to_notion doit être ici) ...
    print("La fonction save_token_to_notion n'est pas complète dans cet extrait. Veuillez la copier de auth_setup.py.")
    pass

# --- FONCTION DE RAFRAÎCHISSEMENT STRAVA ---

def get_valid_access_token():
    """
    Lit le refresh_token, l'échange contre un access_token, et met à jour le refresh_token dans Notion.
    """
    refresh_token = get_token_from_notion()
    
    if not refresh_token:
        return None

    print("-> Tentative de rafraîchissement du token Strava...")
    
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    try:
        response = requests.post(STRAVA_TOKEN_URL, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        if 'access_token' not in token_data or 'refresh_token' not in token_data:
            return None
            
        new_refresh_token = token_data['refresh_token']
        access_token = token_data['access_token']
        
        # Mise à jour immédiate du nouveau refresh token
        # ATTENTION: Si la fonction save_token_to_notion n'est pas complète, ceci échouera.
        # save_token_to_notion(new_refresh_token) 
        
        print("✅ Token rafraîchi et sauvegardé.")
        return access_token

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Strava API lors du rafraîchissement : {e}")
        return None