import re
from dataclasses import dataclass, field

from app.locations import BARRIOS, ALIAS_CIUDADES
from app.normalizer import normalize_text, remove_emojis
from app.price_parser import extract_budget, Budget


@dataclass
class Location:
    ciudad: str
    barrio: str
    


@dataclass
class SolicitudParseada:
    es_solicitud: bool = False
    ubicaciones: list[Location] = field(default_factory=list)
    ubicaciones_excluidas: list[Location] = field(default_factory=list)
    presupuesto: Budget = field(default_factory=Budget)
    tipo_inmueble: str | None = None
    habitaciones_min: int | None = None
    area_min: int | None = None
    administracion_max: int | None = None
    asesor: str | None = None
    cliente: str | None = None
    telefono: str | None = None
    caracteristicas: list[str] = field(default_factory=list)
    mensaje_original: str = ""


def is_solicitud(text: str) -> bool:
    normalized = normalize_text(text)
    keywords = [
        "solicitud de propiedad",
        "solicitud de inmueble",
        "se busca",
        "busco",
        "necesito",
        "cliente busca",
        "cliente necesita",
        "requiero",
        "presupuesto",
        "ubicacion deseada",
        # REMOVIDO: "habitaciones" → aparece en ofertas también
        # REMOVIDO: "inmueble"      → aparece en ofertas también
        # REMOVIDO: "inmobiliaria", "inmobiliarios", "inmobiliario" → ambiguos
        # REMOVIDO: "real estate"   → ambiguo
        "solicitud",
        "solicito",
        "modo de pago",
        "credito hipotecario",
        "credito bancario",
        "credito",
        "pago de contado",
        "pago contado",
        "leasing",
        "arrendamiento con opcion de compra",
        "leasing habitacional",
        "quiero apartamento",
        "quiero un apartamento",
        "quiero apto",
        "quiero un apto",
        "quiero casa",
        "quiero una casa",
        "cliente quiere casa",
        "cliente quiere una casa",      
        "cliente quiere apartamento",
        "cliente quiere un apartamento",        
    ]
    
    keywords_oferta = [
        "oferta de propiedad",
        "oferta de inmueble",
        "venta",
        "ofrezco",
        "disponible",
        "ofertar",
        "oferta",
        "ofrecemos",
        "para colegaje",
        "vendemos",
        "en venta",
        "se vende",
        "se ofrece",
        "vendo", 

    ]
     
    keyword_oferta_count = sum(1 for ko in keywords_oferta if ko in normalized)
    keyword_count = sum(1 for kw in keywords if kw in normalized)
    has_price = bool(
        re.search(r"\$?\d{1,3}(?:\.\d{3}){2,}", text)
        or re.search(r"\d+\s*(?:millones|millon|mills?|mll|mls)\b", text, re.IGNORECASE)
        or re.search(r"\d{1,3}['']\d{3}", text)
        or re.search(r"(?<!\d)\d{3,4}\s*[Mm]\b", text)
        or (
            re.search(r"presupuesto", normalized, re.IGNORECASE)
            and re.search(r"(?<!\d)\d{3,5}(?!\d)", text)
        )
    )
    has_url = bool(
        re.search(r"https?://[^/]+\.inmo\.co", normalized)
        or re.search(r"https://info\.wasi\.co", text)
    )

    # Si el mensaje tiene señales claras de búsqueda, no bloquearlo por oferta
    has_solicitud_fuerte = any(
        kw in normalized
        for kw in ["busco", "se busca", "necesito", "solicitud", "solicito",
                   "cliente busca", "cliente necesita", "requiero"]
    )

    if has_url:
        return False
    elif keyword_oferta_count >= 1 and not has_solicitud_fuerte:
        # Oferta clara sin señal de búsqueda → siempre es oferta
        return False
    elif has_solicitud_fuerte and has_price:
        # Señal explícita de búsqueda ("busco", "necesito", etc.) + precio → solicitud
        return True
    else:
        return keyword_count >= 1 and has_price


def _word_match(pattern: str, text: str) -> bool:
    """Verifica que el patrón aparece como palabra completa (no como parte de otra)."""
    return bool(re.search(r"(?<!\w)" + re.escape(pattern) + r"(?!\w)", text))


def extract_locations(text: str) -> list[Location]:
    normalized = normalize_text(text)
    found: list[Location] = []
    seen: set[str] = set()

    sorted_barrios = sorted(BARRIOS.items(), key=lambda x: len(x[0]), reverse=True)

    for key, data in sorted_barrios:
        normalized_key = normalize_text(key)
        if _word_match(normalized_key, normalized) and data["nombre"] not in seen:
            found.append(Location(barrio=data["nombre"], ciudad=data["ciudad"]))
            seen.add(data["nombre"])

    # Fallback: si mencionan la ciudad sin barrio específico
    sorted_ciudades = sorted(ALIAS_CIUDADES.items(), key=lambda x: len(x[0]), reverse=True)
    for key, ciudad in sorted_ciudades:
        normalized_key = normalize_text(key)
        if _word_match(normalized_key, normalized):
            already_covered = any(loc.ciudad == ciudad for loc in found)
            if not already_covered and ciudad not in seen:
                found.append(Location(barrio=ciudad, ciudad=ciudad))
                seen.add(ciudad)

    return found


