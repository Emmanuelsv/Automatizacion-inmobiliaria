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
    tipo_inmueble: list[str] | None = None
    habitaciones_min: int | None = None
    area_min: int | None = None
    administracion_max: int | None = None
    parqueaderos_min: int | None = None
    vestieres_min: int | None = None
    asesor: str | None = None
    cliente: str | None = None
    telefono: str | None = None
    caracteristicas: list[str] = field(default_factory=list)
    es_renta_corta: bool = False
    inmueble_nuevo: bool = False
    bathrooms_min: int | None = None
    piso_categoria: str | None = None
    piso_maximo: int | None = None
    piso_minimo: int | None = None
    independiente: bool = False
    mensaje_original: str = ""


def _replace_spanish_numbers(text: str) -> str:
    NUM_WORDS = {
        r"\bdos\b": "2", r"\btres\b": "3", r"\bcuatro\b": "4",
        r"\bcinco\b": "5", r"\bseis\b": "6", r"\bsiete\b": "7",
        r"\bocho\b": "8", r"\bnueve\b": "9", r"\bdiez\b": "10",
    }
    for pattern, digit in NUM_WORDS.items():
        text = re.sub(pattern, digit, text, flags=re.IGNORECASE)
    return text


def is_solicitud(text: str) -> bool:
    normalized = normalize_text(text)
    
    keywords = [
        "solicitud de propiedad", "solicitud de inmueble", "se busca", "busco",
        "necesito", "cliente busca", "cliente necesita", "requiero", "presupuesto",
        "ubicacion deseada", "solicitud", "solicito", "modo de pago",
        "credito hipotecario", "credito bancario", "credito", "pago de contado",
        "pago contado", "leasing", "arrendamiento con opcion de compra",
        "leasing habitacional", "quiero apartamento", "quiero un apartamento",
        "quiero apto", "quiero un apto", "quiero casa", "quiero una casa",
        "cliente quiere casa", "cliente quiere una casa", "cliente quiere apartamento",
        "cliente quiere un apartamento"
    ]
    
    keywords_oferta = [
        "oferta de propiedad", "oferta de inmueble", "venta", "ofrezco",
        "disponible", "ofertar", "oferta", "ofrecemos", "para colegaje",
        "vendemos", "en venta", "se vende", "se ofrece", "vendo" ,"arriendo",
        "apto en arriendo", "casa en arriendo", "apartamento en arriendo", 
        "arriendo apartamento", "arriendo casa", "arriendo apto", 
        "arriendo inmueble", "arriendo propiedad", "para arriendo", "para arrendar", 
        "arrendar", "arrendamiento",
        "alquiler", "alquilo", "alquila", "se alquila", "se alquiler",
        "para alquiler", "en alquiler",
    ]
     
    # Utilizamos _word_match para garantizar que las palabras se evalúen completas
    keyword_oferta_count = sum(1 for ko in keywords_oferta if _word_match(ko, normalized))
    keyword_count = sum(1 for kw in keywords if _word_match(kw, normalized))
    
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

    has_solicitud_fuerte = any(
        _word_match(kw, normalized)
        for kw in ["busco", "se busca", "necesito", "solicitud", "solicito",
                   "cliente busca", "cliente necesita", "requiero"]
    )

    has_rental = keyword_oferta_count >= 1 and any(
        _word_match(kw, normalized)
        for kw in ["arriendo", "arrendar", "arrendamiento", "para arriendo",
                   "para arrendar", "canon", "arrendador",
                   "apto en arriendo", "casa en arriendo", "apartamento en arriendo",
                   "arriendo apartamento", "arriendo casa", "arriendo apto",
                   "arriendo inmueble", "arriendo propiedad", "casa lote en arriendo",
                   "lote en arriendo", "lote para arriendo", "finca en arriendo",
                   "finca para arriendo",
                   "alquiler", "alquilo", "alquila", "se alquila", "se alquiler",
                   "para alquiler", "en alquiler"]
    )

    if has_url:
        return False
    elif has_rental:
        return False
    elif keyword_oferta_count >= 1 and not has_solicitud_fuerte:
        return False
    elif has_solicitud_fuerte and has_price:
        return True
    else:
        return keyword_count >= 1 and has_price


