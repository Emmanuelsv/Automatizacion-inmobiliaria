"""
Matching de propiedades vs solicitud con scoring por prioridad:
1. Precio (obligatorio) — hasta 30 pts por proximidad
2. Ubicación (ciudad + barrio) — hasta 30 pts (ciudad es filtro estricto)
3. Habitaciones — 20 pts
4. Área — 15 pts
5. Administración — 10 pts
6. Tipo de inmueble — 20 pts (filtro estricto si se especifica; admite uno o varios tipos, ej. "apartamento o casa")
7. Características — 5 pts c/u
8. Base por pasar todos los filtros — 5 pts

REGLAS DE UBICACIÓN (ESTRICTAS):
- Si el usuario solicita una ciudad (Medellín, Envigado, Sabaneta, etc.),
  se descartan todas las propiedades de otros municipios. Sin excepción.
- Si el usuario solicita un barrio específico, se descartan las propiedades
  cuya zona/título no coincida con ese barrio (o sus alias de zona).
"""
import re  # <-- IMPORTANTE: Añadido para procesar las expresiones regulares de las unidades
from app.normalizer import normalize_text
from app.parser import SolicitudParseada
from app.wasi_client import CITY_ID_MAP
from app.locations import BARRIOS, PUNTOS_INTERES  # <-- Importamos PUNTOS_INTERES

# Barrios que componen cada zona conceptual de El Poblado y Envigado.
ZONE_ALIASES: dict[str, list[str]] = {
    # === EL POBLADO (Medellín) ===
    "poblado alto": [
        "altos del poblado", "los balsos", "loma de los balsos",
        "las lomas", "el tesoro", "patio bonito", "manila",
        "el castillo", "alejandria", "los naranjos", "loma del indio",
        "cola del zorro", "la tomatera", "el campestre", "san michel",
        "villa carlota", "castropol", "loma de los parra", "loma de los gonzalez",
        "el diamante", "santa maria de los angeles",
    ],
    "poblado bajo": [
        "san lucas", "la florida", "la aguacatala", "lalinde",
        "la visitacion", "astorga", "provenza", "los gonzalez",
        "alejandria", "parque lleras", "castropol",
        "santa maria de los angeles",
    ],
    # === ENVIGADO ===
    "envigado alto": [
        "loma del chocho", "el chocho",
        "el esmeraldal", "esmeraldal", "loma del esmeraldal",
        "loma de los balsos", "los balsos", "balsos",
        "las brujas", "loma de las brujas", "loma de brujas",
        "loma del atravesado", "atravesado",
        "escobero", "el escobero", "loma del escobero",
        "el salado", "salado",
        "las palmas", "palmas envigado",
        "alto de palmas", "alto de las palmas",
        "loma del barro", "barro",
        "cumbres", "las cumbres",
        "la intermedia", "intermedia",
    ],
    "envigado centro": [
        "zona centro", "centro envigado", "envigado centro",
        "Obrero", "el obrero", "barrio obrero",
        "mesa", "la mesa", "bucarest"
    ],

    "envigado bajo": [
        "zuñiga", "bosques de zuñiga", "bosque de zuniga", "zuniga",
        "la frontera", "frontera", "el portal", "el dorado", "otra parte",
        "la abadia", "abadia", "la abadía", "abadía",
        "el campestre", "campestre",
        "santa maria de los angeles", "santa maria", "los angeles",
        "las orquideas", "orquideas",
        "las antillas", "la paz", "la sebastiana",
        "alcala", "jardin", "jardines", "jardin de envigado",
        "san marcos", "mesa",
        "zona centro", "centro envigado",
        "milan", "pontevedra", "san jose",
    ],
    "viva envigado": [
        "viva envigado", "centro comercial viva envigado", "cc viva envigado", "exito envigado",
        "alcalá", "alcala", "jardín", "jardin", "jardines", "jardín de envigado",
        "san marcos", "mesa", "la mesa", "oasis", "primavera","la primavera", 
        "pontevedra", "la magnolia", "magnolia", "el dorado", "dorado", 
    ],
}

