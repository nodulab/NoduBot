from flask import Blueprint, request
from utils.openai_proxy import chat, reset_memory_route
from utils.authentication import check_auth

ai_bp = Blueprint('ai', __name__)

# @ai_bp.route('/chat', methods=['POST'])
# def proxy_to_openai():
#     check_auth(request.headers.get("Authorization", ""))
#     data = request.get_json()
#     user_message = data.get("message", "").strip()
#     memory_key = data.get("memory_key")
#     return chat(user_message, memory_key)


@ai_bp.route("/reset/<key>", methods=["DELETE"])
def forget_user(key):
    check_auth(request.headers.get("Authorization", ""))
    return reset_memory_route(key)
