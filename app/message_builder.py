import re

from app.parser import SolicitudParseada
from app.matcher import _extract_property_floor, _get_number
from app.config import MAX_RESULTS


def _floor_label(piso: int | None) -> str | None:
    if piso is None:
        return None
    if piso <= 8:
        return "Bajo"
    if 7 <= piso <= 11:
        return "Medio"
    return "Alto"


def _no_contact_url(url: str) -> str:
    if not url:
        return url
    return re.sub(r'https?://[^/]+\.inmo\.co', 'https://info.wasi.co', url)


def format_price(price) -> str:
    if not price:
        return "N/A"
    try:
        return f"${int(price):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "N/A"


def _property_type_label(prop: dict) -> str:
    raw = str(prop.get("property_type", prop.get("tipo", prop.get("property_type_label", ""))))
    return raw.capitalize() if raw else "Inmueble"


def _location_label(prop: dict) -> str:
    return prop.get("neighborhood", prop.get("zone", prop.get("zone_label", prop.get("city", ""))))


def _stratum(prop: dict) -> int | None:
    val = prop.get("stratum")
    if val is not None:
        try:
            v = int(val)
            if 1 <= v <= 6:
                return v
        except (ValueError, TypeError):
            pass
    # fallback: buscar en texto
    searchable = " ".join(filter(None, [
        str(prop.get("title", "")),
        str(prop.get("description", "")),
        str(prop.get("features", "")),
    ]))
    m = re.search(r"(?:estrato|stratum)\s*:?\s*(\d)", searchable, re.IGNORECASE)
    if m:
        v = int(m.group(1))
        if 1 <= v <= 6:
            return v
    return None


def build_response_message(
    properties: list[dict],
    solicitud: SolicitudParseada,
    max_results: int = MAX_RESULTS,
) -> list[str]:
    if not properties:
        msg = (
            "⚠️ *Sin resultados*\n\n"
            f"No se encontraron inmuebles que coincidan con la solicitud"
            f"{f' de *{solicitud.cliente}*' if solicitud.cliente else ''}.\n\n"
            f"Zonas buscadas: {', '.join(u.barrio for u in solicitud.ubicaciones) or 'No especificada'}\n"
            f"Presupuesto: {format_price(solicitud.presupuesto.exact) if solicitud.presupuesto.exact else 'No especificado'}\n\n"
            "_Puedes verificar manualmente en el portal Wasi._\n"
            "_Jhaen Inmobiliarios_"
        )
        return [msg]

    to_show = properties[:max_results]
    messages: list[str] = []

    # Pedido primero (n8n enviará en orden: 1. pedido, 2..N. propiedades)
    if solicitud.mensaje_original:
        messages.append(
            f"📋 *Buenas colega ¿como estas?, esto te puede servir:*\n\n{solicitud.mensaje_original}"
        )

    for p in to_show:
        tipo = _property_type_label(p)
        ubicacion = _location_label(p)
        ciudad = p.get("city", p.get("region", ""))
        url = _no_contact_url(p.get("url", p.get("link", "")))

        area = _get_number(p, ["area", "built_area", "area_construida", "area_total", "metros"])
        rooms = int(_get_number(p, ["rooms", "bedrooms", "habitaciones", "alcobas", "num_rooms", "num_bedrooms"]))
        bathrooms = int(_get_number(p, ["bathrooms", "baños", "banos", "num_bathrooms"]))
        parking = int(_get_number(p, ["parking", "garajes", "garage", "parking_spots"]))
        sale_price = _get_number(p, ["sale_price", "price", "precio_venta", "precio", "valor_venta"])
        stratum = _stratum(p)

        location_part = f"{ubicacion}, {ciudad}" if ciudad else ubicacion

        lines = [f"*{tipo} en venta en {location_part} :*"]
        lines.append(f"- Precio de venta: {format_price(sale_price)}")

        if area:
            lines.append(f"- {int(area)} M2")
        if rooms:
            lines.append(f"- {rooms} Alcobas")
        if bathrooms:
            lines.append(f"- {bathrooms} Baños")
        if parking:
            lines.append(f"- {parking} Garaje")
        if stratum is not None:
            lines.append(f"- Estrato: {stratum}")

        prop_floor = _extract_property_floor(p)
        if prop_floor is not None:
            lines.append(f"- Piso: {prop_floor}")

        if url:
            lines.append(f"- Más información y fotos:")
            lines.append(url)

        messages.append("\n".join(lines))

    return messages
