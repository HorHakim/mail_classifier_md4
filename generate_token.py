from __future__ import print_function
import os
import os.path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


def generate_gmail_token():
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    print("token.json généré avec succès.")



def generate_google_drive_token():
    """
    Exécute l'authentification Google OAuth et génère le token.
    """
    SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
    ]
    creds = None
    token_file="token_sheets.pickle"
    # Charger le token existant si présent
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    # Sinon lancer un login OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Sauvegarde du token
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)

    print("✅ Token OAuth généré avec succès :", token_file)


if __name__ == "__main__":
    generate_gmail_token()
