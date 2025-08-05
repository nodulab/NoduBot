from flask import Flask, jsonify
import os
import openai
import time
from replit import db
from utils.tiv import fetch_properties_from_tiv

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "")

# === Memory Helpers ===


def convert_to_native(obj):
    if hasattr(obj, "value"):
        return convert_to_native(obj.value)
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def get_memory(key):
    raw = db.get(key, [])
    native = convert_to_native(raw)
    return native if isinstance(native, list) else []


def set_memory(key, messages):
    db[key] = convert_to_native(messages)


def reset_memory_route(memory_key):
    thread_key = f"thread:{memory_key}"
    if thread_key in db:
        del db[thread_key]
        return jsonify({"status": "deleted", "thread_key": thread_key})
    return jsonify({"status": "not found", "thread_key": thread_key}), 404


# === Thread & GPT Logic ===


def get_or_create_thread(memory_key):
    key = f"thread:{memory_key}"
    thread_id = db.get(key)
    if not thread_id:
        thread = openai.beta.threads.create()
        thread_id = thread.id
        db[key] = thread_id
        print(f"> Created new thread: {thread_id}")
    else:
        print(f"> Reusing thread: {thread_id}")
    return thread_id


def add_message_to_thread(thread_id, message):
    openai.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=message)


def handle_tool_calls(run, thread_id):
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []

    for tool_call in tool_calls:
        name = tool_call.function.name
        args = eval(tool_call.function.arguments)

        if name == "search_properties":
            output = fetch_properties_from_tiv(args)
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": output
            })

    return openai.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs)


def poll_until_ready(thread_id, run_id):
    while True:
        run = openai.beta.threads.runs.retrieve(thread_id=thread_id,
                                                run_id=run_id)

        if run.status in ["queued", "in_progress"]:
            time.sleep(1)
            continue
        elif run.status == "requires_action":
            run = handle_tool_calls(run, thread_id)
            continue
        elif run.status == "completed":
            return
        else:
            raise Exception(f"Run failed or unknown status: {run.status}")


def get_latest_assistant_reply(thread_id):
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages.data:
        if msg.role == "assistant":
            return msg.content[0].text.value
    raise Exception("No assistant reply found.")


# === Public API ===


def chat(user_message, memory_key):
    if not user_message or not memory_key:
        raise ValueError("Missing user_message or memory_key")

    print(f"> chat(): memory_key = {memory_key}")
    thread_id = get_or_create_thread(memory_key)
    add_message_to_thread(thread_id, user_message)

    run = openai.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=ASSISTANT_ID)
    print(f"> Run started: {run.id}")

    poll_until_ready(thread_id, run.id)
    return get_latest_assistant_reply(thread_id)