def es_renta_corta(text: str) -> bool:
    normalized = normalize_text(text)
    keywords = [
        "rentas cortas", "renta corta", "corta estancia",
        "renta temporal", "rentas temporales", "alquiler temporal",
        "alquiler corto", "alquiler por dias", "alquiler por meses",
        "alquiler mensual", "arriendo temporal", "arriendo por dias",
        "arriendo mensual", "arriendo por meses", "para airbnb",
        "inversion en renta", "inversion en alquiler",
        "inversion temporal", "inversion corta",
    ]
    return any(_word_match(kw, normalized) for kw in keywords)


def inmueble_nuevo(text: str) -> bool:
    normalized = normalize_text(text)
    keywords = [
        "nada viejo", "nada antiguo", "recien construido",
        "estrenar", "primer dueno", "primer dueño", "primer propietario",
        "edificio nuevo", "construccion reciente", "obra nueva",
        "entrega inmediata", "proyecto nuevo",
    ]
    if any(_word_match(kw, normalized) for kw in keywords):
        return True
    if _word_match("nuevo", normalized):
        template_prefixes = ["pedido", "mensaje", "solicitud", "cliente", "formato"]
        after = re.search(r"(?<!\w)nuevo\s+(\w+)", normalized)
        if after and after.group(1) in template_prefixes:
            return False
        return True
    return False


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


def extract_property_type(text: str) -> list[str] | None:
    normalized = normalize_text(text)
    found = set()

    # 1. Frases compuestas: interceptar y limpiar el texto
    if re.search(r"lote\s+(?:para\s+)?(?:construir\s+)?(?:una\s+)?casa", normalized):
        found.add("Lote")
        normalized = re.sub(r"lote\s+(?:para\s+)?(?:construir\s+)?(?:una\s+)?casa", "", normalized)

    # "casa lote", "casa con lote", "casa con terreno" → Casa de Campo (Wasi type 11)
    if re.search(r"casa\s+(?:con\s+)?(?:lote|terreno)", normalized):
        found.add("Casa de Campo")
        normalized = re.sub(r"casa\s+(?:con\s+)?(?:lote|terreno)", "", normalized)

    # "casa de campo", "casa campestre" → Casa de Campo
    if re.search(r"casa\s+de\s+campo|casa\s+campestre", normalized):
        found.add("Casa de Campo")
        normalized = re.sub(r"casa\s+de\s+campo|casa\s+campestre", "", normalized)

    # "casa" + "excelente/amplio/gran lote" → Casa de Campo (sin necesidad de "con")
    if re.search(r"(?:^|\W)casa(?:\W|$)", normalized) and re.search(
        r"(?:excelente|amplio|buen|gran|grande|hermoso|bonito|privado|maravilloso|increible)\s+lote", normalized,
    ):
        found.discard("Casa")
        found.add("Casa de Campo")
        normalized = re.sub(r"\bcasa\b", "", normalized)
        normalized = re.sub(r"(?:excelente|amplio|buen|gran|grande|hermoso|bonito|privado|maravilloso|increible)\s+lote", "", normalized)

    # 2. Limpiar "lote" descriptivo standalone (sin "casa") para que no se confunda con tipo Lote
    normalized = re.sub(
        r"(?:excelente|amplio|buen|gran|grande|hermoso|bonito|privado|maravilloso|increible)\s+lote",
        "", normalized, flags=re.IGNORECASE,
    )

    # 3. Búsqueda estándar (ahora segura contra cruces)
    types = [
        (["apartamento", "apto", "apartaestudio"], "Apartamento"),
        (["casa"], "Casa"),
        (["local comercial", "local", "locales"], "Local"),
        (["oficina", "oficinas", "consultorio", "consultorios"], "Oficina"),
        (["bodega", "bodegas"], "Bodega"),
        (["lote", "terreno", "lotes"], "Lote"),
        (["finca"], "Finca"),
    ]

    for patterns, prop_type in types:
        for pattern in patterns:
            if _word_match(pattern, normalized):
                found.add(prop_type)
                break

    return list(found) if found else None


