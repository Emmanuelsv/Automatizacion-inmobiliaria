from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from app.parser import parse_message
from app.wasi_client import search_all_locations
from app.matcher import match_properties
from app.message_builder import build_response_message
from app.config import APP_PORT, COUNTRY_CODE
from app.dedup import init_db, is_duplicate


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="MYE Inmobiliaria - Parser de Solicitudes",
    description="API para parsear solicitudes de inmuebles desde WhatsApp y buscar en Wasi",
    version="1.0.0",
    lifespan=lifespan,
)


class WebhookPayload(BaseModel):
    text: str
    sender: str | None = None
    group_id: str | None = None
    push_name: str | None = None


class ProcessResponse(BaseModel):
    es_solicitud: bool
    mensajes: list[str]
    telefono: str | None
    asesor: str | None
    total_resultados: int
    solicitud: dict


@app.get("/health")
def health():
    return {"status": "ok", "service": "mye-parser"}


@app.post("/debug-wasi")
async def debug_wasi(payload: WebhookPayload):
    """Retorna los campos crudos que devuelve Wasi para diagnóstico."""
    solicitud = parse_message(payload.text)
    if not solicitud.ubicaciones:
        return {"error": "no_locations", "parsed": _solicitud_to_dict(solicitud)}
    ubicaciones_dict = [{"barrio": u.barrio, "ciudad": u.ciudad} for u in solicitud.ubicaciones]
    try:
        properties = await search_all_locations(ubicaciones=ubicaciones_dict)
        sample = properties[:2] if properties else []
        return {
            "total_wasi": len(properties),
            "sample_keys": list(sample[0].keys()) if sample else [],
            "sample": sample,
            "parsed": _solicitud_to_dict(solicitud),
        }
    except Exception as e:
        return {"error": str(e), "parsed": _solicitud_to_dict(solicitud)}


@app.post("/parse", response_model=dict)
def parse_only(payload: WebhookPayload):
    """Solo parsea el mensaje sin buscar en Wasi. Útil para testing."""
    result = parse_message(payload.text)
    return {
        "es_solicitud": result.es_solicitud,
        "ubicaciones": [{"barrio": u.barrio, "ciudad": u.ciudad} for u in result.ubicaciones],
        "ubicaciones_excluidas": [{"barrio": u.barrio, "ciudad": u.ciudad} for u in result.ubicaciones_excluidas],
        "presupuesto": {
            "min": result.presupuesto.min_price,
            "max": result.presupuesto.max_price,
            "exact": result.presupuesto.exact,
        },
        "tipo_inmueble": result.tipo_inmueble,
        "habitaciones_min": result.habitaciones_min,
        "area_min": result.area_min,
        "administracion_max": result.administracion_max,
        "asesor": result.asesor,
        "cliente": result.cliente,
        "telefono": result.telefono,
        "caracteristicas": result.caracteristicas,
    }


def _extract_phone(sender: str | None) -> str | None:
    """Extrae el número local del campo 'from' de Whapi.

    Whapi envía el remitente como número con código de país: '573026218105'.
    Retorna el número sin el código de país configurado.
    """
    if not sender or "@g.us" in sender:
        return None
    number = sender.split("@")[0]
    if number.startswith(COUNTRY_CODE) and len(number) > len(COUNTRY_CODE):
        number = number[len(COUNTRY_CODE):]
    return number if number.isdigit() and 8 <= len(number) <= 12 else None


@app.post("/process", response_model=ProcessResponse)
async def process_message(payload: WebhookPayload):
    """Endpoint principal: parsea, busca en Wasi, y retorna mensajes para WhatsApp."""
    solicitud = parse_message(payload.text)

    sender_phone = _extract_phone(payload.sender)
    if sender_phone:
        solicitud.telefono = sender_phone
    elif payload.sender and not solicitud.telefono:
        solicitud.telefono = payload.sender

    if not solicitud.es_solicitud:
        return ProcessResponse(
            es_solicitud=False,
            mensajes=[],
            telefono=None,
            asesor=None,
            total_resultados=0,
            solicitud={"es_solicitud": False},
        )

    sender_key = payload.sender or ""
    if await is_duplicate(sender_key, payload.text):
        return ProcessResponse(
            es_solicitud=True,
            mensajes=[],
            telefono=solicitud.telefono,
            asesor=solicitud.asesor,
            total_resultados=0,
            solicitud=_solicitud_to_dict(solicitud),
        )

    if not solicitud.ubicaciones:
        return ProcessResponse(
            es_solicitud=True,
            mensajes=["⚠️ No se pudo identificar la ubicación en la solicitud."],
            telefono=solicitud.telefono,
            asesor=solicitud.asesor,
            total_resultados=0,
            solicitud=_solicitud_to_dict(solicitud),
        )

    ubicaciones_dict = [
        {"barrio": u.barrio, "ciudad": u.ciudad}
        for u in solicitud.ubicaciones
    ]

    try:
        properties = await search_all_locations(
            ubicaciones=ubicaciones_dict,
            min_price=solicitud.presupuesto.min_price,
            max_price=solicitud.presupuesto.max_price,
            min_area=solicitud.area_min,
            min_rooms=solicitud.habitaciones_min,
            property_type=solicitud.tipo_inmueble,
        )
    except Exception as e:
        return ProcessResponse(
            es_solicitud=True,
            mensajes=[f"⚠️ Error al consultar inventario Wasi: {str(e)}"],
            telefono=solicitud.telefono,
            asesor=solicitud.asesor,
            total_resultados=0,
            solicitud=_solicitud_to_dict(solicitud),
        )

    matched = match_properties(properties, solicitud)
    messages = build_response_message(matched, solicitud)

    return ProcessResponse(
        es_solicitud=True,
        mensajes=messages,
        telefono=solicitud.telefono,
        asesor=solicitud.asesor,
        total_resultados=len(matched),
        solicitud=_solicitud_to_dict(solicitud),
    )


def _solicitud_to_dict(solicitud) -> dict:
    return {
        "es_solicitud": solicitud.es_solicitud,
        "ubicaciones": [{"barrio": u.barrio, "ciudad": u.ciudad} for u in solicitud.ubicaciones],
        "presupuesto": {
            "min": solicitud.presupuesto.min_price,
            "max": solicitud.presupuesto.max_price,
            "exact": solicitud.presupuesto.exact,
        },
        "tipo_inmueble": solicitud.tipo_inmueble,
        "habitaciones_min": solicitud.habitaciones_min,
        "area_min": solicitud.area_min,
        "administracion_max": solicitud.administracion_max,
        "asesor": solicitud.asesor,
        "cliente": solicitud.cliente,
        "telefono": solicitud.telefono,
        "caracteristicas": solicitud.caracteristicas,
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=APP_PORT, reload=True)
