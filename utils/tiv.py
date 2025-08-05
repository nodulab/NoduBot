import requests
import os
from flask import current_app
from utils.debugger_utils import debug_print

TIV_API_URL = "https://api.tiv.com.ar/v1/inmuebles/buscar"
TIV_API_KEY = os.getenv("TIV_API_KEY")


def fetch_properties_from_tiv(filters: dict) -> str:
    try:
        # Map OpenAI args to TIV query params
        query_params = {}

        if "zona" in filters:
            query_params["direccion"] = filters["zona"]

        if "tipo" in filters:
            query_params["descripcion_busqueda"] = filters["tipo"]

        if "precio_min" in filters:
            query_params["precio_desde"] = filters["precio_min"]

        if "precio_max" in filters:
            query_params["precio_hasta"] = filters["precio_max"]

        if "con_cochera" in filters:
            query_params["con_cochera"] = filters["con_cochera"]

        if "amoblado" in filters:
            query_params["amoblado"] = filters["amoblado"]

        if "apto_credito" in filters:
            query_params["apto_credito"] = filters["apto_credito"]

        if "apto_profesional" in filters:
            query_params["apto_profesional"] = filters["apto_profesional"]

        if "con_vigilancia" in filters:
            query_params["con_vigilancia"] = filters["con_vigilancia"]

        if "en_barriocerrado" in filters:
            query_params["en_barriocerrado"] = filters["en_barriocerrado"]

        debug_print(f"> TIV query params: {query_params}")

        headers = {
            "Accept": "application/json",
            "x-tg-key": os.getenv("TIV_API_KEY")
        }

        response = requests.get(TIV_API_URL,
                                params=query_params,
                                headers=headers)

        data = response.json()
        items = data.get("items", [])
        if not items:
            return "No se encontraron propiedades con esos criterios."

        summaries = []
        for p in items[:5]:  # Show top 5 matches
            title = p.get("titulo", "Sin título")
            precio = p.get("operacion", {}).get("precio", "s/d")
            moneda = p.get("operacion", {}).get("moneda", "")
            descripcion = p.get("descripcion",
                                "").split('\n')[0]  # Solo primer línea
            ubicacion = p.get("ubicacion", {}).get("otras_descripciones",
                                                   {}).get("limitada", "")
            tipo = p.get("producto", {}).get("nombre", "")
            ambientes = p.get("ambientes", "")
            dormitorios = p.get("cantidad_dormitorios", "")
            banos = p.get("cantidad_banos", "")
            metros = next(
                (s["valor"]
                 for s in p.get("superficies", []) if s["id"] == "cubierta"),
                None)

            parts = [
                f"{title}", f"Ubicación: {ubicacion}" if ubicacion else "",
                f"Tipo: {tipo}" if tipo else "",
                f"Ambientes: {ambientes}" if ambientes else "",
                f"Dormitorios: {dormitorios}" if dormitorios else "",
                f"Baños: {banos}" if banos else "",
                f"Superficie cubierta: {metros} m²" if metros else "",
                f"Precio: {moneda} {precio}",
                f"Descripción: {descripcion}" if descripcion else ""
            ]

            summary = "\n".join([line for line in parts if line])
            summaries.append(summary)

        ret = "\n\n".join(summaries)
        if current_app.debug:
            debug_print(f"> TIV response: {ret}")
        return ret

    except Exception as e:
        debug_print("> TIV API error:", str(e))
        return "Hubo un error al buscar propiedades."
