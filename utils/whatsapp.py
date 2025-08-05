# /utils/meta_whatsapp.py
import requests
import os

ACCESS_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = "722456124288514"


def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": text
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    
    print(f"> WhatsApp response: {response.status_code} {response.text}")

    if response.status_code != 200:
        raise Exception(f"WhatsApp error: {response.text}")
    return response.json()
