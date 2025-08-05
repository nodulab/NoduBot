# /utils/meta_whatsapp.py
import requests

YOUR_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

def send_whatsapp_message(to, text):
    url = "https://graph.facebook.com/v19.0/YOUR_PHONE_NUMBER_ID/messages"
    headers = {
        "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.json()
