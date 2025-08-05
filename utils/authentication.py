from flask import abort, current_app
import os
from utils.debugger_utils import debug_print

AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")


def check_auth(auth_header):
  debug_print("> Received header:", auth_header)
  if not auth_header.startswith("Bearer ") or auth_header.split(
      " ")[1] != AUTHORIZATION_TOKEN:
    abort(401, description="Unauthorized")
