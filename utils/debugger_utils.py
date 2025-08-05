from flask import current_app


def debug_print(*args, **kwargs):
  try:
    if current_app.debug:
      print(*args, **kwargs)
  except RuntimeError:
    # En caso de que no haya un contexto de app (por ejemplo en pruebas)
    print(*args, **kwargs)