def extract_rooms(text: str) -> int | None:
    # Spanish number words
    word_to_num = {
        "una": 1, "un": 1, "uno": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
        "diez": 10,
    }

    # "tres habitaciones", "dos alcobas" etc.
    for word, num in word_to_num.items():
        if re.search(rf"\b{word}\s+(?:habitacion|hab|alcoba|cuarto)", text, re.IGNORECASE):
            if 1 <= num <= 10:
                return num

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


def extract_bathrooms(text: str) -> int | None:
    range_match = re.search(
        r"(\d+)\s*(?:o|a|y)\s*(\d+)\s*(?:ba[ñn]o|baños|banos)",
        text, re.IGNORECASE,
    )
    if range_match:
        baths = min(int(range_match.group(1)), int(range_match.group(2)))
        if 1 <= baths <= 10:
            return baths

    patterns = [
        r"(\d+)\s*(?:ba[ñn]o|baños|banos)\s*(?:o\s*m[aá]s)?",
        r"(?:ba[ñn]o|baños|banos)\s*(?:m[ií]nimo|min|desde)?\s*[:.]?\s*(\d+)",
        r"desde\s*(\d+)\s*(?:ba[ñn]o|baños|banos)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            baths = int(match.group(1))
            if 1 <= baths <= 10:
                return baths

    # "N con baño" — private bathrooms per bedroom, add 1 for social/service
    con_bano = re.search(r"(\d+)\s+con\s+(?:ba[ñn]o|baños|banos)", text, re.IGNORECASE)
    if con_bano:
        baths = int(con_bano.group(1)) + 1
        if 2 <= baths <= 11:
            return baths

    has_cada_una_con_bano = re.search(r"cada\s+una?\s+con\s+ba[ñn]o", text, re.IGNORECASE)
    has_bano_social = re.search(r"ba[ñn]o\s+social", text, re.IGNORECASE)

    if has_cada_una_con_bano:
        rooms = extract_rooms(text)
        if rooms is not None:
            return rooms + 1

    return None


def extract_area(text: str) -> int | None:
    patterns = [
        r"(?:area|área)\s*(?:desde|m[ií]nim[ao]|min|entre)\s*[:.]?\s*(\d+)\s*(?:m2|m²|mts?|metros)",
        r"(?:minimo|min|m[ií]nim[ao])\s*(\d+)\s*(?:m2|m²|mts?|metros)",
        r"desde\s*(\d+)\s*(?:m2|m²|mts?|metros)",
        r"m[aá]s\s*de\s*(\d+)\s*(?:m2|m²|mts?|metros)",
        r"entre\s*(\d+)\s*y\s*\d+\s*(?:m2|m²|mts?|metros)",
        r"(\d+)\s*[-–]\s*(\d+)\s*(?:m2|m²|mts?|metros)",
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
        (r"administraci[oó]n\s*(?:m[aá]xim[ao]?|max|hasta|:)?\s*[:.]?\s*\$?\s*(\d{1,3}(?:\.\d{3})*)", False),
        (r"admin\s*(?:m[aá]xim[ao]?|max|:)?\s*[:.]?\s*\$?\s*(\d{1,3}(?:\.\d{3})*)", False),
        (r"administraci[oó]n\s+no\s+superior\s+a\s*\$?\s*(\d{1,3}(?:\.\d{3})*)\s*(mil\b)?", True),
        (r"admin\s+no\s+superior\s+a\s*\$?\s*(\d{1,3}(?:\.\d{3})*)\s*(mil\b)?", True),
        (r"administraci[oó]n\s+m[aá]xim[ao]?\s+entre\s*\$?\s*\d{1,3}(?:\.\d{3})*\s*y\s*\$?\s*(\d{1,3}(?:\.\d{3})*)\s*(mil\b)?", True),
        (r"admin\s+m[aá]xim[ao]?\s+entre\s*\$?\s*\d{1,3}(?:\.\d{3})*\s*y\s*\$?\s*(\d{1,3}(?:\.\d{3})*)\s*(mil\b)?", True),
    ]

    for pattern, check_mil in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fee = int(match.group(1).replace(".", ""))
            if check_mil and match.group(2):
                fee *= 1000
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


def extract_parking_min(text: str) -> int | None:
    normalized = normalize_text(text)
    m = re.search(r"(\d+)\s*(?:parqueadero|parqueaderos|garaje|garajes|parking)", normalized)
    if m:
        val = int(m.group(1))
        if 1 <= val <= 10:
            return val
    if re.search(r"\bdos?\b.*parqueadero|\bpar\b.*parqueadero", normalized):
        return 2
    if re.search(r"(?:requiere|necesita|debe\s+tener|con)\s+parqueadero|parqueadero\s*$", normalized):
        return 1
    return None


def extract_vestieres(text: str) -> int | None:
    normalized = normalize_text(text)
    m = re.search(r"(\d+)\s*(?:vestier|vestieres|vestidor|vestidores|vetier|vetieres|walk\s*in|walkin)", normalized)
    if m:
        val = int(m.group(1))
        if 1 <= val <= 10:
            return val
    # "cada una con vestier" → inferir desde habitaciones
    if re.search(r"cada\s+una?\s+con.*vestier", normalized, re.IGNORECASE):
        rooms = extract_rooms(text)
        if rooms is not None and 1 <= rooms <= 10:
            return rooms
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
        (r"primer\s*piso|(?<!\d)piso\s*1(?!\d)", "Primer piso"),
        (r"duplex|d[uú]plex", "Dúplex"),
        (r"penthouse|pent\s*house", "Penthouse"),
        (r"esquinero", "Esquinero"),
        (r"remodelado", "Remodelado"),
        (r"estrenar", "Para estrenar"),
        (r"modern[oa]", "Moderno"),
        (r"cuarto\s*[uú]til", "Cuarto útil"),
    ]

    for pattern, label in feature_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = match.start()
            prefix = text[max(0, start - 20):start].strip()
            if re.search(r'(?:^|\s)(?:no|sin|excepto|menos|nunca|evitar|excluye)\s*$', prefix, re.IGNORECASE):
                continue
            features.append(label)
            break

    # "buenas zonas comunes" → implícitamente requiere piscina
    if re.search(r"zonas?\s+comunes|buenas?\s+zonas?\s+comunes", text, re.IGNORECASE):
        if "Piscina" not in features:
            features.append("Piscina")

    return features