# --- NUEVO: Cargar expansiones de POIs automáticamente (Protegiendo tus alias manuales) ---
for poi_id, data in PUNTOS_INTERES.items():
    poi_name_norm = normalize_text(data["nombre"])
    if poi_name_norm not in ZONE_ALIASES:  # <-- ESTA LÍNEA ES CRUCIAL
        ZONE_ALIASES[poi_name_norm] = [normalize_text(b) for b in data["barrios_cercanos"]]

# Mapeo de nombre de POI normalizado a sus palabras clave para búsquedas flexibles en descripción
POI_MATCH_KEYWORDS: dict[str, list[str]] = {}
for poi_id, data in PUNTOS_INTERES.items():
    poi_name_norm = normalize_text(data["nombre"])
    POI_MATCH_KEYWORDS[poi_name_norm] = [normalize_text(kw) for kw in data["keywords"]]

def match_properties(
    properties: list[dict],
    solicitud: SolicitudParseada,
) -> list[dict]:
    if not properties:
        return []

    results: list[dict] = []

    # =====================================================================
    # 0. DETECTAR SI EL ASESOR BUSCA UNA UNIDAD/EDIFICIO ESPECÍFICO
    # Extraemos el nombre una sola vez para no repetir el proceso en cada ciclo
    # =====================================================================
    msg_normalized = normalize_text(solicitud.mensaje_original)
    unidades_detectadas = re.findall(
        r'(?:unidad|edificio|conjunto|urbanizaci[oó]n|torre)(?:\s+(?:residencial|cerrada|abierta|campestre))?\s+([a-z0-9]+)', 
        msg_normalized
    )
    # Agregamos las palabras de amenidades comunes para que no las tome como nombres de unidades
    exclusiones = {
        'de', 'con', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 
        'cerrada', 'abierta', 'residencial', 'campestre',
        'piscina', 'gimnasio', 'gym', 'porteria', 'ascensor', 
        'parqueadero', 'zonas', 'salon', 'juegos', 'cancha', 'social'
    }
    unidades_reales = [u for u in unidades_detectadas if u not in exclusiones]

    for prop in properties:
        score = 0
        passes = True

        # =====================================================================
        # FILTRO ESTRICTO: Si especificó unidad y el inmueble no la tiene, se descarta
        # =====================================================================
        if unidades_reales:
            searchable_prop = normalize_text(" ".join(filter(None, [
                str(prop.get("title") or ""),
                str(prop.get("description") or ""),
                str(prop.get("features") or ""),
                str(prop.get("amenities") or ""),
            ])))
            
            # Si el nombre de la unidad no está en NINGÚN lado de la propiedad, la saltamos
            if not any(u in searchable_prop for u in unidades_reales):
                continue

        # === 0. EXCLUSIÓN DE ZONAS (filtro estricto) ===
        if solicitud.ubicaciones_excluidas:
            excl_keys: set[str] = set()
            for u in solicitud.ubicaciones_excluidas:
                nb = normalize_text(u.barrio)
                excl_keys.add(nb)
                for k, d in BARRIOS.items():
                    if normalize_text(d["nombre"]) == nb:
                        excl_keys.add(normalize_text(k))
            zone_text_excl = normalize_text(" ".join(filter(None, [
                str(prop.get("zone_label") or ""),
                str(prop.get("neighborhood") or ""),
                str(prop.get("zone") or ""),
                str(prop.get("title") or ""),
            ])))
            if any(k in zone_text_excl for k in excl_keys if k):
                continue

        # === 1. PRECIO (filtro obligatorio + hasta 30 pts) ===
        price = _get_number(prop, ["sale_price", "price", "valor_venta", "precio_venta", "precio"])
        if solicitud.presupuesto.min_price and solicitud.presupuesto.max_price and price > 0:
            if price < solicitud.presupuesto.min_price or price > solicitud.presupuesto.max_price:
                passes = False
            elif solicitud.presupuesto.exact and solicitud.presupuesto.exact > 0:
                diff = abs(price - solicitud.presupuesto.exact)
                proximity = 1 - (diff / solicitud.presupuesto.exact)
                score += proximity * 30

        if not passes:
            continue

        # === 2. UBICACIÓN (ciudad estricta + hasta 30 pts totales) ===

        # 2a. CIUDAD: filtro DURO. Si el usuario pidió ciudades específicas,
        # se descartan propiedades de otros municipios. No hay excepciones.
        if solicitud.ubicaciones:
            requested_city_ids = {
                CITY_ID_MAP[u.ciudad]
                for u in solicitud.ubicaciones
                if u.ciudad in CITY_ID_MAP
            }
            requested_city_names = {
                normalize_text(u.ciudad)
                for u in solicitud.ubicaciones
                if u.ciudad
            }

            if requested_city_ids or requested_city_names:
                prop_city_id = _get_number(prop, ["id_city"])
                prop_city_name = normalize_text(str(
                    prop.get("city")
                    or prop.get("city_label")
                    or prop.get("ciudad")
                    or ""
                ))

                city_match = False

                # Coincidencia por ID (más confiable)
                if requested_city_ids and prop_city_id:
                    if int(prop_city_id) in requested_city_ids:
                        city_match = True

                # Coincidencia por nombre (fallback)
                if not city_match and requested_city_names and prop_city_name:
                    if prop_city_name in requested_city_names:
                        city_match = True

                # Último fallback: si la propiedad no trae ningún campo de ciudad,
                # buscar el nombre de la ciudad solicitada en zone_label/título.
                if not city_match and not prop_city_id and not prop_city_name:
                    zone_text = normalize_text(" ".join(filter(None, [
                        str(prop.get("zone_label") or ""),
                        str(prop.get("title") or ""),
                    ])))
                    if any(c in zone_text for c in requested_city_names if c):
                        city_match = True

                if not city_match:
                    # Otra ciudad → descarta sin importar nada más.
                    continue

                # Ciudad correcta: 15 pts base por ubicación
                score += 15

        # 2b. BARRIO: filtro estricto si se pidió uno o un POI + 15 pts adicionales
        if solicitud.ubicaciones:
            specific_barrios = [
                normalize_text(u.barrio)
                for u in solicitud.ubicaciones
                if u.barrio and normalize_text(u.barrio) != normalize_text(u.ciudad)
            ]
            
            # --- 🛡️ SALVAGUARDA ABSOLUTA CONTRA ERRORES DEL PARSER/IA ---
            if solicitud.mensaje_original:
                msg_norm = normalize_text(solicitud.mensaje_original)
                # Si el cliente escribió "viva" en alguna parte pero la IA no lo procesó en el barrio
                if any(kw in msg_norm for kw in ["viva envigado", "cc viva", "viva"]):
                    if "viva envigado" not in specific_barrios:
                        specific_barrios.append("viva envigado")
            # ------------------------------------------------------------

            if specific_barrios:
                # Expandir conceptos usando ÚNICAMENTE tus alias directos
                expanded = []
                for b in specific_barrios:
                    expanded.append(b)
                    expanded.extend(ZONE_ALIASES.get(b, []))

                zone_fields = normalize_text(" ".join(filter(None, [
                    str(prop.get("zone_label") or ""),
                    str(prop.get("neighborhood") or ""),
                    str(prop.get("zone") or ""),
                ])))
                title = normalize_text(str(prop.get("title", "")))
                description = normalize_text(str(prop.get("description", "")))

                # Paso 1: zone_fields contra todos los barrios expandidos autorizados por ti.
                zone_match = bool(zone_fields) and any(b in zone_fields for b in expanded if b)

                # Paso 2: título contra solo los barrios pedidos DIRECTAMENTE
                title_match = any(b in title for b in specific_barrios if b)

                # Paso 3: Búsqueda flexible por palabras clave de POIs
                poi_match = False
                for b in specific_barrios:
                    if b in POI_MATCH_KEYWORDS:
                        if any(kw in title or kw in description for kw in POI_MATCH_KEYWORDS[b] if kw):
                            poi_match = True
                            break

                matches = zone_match or title_match or poi_match

                if matches:
                    score += 15
                    if title_match or poi_match:
                        score += 5
                else:
                    # Si no coincide con "viva envigado" ni sus barrios colindantes, se descarta la propiedad
                    if zone_fields or title or description:
                        continue

        # === 3. HABITACIONES (20 pts) ===
        rooms = _get_number(prop, ["rooms", "bedrooms", "habitaciones", "alcobas", "num_rooms", "num_bedrooms"])
        if solicitud.habitaciones_min:
            if rooms < solicitud.habitaciones_min:
                passes = False
            else:
                score += 20

        if not passes:
            continue

        # === 4. ÁREA (15 pts) ===
        area = _get_number(prop, ["area", "built_area", "area_construida", "area_total", "metros"])
        if solicitud.area_min:
            if area < solicitud.area_min:
                passes = False
            else:
                score += 15

        if not passes:
            continue

        # === 5. ADMINISTRACIÓN (10 pts) ===
        admin_fee = _get_number(prop, ["administration", "admin_fee", "administracion"])
        if solicitud.administracion_max and admin_fee > 0:
            if admin_fee > solicitud.administracion_max:
                passes = False
            else:
                score += 10

        if not passes:
            continue

  

