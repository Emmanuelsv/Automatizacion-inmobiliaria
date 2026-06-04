import httpx
from app.config import WASI_BASE_URL, WASI_COMPANY_ID, WASI_TOKEN

PROPERTY_TYPE_MAP: dict[str, int] = {
    "Apartamento": 2,
    "Casa": 1,
    "Local": 3,
    "Oficina": 4,
    "Bodega": 5,
    "Lote": 6,
    "Finca": 7,
}

CITY_ID_MAP: dict[str, int] = {
    "Medellín": 496,
    "Envigado": 291,
    "Sabaneta": 698,
    "Bello": 89,
    "Itagüí": 466,
    "La Estrella": 420,
    "Caldas": 140,
    "Copacabana": 218,
}

# Barrio normalizado (minúsculas, sin tildes) → id_zone en Wasi
ZONE_ID_MAP: dict[str, int] = {
    # === ENVIGADO ===
    "las brujas": 747178,
    "loma de las brujas": 747178,
    "loma del chocho": 905357,
    "el chocho": 905357,
    "el esmeraldal": 905074,
    "esmeraldal": 905074,
    "el escobero": 749304,
    "escobero": 749304,
    "loma del escobero": 905072,
    "otra parte": 905359,
    "las antillas": 747840,
    "el dorado": 905076,
    "el salado": 905073,
    "loma del atravesado": 905361,
    "la abadia": 905071,
    # === MEDELLÍN ===
    "el poblado": 736658,
    "poblado": 750022,
    "laureles": 735463,
    "belen": 750714,
    "belén": 750714,
    "castropol": 905069,
    "las palmas": 744448,
    "los balsos": 830591,
    "loma de los balsos": 830591,
    "san lucas": 905075,
    "loma del indio": 782735,
    "santa maria": 782230,
    "santa maria de los angeles": 782230,
    # === SABANETA ===
    "aves maria": 744762,
    "aves maría": 744762,
    "las lomitas": 905084,
    "mayorca": 752700,
    "pan de azucar": 774196,
    "san jose": 731929,
}


def _normalize(text: str) -> str:
    replacements = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n"}
    result = text.lower()
    for orig, repl in replacements.items():
        result = result.replace(orig, repl)
    return result


def _get_zone_id(barrio: str) -> int | None:
    key = _normalize(barrio)
    return ZONE_ID_MAP.get(key)


async def _fetch_page(params: dict, page: int, per_page: int) -> list[dict]:
    p = dict(params)
    p["skip"] = (page - 1) * per_page
    p["take"] = per_page
    url = f"{WASI_BASE_URL}/property/search"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=p)
        response.raise_for_status()
        data = response.json()
    if isinstance(data, dict):
        return [v for k, v in data.items() if k.isdigit()]
    elif isinstance(data, list):
        return data
    return []


async def search_properties(
    city: str | None = None,
    zone: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    min_area: int | None = None,
    min_rooms: int | None = None,
    property_type: str | None = None,
    offer_type: int = 1,
    per_page: int = 100,
    max_pages: int = 5,
) -> list[dict]:
    params: dict = {
        "id_company": WASI_COMPANY_ID,
        "wasi_token": WASI_TOKEN,
        "id_offer_type": offer_type,
    }

    if city and city in CITY_ID_MAP:
        params["id_city"] = CITY_ID_MAP[city]

    # No filtramos por id_zone: Wasi tiene propiedades sin zona asignada
    # aunque el título mencione el barrio. El matcher aplica scoring por zona.

    if min_price:
        params["min_price"] = int(min_price)
    if max_price:
        params["max_price"] = int(max_price)
    if min_area:
        params["min_area"] = int(min_area)
    if min_rooms:
        params["min_rooms"] = int(min_rooms)
    if property_type and property_type in PROPERTY_TYPE_MAP:
        params["id_property_type"] = PROPERTY_TYPE_MAP[property_type]

    all_results: list[dict] = []
    for page in range(1, max_pages + 1):
        page_results = await _fetch_page(params, page, per_page)
        all_results.extend(page_results)
        if len(page_results) < per_page:
            break  # última página

    return all_results


async def search_all_locations(
    ubicaciones: list[dict],
    min_price: int | None = None,
    max_price: int | None = None,
    min_area: int | None = None,
    min_rooms: int | None = None,
    property_type: str | None = None,
) -> list[dict]:
    all_properties: list[dict] = []
    seen_ids: set = set()
    seen_cities: set = set()  # <-- Evita llamadas duplicadas a la API por la misma ciudad

    for ubicacion in ubicaciones:
        ciudad = ubicacion["ciudad"]
        
        if ciudad in seen_cities:
            continue
        seen_cities.add(ciudad)

        try:
            properties = await search_properties(
                city=ciudad,
                zone=None,  # Buscamos la ciudad completa; el matcher se encarga del scoring por barrio/POI
                min_price=min_price,
                max_price=max_price,
                min_area=min_area,
                min_rooms=min_rooms,
                property_type=property_type,
            )

            for prop in properties:
                prop_id = prop.get("id_property") or prop.get("id") or id(prop)
                if prop_id not in seen_ids:
                    seen_ids.add(prop_id)
                    all_properties.append(prop)

        except httpx.HTTPError as e:
            print(f"Error buscando en {ciudad}: {e}")
            continue

    return all_properties