def extract_floor_level(text: str) -> tuple[str | None, int | None, int | None]:
    normalized = normalize_text(text)
    categoria = None
    piso_max = None
    piso_min = None

    if re.search(r"piso\s+bajo|pisos?\s+bajos?|nivel\s+bajo|niveles?\s+bajos?", normalized):
        categoria = "bajo"

    if re.search(r"piso\s+medio|pisos?\s+medi(os|o)|nivel\s+medio|niveles?\s+medi(os|o)", normalized):
        categoria = "medio"

    if re.search(r"piso\s+alto|pisos?\s+altos?|nivel\s+alto|niveles?\s+altos?|ultimo\s+piso|penthouse", normalized):
        categoria = "alto"

    # "piso del N al M" → piso_min=N, piso_max=M
    m = re.search(r"piso\s+del\s*(\d+)\s+al\s*(\d+)", normalized)
    if m:
        piso_min = int(m.group(1))
        piso_max = int(m.group(2))

    # maximo piso/nivel → piso_max (solo si no se fijo ya por rango)
    m = re.search(
        r"(?:maximo|max)\s+(?:piso|nivel)\s*(\d+)|(?:piso|nivel)\s+(?:maximo|max)\s*(\d+)"
        r"|(?:maximo|max)\s*(\d+)\s*(?:pisos?|niveles?)",
        normalized,
    )
    if m:
        for g in m.groups():
            if g is not None:
                piso_max = int(g)
                break

    m = re.search(r"(\d+)\s+o\s+inferior|(\d+)\s+o\s+menos", normalized)
    if m:
        piso_max = int(m.group(1) or m.group(2))

    # minimo piso/nivel → piso_min
    m = re.search(
        r"(?:minimo|min)\s+(?:piso|nivel)\s*(\d+)|(?:piso|nivel)\s+(?:minimo|min)\s*(\d+)"
        r"|(?:minimo|min)\s*(\d+)\s*(?:pisos?|niveles?)",
        normalized,
    )
    if m:
        for g in m.groups():
            if g is not None:
                piso_min = int(g)
                break

    m = re.search(r"(\d+)\s+o\s+superior|(\d+)\s+o\s+mas", normalized)
    if m:
        piso_min = int(m.group(1) or m.group(2))

    # "del piso N en adelante" → piso_min = N
    if piso_min is None:
        m = re.search(r"del\s+piso\s*(\d+)\s+(en\s+)?adelante", normalized)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 100:
                piso_min = val

    # N (pisos|niveles) suelto sin prefijo → piso_max (menos o igual cumple)
    if piso_max is None:
        m = re.search(r"(\d+)\s*(?:niveles?|pisos?)\b", normalized)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 30:
                piso_max = val

    # "un solo nivel", "un solo piso", "un nivel", "1 solo nivel" → single level
    if piso_max is None:
        if re.search(r"(?:^|\s)(?:un|1)\s+solo\s+(?:nivel|piso)", normalized):
            piso_max = 1
    if piso_min is None and piso_max == 1:
        piso_min = 1

    return categoria, piso_min, piso_max


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


