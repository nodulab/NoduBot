from flask import Flask, jsonify
import requests
import os
from replit import db

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# === Helpers ===


def convert_to_native(obj):
    if hasattr(obj, "value"):  # ObservedDict / ObservedList
        return convert_to_native(obj.value)
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)  # fallback


def get_memory(key):
    raw = db.get(key, [])
    native = convert_to_native(raw)
    return native if isinstance(native, list) else []


def set_memory(key, messages):
    db[key] = convert_to_native(messages)


# === Actions ===


def reset_memory_route(key):
    if key in db:
        del db[key]
        return jsonify({"status": "deleted", "memory_key": key})
    return jsonify({"status": "not found", "memory_key": key}), 404


def chat(user_message, memory_key, model="gpt-4o", temperature=0.7):
    if not user_message:
        raise ValueError("Missing 'user_message'")
    if not memory_key:
        raise ValueError("Missing 'memory_key'")

    print(f"> Incoming request with memory_key: {memory_key}")
    print(f"> Message: {user_message}")

    messages = get_memory(memory_key)
    print(f"> Retrieved memory for '{memory_key}': {messages}")

    messages.append({"role": "user", "content": user_message})
    print(f"> Full messages to OpenAI:\n{messages}")

    # Call OpenAI
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
    result = response.json()

    if response.status_code != 200:
        raise Exception(result.get("error", {}).get("message", "OpenAI error"))

    assistant_reply = result["choices"][0]["message"]["content"]
    print(f"> OpenAI reply: {assistant_reply}")

    # Save updated memory (limit to last 20)
    messages.append({"role": "assistant", "content": assistant_reply})
    set_memory(memory_key, messages[-20:])
    print(f"> Saved memory for '{memory_key}'")

    return assistant_reply
