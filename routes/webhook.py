from flask import Blueprint, request, jsonify, Response
from utils.whatsapp import send_whatsapp_message
from utils.openai_proxy import chat
from utils.debugger_utils import debug_print
import hashlib
import hmac
import os

webhook_bp = Blueprint('webhook', __name__)

APP_SECRET = os.environ.get("META_APP_SECRET")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


@webhook_bp.route("/nodubotchat", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    token = request.args.get("hub.verify_token")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED")
        return Response(challenge, status=200, mimetype="text/plain")
    else:
        return Response("", status=403)


def verify_signature(request):
    received_sig = request.headers.get('X-Hub-Signature-256')
    if not received_sig:
        return False

    payload = request.get_data()
    expected_sig = 'sha256=' + hmac.new(APP_SECRET.encode(),
                                        msg=payload,
                                        digestmod=hashlib.sha256).hexdigest()

    return hmac.compare_digest(received_sig, expected_sig)


@webhook_bp.route('/nodubotchat', methods=['POST'])
def handle_webhook():
    if not verify_signature(request):
        return Response("Invalid signature", status=403)
    debug_print("Received webhook request")
    try:
        data = request.get_json()
        entry = data['entry'][0]['changes'][0]['value']

        if 'messages' not in entry:
            # Different status - ex: delivered
            return jsonify({"status": "no message"}), 200

        messages = entry['messages']
        if not messages:
            return jsonify({"status": "no message"}), 200

        msg = messages[0]
        sender = msg['from']
        text = msg['text']['body']

        debug_print(f"Received message from {sender}: {text}")

        reply = chat(user_message=text, memory_key=sender)
        debug_print(f"Prepared reply to {sender}: {reply}")

        send_whatsapp_message(sender, reply)
        return jsonify({"Status": f"Sent reply to {sender}"}), 200

    except Exception as e:
        print("Webhook error:", str(e))
        return jsonify({"error": str(e)}), 500