def extract_independiente(text: str) -> bool:
    normalized = normalize_text(text)
    # "independiente" como palabra suelta
    if _word_match("independiente", normalized):
        return True
    # "no unidad", "sin unidad"
    if re.search(r"(?:no|sin)\s+unidad", normalized):
        return True
    # "no quiere unidad"
    if re.search(r"no\s+quiere\s+unidad", normalized):
        return True
    # "no le/me/te gusta la unidad", "no gusta unidad"
    if re.search(r"no\s+(?:(?:le|me|te)\s+)?gusta\s+(?:la\s+)?unidad", normalized):
        return True
    # "nole gusta", "nolegusta", "no legusta" (sin espacio entre "no" y "le")
    if re.search(r"no\s*le\s*gusta\s+unidad", normalized):
        return True
    # "excluye unidad", "excepto unidad", "evitar unidad" (pero NO "no excluye unidad")
    if re.search(r"(?<!\bno\s)(?:excluye?|excepto|evitar)\s+unidad", normalized):
        return True
    # "que no sea unidad", "que no sea conjunto", "que no sea urbanizacion"
    if re.search(r"que\s+no\s+sea\s+(?:unidad|conjunto|urbanizacion)", normalized):
        return True
    return False


def parse_message(raw_text: str) -> SolicitudParseada:
    text_no_emojis = remove_emojis(raw_text)
    numeric_text = _replace_spanish_numbers(raw_text)  # "tres baños" → "3 baños"

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
            is_generic = kw in ["viva", "exito", "tesoro", "fabricato", "oviedo", "unicentro", "cerca al parque"]
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

    # Si todas las ubicaciones de una ciudad fueron excluidas, preservar la ciudad
    ciudades_mencionadas = {u.ciudad for u in todas_ubicaciones if u.ciudad}
    ciudades_con_barrio_restante = {u.ciudad for u in ubicaciones if u.ciudad}
    for ciudad in ciudades_mencionadas:
        if ciudad not in ciudades_con_barrio_restante and not any(
            u.barrio != ciudad and u.ciudad == ciudad for u in ubicaciones
        ):
            ubicaciones.append(Location(barrio=ciudad, ciudad=ciudad))

    # 4. Detectar "no loma" / "parte plana" / "zona plana" → redirigir a zona plana
    norm = normalize_text(raw_text)
    if re.search(r"no\s+(?:en\s+)?loma|parte\s+(?:plana|baja)|solo\s+parte\s+plana|zona\s+plana", norm):
        ciudades_a_mapa = {
            "medellin": "Medellín", "sabaneta": "Sabaneta", "itagui": "Itagüí",
            "itagüí": "Itagüí", "estrella": "La Estrella", "envigado": "Envigado",
            "bello": "Bello",
        }
        for key, ciudad in ciudades_a_mapa.items():
            if key in norm:
                zplana_key = f"zona plana {ciudad}".lower()
                if zplana_key not in {normalize_text(u.barrio) for u in ubicaciones}:
                    ubicaciones.append(Location(barrio=f"Zona Plana {ciudad}", ciudad=ciudad))

    piso_cat, piso_min, piso_max = extract_floor_level(numeric_text)
    independiente = extract_independiente(raw_text)

    return SolicitudParseada(
        es_solicitud=is_solicitud(raw_text),
        ubicaciones=ubicaciones,
        ubicaciones_excluidas=excluidas,
        presupuesto=extract_budget(raw_text),
        tipo_inmueble=extract_property_type(text_no_emojis),
        habitaciones_min=extract_rooms(numeric_text),
        area_min=extract_area(numeric_text),
        bathrooms_min=extract_bathrooms(numeric_text),
        administracion_max=extract_admin_fee(numeric_text),
        parqueaderos_min=extract_parking_min(numeric_text),
        vestieres_min=extract_vestieres(numeric_text),
        asesor=extract_advisor(raw_text),
        cliente=extract_client(raw_text),
        telefono=extract_phone(raw_text),
        caracteristicas=extract_features(raw_text),
        es_renta_corta=es_renta_corta(raw_text),
        inmueble_nuevo=inmueble_nuevo(raw_text),
        mensaje_original=raw_text,
        piso_categoria=piso_cat,
        piso_maximo=piso_max,
        piso_minimo=piso_min,
        independiente=independiente,
    )