# === 6. TIPO DE INMUEBLE (20 pts) ===
        prop_type = str(prop.get("property_type", prop.get("tipo", prop.get("property_type_label", "")))).lower()
        prop_type_id = int(_get_number(prop, ["id_property_type"]))
        
        # Si la solicitud tiene tipos definidos, validamos contra la lista
        if solicitud.tipo_inmueble:
            from app.wasi_client import PROPERTY_TYPE_MAP  # Importación local para resolver IDs
            
            # Aseguramos que solicitud.tipo_inmueble sea iterable
            tipos_solicitados = solicitud.tipo_inmueble if isinstance(solicitud.tipo_inmueble, list) else [solicitud.tipo_inmueble]
            
            # Traducimos los tipos de texto ("Apartamento") a sus IDs correspondientes de Wasi (2)
            ids_solicitados = [PROPERTY_TYPE_MAP[t] for t in tipos_solicitados if t in PROPERTY_TYPE_MAP]
            
            # Verificamos si el tipo del inmueble coincide por texto O por su ID de Wasi
            es_valido = any(t.lower() in prop_type for t in tipos_solicitados) or (prop_type_id in ids_solicitados)
            
            if not es_valido:
                continue # Descartamos si no es ninguno de los tipos buscados
            else:
                score += 20

        # === 7. CARACTERÍSTICAS (5 pts c/u, bono — nunca descarta) ===
        for caracteristica in solicitud.caracteristicas:
            if _has_feature(prop, caracteristica):
                score += 5

        # === 8. BASE por pasar todos los filtros (5 pts) ===
        score += 5

        result = dict(prop)
        result["match_score"] = round(score)
        results.append(result)

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results


def _has_feature(prop: dict, caracteristica: str) -> bool:
    norm = normalize_text(caracteristica)
    searchable = normalize_text(" ".join(filter(None, [
        str(prop.get("title") or ""),
        str(prop.get("zone_label") or ""),
        str(prop.get("description") or ""),
        str(prop.get("features") or ""),
        str(prop.get("amenities") or ""),
    ])))
    if norm in searchable:
        return True
    if "parqueadero" in norm and _get_number(prop, ["parking"]) > 0:
        return True
    return False


def _get_number(prop: dict, keys: list[str]) -> float:
    for key in keys:
        val = prop.get(key)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                continue
    return 0