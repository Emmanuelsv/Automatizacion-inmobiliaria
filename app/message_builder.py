import re

from app.parser import SolicitudParseada
from app.config import MAX_RESULTS


def _no_contact_url(url: str) -> str:
    """Convierte la URL de Wasi al formato sin datos de contacto (info.wasi.co)."""
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

    header = "*Buenas colega ¿como estas?, esto te puede servir*\n\n"
    #if solicitud.cliente:
    #    header += f"Cliente: *{solicitud.cliente}*\n"
    #header += f"Zonas: {', '.join(f'{u.barrio} ({u.ciudad})' for u in solicitud.ubicaciones)}\n"
    #header += f"Presupuesto: hasta {format_price(solicitud.presupuesto.exact)}\n"
    #if solicitud.tipo_inmueble:
    #    header += f"Tipo: {solicitud.tipo_inmueble}\n"
    #if solicitud.habitaciones_min:
    #    header += f"Mín. {solicitud.habitaciones_min} habitaciones\n"
    #if solicitud.area_min:
    #    header += f"Mín. {solicitud.area_min} m²\n"
    #header += "\n"

    prop_lines: list[str] = []
    for i, p in enumerate(to_show):
        line = f"*{i + 1}. {p.get('title', p.get('titulo', 'Inmueble'))}*\n"
        line += f" {p.get('neighborhood', p.get('zone', ''))}, {p.get('city', p.get('region', ''))}\n"
        line += f" {format_price(p.get('sale_price', p.get('price')))}\n"
        line += f" {p.get('area', '?')} m²"
        line += f" |  {p.get('rooms', p.get('bedrooms', '?'))} hab"
        line += f" |  {p.get('bathrooms', '?')} baños\n"

        admin = p.get("administration", p.get("admin_fee"))
        if admin:
            line += f" Adm: {format_price(admin)}\n"

        url = _no_contact_url(p.get("url", p.get("link")))
        if url:
            line += f"🔗 {url}\n"

        #line += f"⭐ Coincidencia: {p.get('match_score', 0)}%\n"
        prop_lines.append(line)

    footer = "\n VISITA NUESTRA PAGINA WEB PARA MAS OPCIONES: https://jhaeninmobiliarios.inmo.co/ "

    full_body = "\n".join(prop_lines)
    full_message = header + full_body + footer

    if len(full_message) <= 4000:
        return [full_message]

    # Dividir en múltiples mensajes si supera límite de WhatsApp
    messages = [header]
    current = ""

    for prop_text in prop_lines:
        if len(current) + len(prop_text) > 3500:
            messages.append(current)
            current = prop_text
        else:
            current += "\n" + prop_text

    if current:
        messages.append(current + footer)

    return messages
