
# 🚀 Strava To Notion Sync

## 🧩 Aperçu du Projet

**Strava To Notion Sync** est un micro-service personnel basé sur Python qui automatise la synchronisation de toutes les activités sportives enregistrées sur Strava vers une base de données Notion dédiée.

Le service utilise les Webhooks de Strava pour une détection d'événement en temps réel et gère l'authentification OAuth2 (rafraîchissement automatique des tokens) pour assurer une synchronisation continue et sans intervention manuelle.

-----

## 🏗️ Architecture et Technologies

Ce projet repose sur une architecture simple et robuste :

| Composant | Technologie | Rôle |
| :--- | :--- | :--- |
| **Backend** | Python / FastAPI | Logique métier (Réception Webhook, Traitement, API Calls) |
| **Hébergement** | *Choix Gratuit (Render/Railway)* | Déploiement en continu |
| **Stockage Tokens** | Notion Database (Config) | Coffre-fort sécurisé et persistant pour les tokens d'accès |
| **APIs** | Strava API (Webhooks & Activity Fetch) | Déclenchement événementiel et récupération des données brutes |

-----

## 🛠️ Installation et Configuration

Pour faire fonctionner l'intégration, vous devez configurer trois éléments : **Strava**, **Notion**, et votre **Environnement Local**.

### 1\. Configuration de l'environnement Python

```bash
# 1. Cloner le dépôt
git clone [URL_DE_TON_REPO]
cd strava-to-notion-sync

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# venv\Scripts\activate.bat (Sur Windows)

# 3. Installer les dépendances
pip install -r requirements.txt
```

### 2\. Configuration des Secrets (Variables d'environnement)

Créez un fichier `.env` à la racine du projet (ce fichier DOIT être dans votre `.gitignore` pour la sécurité) et remplissez-le avec vos clés API.

```dotenv
# .env file (DO NOT COMMIT THIS)

# -- Strava App Credentials --
STRAVA_CLIENT_ID="[VOTRE_CLIENT_ID]"
STRAVA_CLIENT_SECRET="[VOTRE_CLIENT_SECRET]"

# -- Notion Credentials --
NOTION_API_KEY="[VOTRE_INTEGRATION_TOKEN]"
NOTION_DB_ID="[ID_DE_VOTRE_BASE_ACTIVITES]"
NOTION_CONFIG_DB_ID="[ID_DE_VOTRE_BASE_CONFIG_TOKEN]"
```

### 3\. Création des Bases de Données Notion

Deux bases de données distinctes sont nécessaires :

#### A. 🏃 Activités (Base Principale)

  * Doit contenir les propriétés détaillées dans le Cahier des Charges (CdC), y compris la propriété `Activity ID` (Type Number) pour la gestion des mises à jour.

#### B. 🔑 Config (Coffre-Fort pour Tokens)

  * Une base simple pour stocker de manière persistante le `refresh_token` Strava.
  * Propriétés requises : **Key** (Title) et **Value** (Text).
  * Assurez-vous que votre intégration Notion a accès à ces deux bases de données.

### 4\. Authentification Initiale Strava (OAuth)

Avant que le webhook ne puisse fonctionner, vous devez effectuer la première authentification manuelle pour obtenir le premier `refresh_token`.

1.  Exécutez le script d'authentification initial :
    ```bash
    python scripts/auth_setup.py
    ```
2.  Suivez les instructions pour autoriser l'application Strava dans votre navigateur.
3.  Le script sauvegardera automatiquement le premier `refresh_token` dans la base **Notion Config**.

-----

## 📡 Développement et Test du Webhook (Local)

Le développement des webhooks nécessite l'exposition de votre machine locale à Internet.

1.  **Démarrer votre serveur FastAPI :**

    ```bash
    uvicorn main:app --reload
    ```

    *(Le serveur tourne généralement sur `http://127.0.0.1:8000`)*

2.  **Démarrer ngrok pour le tunneling :**

    ```bash
    ngrok http 8000
    ```

    *ngrok* vous donnera une URL publique temporaire (ex: `https://abcd123.ngrok-free.app`).

3.  **Configuration du Webhook Strava :**

      * Rendez-vous sur la page de votre application Strava.
      * Définissez l'URL de Callback sur l'URL de ngrok, suivi de l'endpoint : `https://abcd123.ngrok-free.app/webhook/strava`.
      * Strava enverra un "challenge" que le serveur doit valider pour s'abonner aux événements.

-----

## 📝 Roadmap des Fonctionnalités (Récapitulatif)

  * [x] Implémentation du flux OAuth2 et rafraîchissement automatique.
  * [x] Gestion sécurisée des tokens via la DB Notion Config.
  * [ ] Endpoint `/webhook/strava` pour la validation du challenge Strava.
  * [ ] Logique de gestion de l'événement `activity.create` (Création).
  * [ ] Logique de gestion de l'événement `activity.update` (Mise à jour).
  * [ ] Déploiement sur un service gratuit.