import requests
import os

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

        print(f"> TIV query params: {query_params}")

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
            descripcion = p.get("descripcion", "")
            summaries.append(
                f"{title}\nPrecio: {moneda} {precio}\n{descripcion}")

        return "\n\n".join(summaries)

    except Exception as e:
        print("> TIV API error:", str(e))
        return "Hubo un error al buscar propiedades."


# filters = {
#     "zona": "Acacias",
#     "tipo": "casa",
#     "precio_max": 30000000,
#     "dormitorios": 3,
#     "con_cochera": True
# }

# print(fetch_properties_from_tiv(filters))