def extract_property_type(text: str) -> str | None:
    normalized = normalize_text(text)

    types = [
        (["apartamento", "apto", "apto.", "apartaestudio"], "Apartamento"),
        (["casa", "casa campestre"], "Casa"),
        (["local", "local comercial"], "Local"),
        (["oficina"], "Oficina"),
        (["bodega"], "Bodega"),
        (["lote", "terreno"], "Lote"),
        (["finca"], "Finca"),
    ]

    found = []
    for patterns, prop_type in types:
        for pattern in patterns:
            if pattern in normalized:
                found.append(prop_type)
                break

    # Si el usuario menciona múltiples tipos ("apartamento o casa"), no filtrar
    if len(found) == 1:
        return found[0]
    return None


def extract_rooms(text: str) -> int | None:
    # "2 o 3 habitaciones", "2 a 3 hab", "entre 2 y 3 alcobas" → return the lower bound
    range_match = re.search(
        r"(\d+)\s*(?:o|a|y)\s*(\d+)\s*(?:habitacion|hab|alcoba|cuarto)",
        text,
        re.IGNORECASE,
    )
    if range_match:
        rooms = min(int(range_match.group(1)), int(range_match.group(2)))
        if 1 <= rooms <= 10:
            return rooms

    patterns = [
        r"m[ií]nimo\s*(\d+)\s*(?:habitacion|hab|alcoba|cuarto)",
        r"(\d+)\s*(?:habitacion|hab|alcoba|cuarto)\s*(?:o\s*m[aá]s)?",
        r"(?:habitacion|hab|alcoba|cuarto)\s*(?:m[ií]nimo|min|desde)?\s*[:.]?\s*(\d+)",
        r"desde\s*(\d+)\s*(?:habitacion|hab|alcoba|cuarto)",
        r"🛏️?\s*(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            rooms = int(match.group(1))
            if 1 <= rooms <= 10:
                return rooms

    return None


def extract_area(text: str) -> int | None:
    patterns = [
        r"(?:area|área)\s*(?:desde|m[ií]nim[ao]|min)?\s*[:.]?\s*(\d+)\s*(?:m2|m²|mts?|metros)",
        r"desde\s*(\d+)\s*(?:m2|m²|mts?|metros)",
        r"m[aá]s\s*de\s*(\d+)\s*(?:m2|m²|mts?|metros)",
        r"(\d+)\s*(?:m2|m²)\s*(?:en\s*adelante|o\s*m[aá]s)?",
        r"(\d+)\s*(?:metros?\s*cuadrados)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            area = int(match.group(1))
            if 20 <= area <= 100000:
                return area

    return None


def extract_admin_fee(text: str) -> int | None:
    patterns = [
        r"administraci[oó]n\s*(?:m[aá]ximo|max|hasta|:)?\s*[:.]?\s*\$?\s*(\d{1,3}(?:\.\d{3})*)",
        r"admin\s*(?:m[aá]ximo|max|:)?\s*[:.]?\s*\$?\s*(\d{1,3}(?:\.\d{3})*)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fee = int(match.group(1).replace(".", ""))
            if 50_000 <= fee <= 50_000_000:
                return fee

    return None


def extract_advisor(text: str) -> str | None:
    # [ \t]+ en vez de \s+ para no cruzar saltos de línea
    patterns = [
        r"(?:👨‍💼|👩‍💼)\s*(?:[Aa]sesor[a]?\s*[:.]?\s*)([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:[ \t]+[A-ZÁÉÍÓÚÑa-záéíóúñ]+){1,3})",
        r"[Aa]sesor[a]?\s*[:.]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:[ \t]+[A-ZÁÉÍÓÚÑa-záéíóúñ]+){1,3})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return None


def extract_client(text: str) -> str | None:
    patterns = [
        r"(?:👩‍💼|👤)\s*(?:[Cc]liente\s*[:.]\s*)([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:[ \t]+[A-ZÁÉÍÓÚÑa-záéíóúñ]+){1,3})",
        r"[Cc]liente\s*[:.]\s*([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:[ \t]+[A-ZÁÉÍÓÚÑa-záéíóúñ]+){1,3})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return None


def extract_phone(text: str) -> str | None:
    patterns = [
        r"[Cc]ontacto\s*[:.]?\s*(\d[\d\s\-]{8,})",
        r"[Tt]el[eé]fono\s*[:.]?\s*(\d[\d\s\-]{8,})",
        r"[Cc]el\s*[:.]?\s*(\d[\d\s\-]{8,})",
        r"📱\s*(\d[\d\s\-]{8,})",
        r"[Ww]hatsapp\s*[:.]?\s*(\d[\d\s\-]{8,})",
        r"(3\d{9})",  # celular colombiano
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = re.sub(r"[\s\-]", "", match.group(1))
            if 10 <= len(phone) <= 12:
                return phone

    return None


def extract_features(text: str) -> list[str]:
    features: list[str] = []

    feature_patterns = [
        (r"piso\s*alto", "Piso alto"),
        (r"buena\s*vista|vista\s+agradable", "Vista"),
        (r"ascensor", "Ascensor"),
        (r"sin\s*registro", "Sin registro (propiedad horizontal)"),
        (r"parqueadero|garaje|parking", "Parqueadero"),
        (r"balc[oó]n", "Balcón"),
        (r"terraza", "Terraza"),
        (r"estudio|study", "Estudio"),
        (r"amoblado|amueblado", "Amoblado"),
        (r"piscina", "Piscina"),
        (r"gimnasio|gym", "Gimnasio"),
        (r"vigilancia|seguridad\s*24", "Vigilancia 24h"),
        (r"primer\s*piso|piso\s*1", "Primer piso"),
        (r"duplex|d[uú]plex", "Dúplex"),
        (r"penthouse|pent\s*house", "Penthouse"),
        (r"esquinero", "Esquinero"),
        (r"remodelado", "Remodelado"),
        (r"estrenar", "Para estrenar"),
    ]

    for pattern, label in feature_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            features.append(label)

    return features


_NEG_PREFIX = r"(?:no|sin|excluye?|excepto)\s+(?:le\s+gusta\s+)?"


def extract_negative_locations(text: str) -> list[Location]:
    """Detecta zonas explícitamente rechazadas: 'no palmas', 'sin palmas', 'no le gusta palmas'."""
    normalized = normalize_text(text)
    found: list[Location] = []
    seen: set[str] = set()

    sorted_barrios = sorted(BARRIOS.items(), key=lambda x: len(x[0]), reverse=True)
    for key, data in sorted_barrios:
        normalized_key = normalize_text(key)
        pattern = r"(?<!\w)" + _NEG_PREFIX + re.escape(normalized_key) + r"(?!\w)"
        if re.search(pattern, normalized, re.IGNORECASE) and data["nombre"] not in seen:
            found.append(Location(barrio=data["nombre"], ciudad=data["ciudad"]))
            seen.add(data["nombre"])

    return found


def parse_message(raw_text: str) -> SolicitudParseada:
    text_no_emojis = remove_emojis(raw_text)

    # 1. Extraer ubicaciones estándar (barrios y ciudades)
    ubicaciones_estandar = extract_locations(raw_text)
    
    # Obtener el conjunto de ciudades explícitas para desambiguar palabras clave genéricas (como "viva" o "exito")
    ciudades_detectadas = {u.ciudad for u in ubicaciones_estandar}

    # 2. Extraer Puntos de Interés (POIs) de forma inteligente
    from app.locations import PUNTOS_INTERES
    pois_encontrados = []
    normalized_text_content = normalize_text(raw_text)
    seen_poi_names = set()
    
    # Crear lista de palabras clave de POIs ordenada por longitud descendente (evita falsos positivos parciales)
    all_poi_kws = []
    for poi_id, data in PUNTOS_INTERES.items():
        for kw in data["keywords"]:
            # Identificar palabras que por sí solas son muy genéricas
            is_generic = kw in ["viva", "exito", "tesoro", "fabricato", "oviedo", "unicentro"]
            all_poi_kws.append({
                "keyword": normalize_text(kw),
                "nombre": data["nombre"],
                "ciudad": data["ciudad"],
                "is_generic": is_generic
            })
    all_poi_kws.sort(key=lambda x: len(x["keyword"]), reverse=True)
    
    for item in all_poi_kws:
        if _word_match(item["keyword"], normalized_text_content):
            # Si el término es genérico, exigimos que la ciudad del POI coincida con las detectadas.
            # Si no se detectó ninguna ciudad en el mensaje, lo dejamos pasar como fallback.
            if item["is_generic"] and ciudades_detectadas and item["ciudad"] not in ciudades_detectadas:
                continue
                
            if item["nombre"] not in seen_poi_names:
                pois_encontrados.append(Location(barrio=item["nombre"], ciudad=item["ciudad"]))
                seen_poi_names.add(item["nombre"])

    # 3. Detectar exclusiones y combinar ubicaciones finales
    excluidas = extract_negative_locations(raw_text)
    excl_nombres = {u.barrio for u in excluidas}
    
    todas_ubicaciones = ubicaciones_estandar + pois_encontrados
    ubicaciones = [u for u in todas_ubicaciones if u.barrio not in excl_nombres]

    return SolicitudParseada(
        es_solicitud=is_solicitud(raw_text),
        ubicaciones=ubicaciones,
        ubicaciones_excluidas=excluidas,
        presupuesto=extract_budget(raw_text),
        tipo_inmueble=extract_property_type(text_no_emojis),
        habitaciones_min=extract_rooms(raw_text),
        area_min=extract_area(raw_text),
        administracion_max=extract_admin_fee(raw_text),
        asesor=extract_advisor(raw_text),
        cliente=extract_client(raw_text),
        telefono=extract_phone(raw_text),
        caracteristicas=extract_features(raw_text),
        mensaje_original=raw_text,
    )