import requests
from notion_token_manager import get_valid_access_token 
import os
from dotenv import load_dotenv

load_dotenv()
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

STRAVA_API_URL = "https://www.strava.com/api/v3"

def clean_data(activity_data):
    """ Nettoie et convertit les données brutes de Strava. """
    
    distance_km = activity_data.get('distance', 0) / 1000
    moving_time_minutes = activity_data.get('moving_time', 0) / 60
    
    start_date_local = activity_data.get('start_date_local')
    date_part = start_date_local[:10]
    name_part = activity_data.get('name', 'Activité sans nom')
    title = f"{date_part} - {name_part}"

    return {
        "Activity ID": activity_data.get('id'),
        "Name": title,
        "Date": start_date_local,
        "Type": activity_data.get('type', 'Inconnu'),
        "Distance (km)": round(distance_km, 2),
        "Durée (min)": round(moving_time_minutes, 1),
        "D+ (m)": activity_data.get('total_elevation_gain', 0),
        "Calories": activity_data.get('calories', 0)
    }

def format_for_notion(cleaned_data):
    """ Convertit les données nettoyées en un payload JSON compatible avec l'API Notion. """
    properties = {
        "Name": {"title": [{"text": {"content": cleaned_data['Name']}}]},
        "Activity ID": {"number": cleaned_data['Activity ID']},
        "Distance (km)": {"number": cleaned_data['Distance (km)']},
        "Durée (min)": {"number": cleaned_data['Durée (min)']},
        "D+ (m)": {"number": cleaned_data['D+ (m)']},
        "Calories": {"number": cleaned_data['Calories']},
        "Date": {"date": {"start": cleaned_data['Date']}},
        "Type": {"select": {"name": cleaned_data['Type']}}
    }
    return properties


def find_notion_page(activity_id):
    """ Recherche une page Notion par l'Activity ID Strava. """
    search_url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    filter_payload = {
        "filter": {
            "property": "Activity ID",
            "number": {
                "equals": activity_id
            }
        }
    }

    response = requests.post(search_url, headers=headers, json=filter_payload)
    response.raise_for_status()
    results = response.json().get("results", [])
    
    if results:
        return results[0]["id"]
    return None


def sync_activity_to_notion(activity_id, is_update=False):
    """ Gère le flux complet : Strava -> Traitement -> Notion. """
    
    access_token = get_valid_access_token()
    if not access_token:
        print("❌ Sync échoué : Pas de token d'accès Strava valide.")
        return False
        
    activity_url = f"{STRAVA_API_URL}/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        strava_response = requests.get(activity_url, headers=headers)
        strava_response.raise_for_status()
        activity_data = strava_response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Strava API : {e}")
        return False

    cleaned_data = clean_data(activity_data)
    notion_payload = format_for_notion(cleaned_data)
    page_id = find_notion_page(activity_id)

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    if page_id:
        # MISE À JOUR
        print(f"🔄 Mise à jour de la page Notion existante...")
        update_url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.patch(update_url, headers=headers, json={"properties": notion_payload})
    else:
        # CRÉATION
        print(f"➕ Création d'une nouvelle page Notion...")
        create_url = "https://api.notion.com/v1/pages"
        create_payload = {
            "parent": {"database_id": NOTION_DB_ID},
            "properties": notion_payload
        }
        response = requests.post(create_url, headers=headers, json=create_payload)

    try:
        response.raise_for_status()
        print(f"✅ Sync Notion réussi pour : {cleaned_data['Name']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur Notion API : {e}")
        return False