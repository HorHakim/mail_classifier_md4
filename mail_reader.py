
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
import html
import os
import pickle

def extract_mail_content(message):
    """
    Extrait le corps complet d'un mail Gmail (supporte HTML et texte).
    Décode automatiquement le base64 ET les entités HTML.
    """
    payload = message.get("payload", {})

    # ---- Cas : email multipart (HTML + texte) ----
    if "parts" in payload:
        for part in payload["parts"]:
            mime = part.get("mimeType", "")
            if mime in ("text/plain", "text/html"):
                data = part.get("body", {}).get("data")
                if data:
                    texte = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                    return html.unescape(texte)

    # ---- Cas : email simple ----
    body = payload.get("body", {})
    if "data" in body:
        data = body["data"]
        texte = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return html.unescape(texte)

    return ""


def read_mails_from_gmail(start_datetime, end_datetime, verbose=False, creds_file="token.json"):
    """
    Lit tous les emails Gmail dans une plage horaire donnée.
    Maintenant renvoie le CONTENU COMPLET du mail.
    """

    if os.path.exists("mails.pkl"):
        with open("mails.pkl", "rb") as f:  # "rb" = read binary
            mails_content = pickle.load(f)

    else:
        counter = 0
        creds = Credentials.from_authorized_user_file(
            creds_file,
            ["https://www.googleapis.com/auth/gmail.readonly"]
        )
        service = build("gmail", "v1", credentials=creds)

        after = int(start_datetime.timestamp())
        before = int(end_datetime.timestamp())
        query = f"after:{after} before:{before}"

        mails_content = []
        page_token = None

        while True:
            response = service.users().messages().list(
                userId="me",
                q=query,
                pageToken=page_token,
                maxResults=100
            ).execute()

            messages = response.get("messages", [])
            for message in messages:

                # Récupération du mail complet (pas snippet)
                full_message = service.users().messages().get(
                    userId="me",
                    id=message["id"],
                    format="full"
                ).execute()

                # Extraction du texte complet
                mail_content = extract_mail_content(full_message)
                if verbose:
                    print("ID :", full_message["id"])
                    print("Texte complet :")
                    print(mail_content)
                    print("-----")


                mails_content.append(mail_content)
                counter += 1
                print(counter)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

    return mails_content


if __name__ == "__main__":

    emails = read_mails_from_gmail(
        start_datetime=datetime(2025, 11, 16, 0, 0),
        end_datetime=datetime(2025, 11, 18, 23, 59)
    )
    print(emails)



    # with open("mails.pkl", "wb") as f:  # "wb" = write binary
    #     pickle.dump(emails, f)

    # print("Nombre d'emails récupérés :", len(emails))

    # # Exemple : afficher les 3 premiers textes complets
    # for mail in emails[:3]:
    #     print("Texte :", mail)
    #     print("-----")

