"""
Matching de propiedades vs solicitud con filtrado booleano estricto:
Cada criterio es un filtro duro (pasa/no pasa). Sin sistema de puntos.

REGLAS DE UBICACIÓN (ESTRICTAS):
- Si el usuario solicita una ciudad (Medellín, Envigado, Sabaneta, etc.),
  se descartan todas las propiedades de otros municipios. Sin excepción.
- Si el usuario solicita un barrio específico, se descartan las propiedades
  cuya zona/título no coincida con ese barrio (o sus alias de zona).
"""
import re  # <-- IMPORTANTE: Añadido para procesar las expresiones regulares de las unidades
from datetime import date
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
    # === ZONAS PLANAS (opuesto a loma) ===
    "zona plana medellin": [
        "laureles", "estadio", "san joaquin", "bolivariana", "carlos e restrepo",
        "aeroparque juan pablo ii", "belen fatima", "belen rosales", "rosales",
        "nueva villa de aburra", "manila", "astorga", "barrio colombia",
        "castropol", "patio bonito", "la aguacatala", "santa maria de los angeles",
    ],
    "zona plana poblado": [
        "manila", "astorga", "barrio colombia", "castropol", "patio bonito",
        "la aguacatala", "santa maria de los angeles",
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

        # === 1. PRECIO (filtro duro) ===
        price = _get_number(prop, ["sale_price", "price", "valor_venta", "precio_venta", "precio"])
        if solicitud.presupuesto.min_price and solicitud.presupuesto.max_price and price > 0:
            if price < solicitud.presupuesto.min_price or price > solicitud.presupuesto.max_price:
                continue

        # === 2. UBICACIÓN (ciudad + barrio, filtro duro) ===

        # 2a. CIUDAD: filtro DURO.
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

                if requested_city_ids and prop_city_id:
                    if int(prop_city_id) in requested_city_ids:
                        city_match = True

                if not city_match and requested_city_names and prop_city_name:
                    if prop_city_name in requested_city_names:
                        city_match = True

                if not city_match and not prop_city_id and not prop_city_name:
                    zone_text = normalize_text(" ".join(filter(None, [
                        str(prop.get("zone_label") or ""),
                        str(prop.get("title") or ""),
                    ])))
                    if any(c in zone_text for c in requested_city_names if c):
                        city_match = True

                if not city_match:
                    continue

        # 2b. BARRIO: filtro estricto si se pidió uno o un POI
        if solicitud.ubicaciones:
            specific_barrios = [
                normalize_text(u.barrio)
                for u in solicitud.ubicaciones
                if u.barrio and normalize_text(u.barrio) != normalize_text(u.ciudad)
            ]

            if solicitud.mensaje_original:
                msg_norm = normalize_text(solicitud.mensaje_original)
                if any(kw in msg_norm for kw in ["viva envigado", "cc viva", "viva"]):
                    if "viva envigado" not in specific_barrios:
                        specific_barrios.append("viva envigado")

            if specific_barrios:
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

                zone_match = bool(zone_fields) and any(b in zone_fields for b in expanded if b)
                title_match = any(b in title for b in specific_barrios if b)

                poi_match = False
                for b in specific_barrios:
                    if b in POI_MATCH_KEYWORDS:
                        if any(kw in title or kw in description for kw in POI_MATCH_KEYWORDS[b] if kw):
                            poi_match = True
                            break

                matches = zone_match or title_match or poi_match

                if not matches and (zone_fields or title or description):
                    continue

        # === 3. HABITACIONES (filtro duro) ===
        rooms = _get_number(prop, ["rooms", "bedrooms", "habitaciones", "alcobas", "num_rooms", "num_bedrooms"])
        if solicitud.habitaciones_min and rooms < solicitud.habitaciones_min:
            continue

        # === 3b. BAÑOS (filtro duro) ===
        if solicitud.bathrooms_min is not None:
            bathrooms = _get_number(prop, ["bathrooms", "baños", "banos", "num_bathrooms", "half_bathrooms"])
            if bathrooms < solicitud.bathrooms_min:
                continue

        # === 4. ÁREA (filtro duro) ===
        area = _get_number(prop, ["area", "built_area", "area_construida", "area_total", "metros"])
        if solicitud.area_min and area < solicitud.area_min:
            continue

        # === 5. ADMINISTRACIÓN (filtro duro) ===
        admin_fee = _get_number(prop, ["administration", "admin_fee", "administracion"])
        if solicitud.administracion_max and admin_fee > 0 and admin_fee > solicitud.administracion_max:
            continue

        # === 6. TIPO DE INMUEBLE (filtro duro) ===
        if solicitud.tipo_inmueble:
            from app.wasi_client import PROPERTY_TYPE_MAP

            prop_type = str(prop.get("property_type", prop.get("tipo", prop.get("property_type_label", "")))).lower()
            prop_type_id = _get_number(prop, ["id_property_type"])
            tipos_solicitados = solicitud.tipo_inmueble if isinstance(solicitud.tipo_inmueble, list) else [solicitud.tipo_inmueble]
            ids_solicitados = [PROPERTY_TYPE_MAP[t] for t in tipos_solicitados if t in PROPERTY_TYPE_MAP]

            if "Lote" not in tipos_solicitados and "Lote Comercial" not in tipos_solicitados:
                url_text = normalize_text(" ".join(filter(None, [
                    prop_type,
                    str(prop.get("url") or ""),
                    str(prop.get("link") or ""),
                ])))
                if re.search(r"(?<!\w)(lote|terreno)(?!\w)", url_text):
                    continue

            es_valido = False
            if prop_type_id and ids_solicitados:
                es_valido = int(prop_type_id) in ids_solicitados

            if not es_valido:
                searchable = normalize_text(" ".join(filter(None, [
                    prop_type,
                    str(prop.get("url") or ""),
                    str(prop.get("link") or ""),
                    str(prop.get("title") or ""),
                ])))
                es_valido = any(
                    re.search(r"(?<!\w)" + re.escape(t.lower()) + r"(?!\w)", searchable)
                    for t in tipos_solicitados
                )

            if not es_valido:
                continue

        # === 7. CARACTERÍSTICAS (filtro duro) ===
        if solicitud.caracteristicas and not all(_has_feature(prop, c) for c in solicitud.caracteristicas):
            continue

        # === 7b. PARQUEADEROS MÍNIMOS (filtro duro) ===
        if solicitud.parqueaderos_min:
            parking = int(_get_number(prop, ["parking", "garajes", "garage", "parking_spots"]))
            if parking < solicitud.parqueaderos_min:
                continue

        # === 7c. VESTIERES MÍNIMOS (filtro duro) ===
        if solicitud.vestieres_min is not None:
            vestieres = int(_get_number(prop, ["vestier", "vestidores", "walk_in_closet", "walkin", "dressing_room"]))
            if vestieres < solicitud.vestieres_min:
                continue

        # === 8. INMUEBLE NUEVO (filtro duro) ===
        if solicitud.inmueble_nuevo:
            year_cutoff = date.today().year - 5
            year = _get_number(prop, ["building_date", "year", "year_built", "anio_construccion"])
            if year and year < year_cutoff:
                continue
            if not year:
                searchable_year = normalize_text(" ".join(filter(None, [
                    str(prop.get("observations") or ""),
                    str(prop.get("title") or ""),
                    str(prop.get("description") or ""),
                ])))
                year_match = re.search(r"(?:a[ñn]o|anio|year|built|construido)\s*(?:construido|de construccion|de construcci[oó]n)?[:\s]*(\d{4})", searchable_year)
                if year_match and int(year_match.group(1)) < year_cutoff:
                    continue
                if not year_match:
                    old_kws = ["usado", "second hand", "viejo", "antiguo", "ocasion", "de ocasion"]
                    if any(kw in searchable_year for kw in old_kws):
                        continue

        # === 9. PISO (filtro duro) ===
        if solicitud.piso_categoria or solicitud.piso_maximo is not None or solicitud.piso_minimo is not None:
            prop_floor = _extract_property_floor(prop)
            if prop_floor is None:
                continue
            passes_floor = True
            if solicitud.piso_categoria == "bajo" and prop_floor > 8:
                passes_floor = False
            elif solicitud.piso_categoria == "medio" and not (6 < prop_floor < 12):
                passes_floor = False
            elif solicitud.piso_categoria == "alto" and prop_floor <= 9:
                passes_floor = False
            if solicitud.piso_maximo is not None and prop_floor > solicitud.piso_maximo:
                passes_floor = False
            if solicitud.piso_minimo is not None and prop_floor < solicitud.piso_minimo:
                passes_floor = False
            if not passes_floor:
                continue

        # === 10. RENTAS CORTAS (filtro duro) ===
        if solicitud.es_renta_corta:
            searchable = normalize_text(" ".join(filter(None, [
                str(prop.get("title") or ""),
                str(prop.get("description") or ""),
                str(prop.get("features") or ""),
                str(prop.get("amenities") or ""),
            ])))
            renta_corta_kws = [
                "rentas cortas", "renta corta", "corta estancia",
                "renta temporal", "alquiler temporal", "alquiler corto",
                "alquiler por dias", "alquiler mensual",
                "arriendo temporal", "arriendo por dias",
                "airbnb", "temporal",
            ]
            if not any(kw in searchable for kw in renta_corta_kws):
                continue

        # === 11. INDEPENDIENTE (excluir unidades cerradas / parcelaciones) ===
        if solicitud.independiente:
            searchable = normalize_text(" ".join(filter(None, [
                str(prop.get("title") or ""),
                str(prop.get("description") or ""),
                str(prop.get("features") or ""),
                str(prop.get("amenities") or ""),
                str(prop.get("property_type") or ""),
                str(prop.get("tipo") or ""),
                str(prop.get("property_type_label") or ""),
            ])))
            unidad_kw = [
                "unidad cerrada", "conjunto cerrado", "unidad residencial",
                "unidad campestre", "condominio", "urbanizacion cerrada",
                "ciudadela", "unidad privada",
            ]
            if any(kw in searchable for kw in unidad_kw):
                continue
            # Para Lote/Bodega, también excluir parcelaciones
            prop_type_text = normalize_text(" ".join(filter(None, [
                str(prop.get("property_type") or ""),
                str(prop.get("tipo") or ""),
                str(prop.get("property_type_label") or ""),
                str(prop.get("title") or ""),
            ])))
            if re.search(r"(?<!\w)(lote|bodega|terreno)(?!\w)", prop_type_text):
                if re.search(r"parcelacion|parcela|parcelación", searchable):
                    continue

        results.append(prop)

    return results


def _extract_property_floor(prop: dict) -> int | None:
    # Primero buscar campo directo en la respuesta de Wasi
    for key in ("piso", "floor", "nivel", "level", "num_pisos", "cantidad_pisos"):
        val = prop.get(key)
        if val is not None:
            try:
                ival = int(float(str(val)))
                if 1 <= ival <= 100:
                    return ival
            except (ValueError, TypeError):
                pass

    searchable = " ".join(filter(None, [
        str(prop.get("url") or ""),
        str(prop.get("title") or ""),
        str(prop.get("slug") or ""),
        str(prop.get("description") or ""),
        str(prop.get("comment") or ""),
        str(prop.get("descripcion") or ""),
    ])).lower()

    if re.search(r"(?<!\w)penthouse(?!\w)", searchable):
        return 20
    if re.search(r"ultimo\s+piso|ultimo\s+nivel", searchable):
        return 15
    m = re.search(r"piso[-\s]*(\d+)", searchable)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)[°\s]*piso", searchable)
    if m:
        return int(m.group(1))
    m = re.search(r"nivel[-\s]*(\d+)", searchable)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*(?:niveles?|pisos?)\b", searchable)
    if m:
        val = int(m.group(1))
        if 1 <= val <= 30:
            return val
    return None


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