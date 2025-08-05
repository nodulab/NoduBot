from flask import abort
import os

AUTHORIZATION_TOKEN = os.getenv("AUTHORIZATION_TOKEN")


def check_auth(headers):
  auth_header = headers.get("Authorization", "")
  print("> Received header:", auth_header)
  if not auth_header.startswith("Bearer ") or auth_header.split(
      " ")[1] != AUTHORIZATION_TOKEN:
    abort(401, description="Unauthorized")
