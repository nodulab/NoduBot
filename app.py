from flask import Flask
from routes.webhook import webhook_bp

app = Flask(__name__)


# Health Check
@app.route("/", methods=["GET"])
def home():
    return "<h2>✅ NoduBot+ is running</h2>"


# Register Blueprints
app.register_blueprint(webhook_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
