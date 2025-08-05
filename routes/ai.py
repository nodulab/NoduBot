from flask import Blueprint, request
from utils.openai_proxy import chat, reset_memory_route
from utils.authentication import check_auth

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/chat', methods=['POST'])
def proxy_to_openai():
    check_auth(request.headers)
    data = request.get_json()
    user_message = data.get("message", "").strip()
    memory_key = data.get("memory_key")
    model = data.get("model", "gpt-4o")
    temperature = float(data.get("temperature", 0.7))
    return chat(user_message, memory_key, model, temperature)


@ai_bp.route("/reset/<key>", methods=["DELETE"])
def forget_user(key):
    check_auth(request.headers)
    return reset_memory_route(key)