def optimizar_ubicaciones(ubicaciones: list) -> list:
    """
    Remueve las macro-zonas amplias (ej. El Poblado) si en la misma solicitud
    se detecta un sector o barrio específico que pertenece a ella (ej. Santa María de los Ángeles).
    """
    # Definimos la jerarquía local (aquí puedes dejar los nombres sin tildes o con tildes, da igual)
    JERARQUIA_ZONAS = {
        "el poblado": [
            "castropol", "provenza", "manila", "patio bonito", "los balsos", 
            "alejandria", "el tesoro", "las lomas", "san lucas", "la calera", 
            "el campestre", "santa maria de los angeles", "lleras", "astorga",
            "poblado bajo", "poblado alto",
        ],
        "laureles": [
            "conquistadores", "estadio", "simon bolivar", "nutibara", 
            "florida nueva", "san joaquin", "la castellana",
        ],
        "belen": [
            "rosales", "loma de los bernal", "granada", "rodeo alto", "fatima"
        ],
        "envigado": [
            "loma de las brujas", "las brujas", "zuñiga", "cumbres", 
            "el escobero", "la sebastiana", "alcala"
        ]
    }
    
    # 1. Normalizamos TODOS los barrios extraídos del mensaje (quita tildes y pasa a minúsculas)
    barrios_extraidos = {normalize_text(u.barrio) for u in ubicaciones}
    macro_zonas_a_eliminar = set()
    
    # 2. Evaluamos la jerarquía normalizando dinámicamente ambas partes
    for macro, sub_sectores in JERARQUIA_ZONAS.items():
        macro_norm = normalize_text(macro)
        
        if macro_norm in barrios_extraidos:
            # Si el equivalente normalizado de algún sub-sector está en los barrios extraídos
            if any(normalize_text(sub) in barrios_extraidos for sub in sub_sectores):
                macro_zonas_a_eliminar.add(macro_norm)
                
    # 3. Retornamos filtrando las macro-zonas comparando también bajo normalización
    return [u for u in ubicaciones if normalize_text(u.barrio) not in macro_zonas_a_eliminar]