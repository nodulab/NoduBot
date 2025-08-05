from flask import Blueprint, request, jsonify
from utils.authentication import check_auth
from utils.whatsapp import send_whatsapp_message
from utils.openai_proxy import chat

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/chat', methods=['POST'])
def handle_webhook():
    check_auth(request.headers.get("Authorization", ""))
    print("Received webhook request")
    try:
        data = request.get_json()
        print("Webhook data:", data)
        entry = data['entry'][0]['changes'][0]['value']
        messages = entry['messages']
        if not messages:
            return jsonify({"status": "no message"}), 200

        msg = messages[0]
        sender = msg['from']
        text = msg['text']['body']

        print(f"Received message from {sender}: {text}")

        reply = chat(user_message=text, memory_key=sender)
        # send_whatsapp_message(sender, reply)

        return jsonify({"Reply": reply}), 200

    except Exception as e:
        print("Webhook error:", str(e))
        return jsonify({"error": str(e)}), 500
