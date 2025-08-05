from flask import Flask, request, Response
from routes.webhook import webhook_bp
from routes.ai import ai_bp
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# # Health Check
# @app.route("/", methods=["GET"])
# def home():
#     return "<h2>✅ NoduBot+ is running</h2>"


@app.route("/", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    token = request.args.get("hub.verify_token")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED")
        return Response(challenge, status=200, mimetype="text/plain")
    else:
        return Response("", status=403)


# Register Blueprints
app.register_blueprint(webhook_bp)
app.register_blueprint(ai_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
