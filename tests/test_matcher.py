import pytest
from app.matcher import match_properties
from app.parser import SolicitudParseada, Location
from app.price_parser import Budget


def _make_solicitud(**kwargs) -> SolicitudParseada:
    defaults = {
        "es_solicitud": True,
        "ubicaciones": [Location(barrio="El Poblado", ciudad="Medellín")],
        "presupuesto": Budget(min_price=600_000_000, max_price=730_000_000, exact=700_000_000),
        "tipo_inmueble": "Apartamento",
        "habitaciones_min": 2,
        "area_min": 80,
        "administracion_max": 600_000,
    }
    defaults.update(kwargs)
    return SolicitudParseada(**defaults)


def test_match_property_passes():
    props = [
        {
            "id": 1,
            "title": "Apto El Poblado",
            "city": "Medellín",
            "zone_label": "El Poblado",
            "sale_price": 680_000_000,
            "rooms": 3,
            "area": 95,
            "administration": 450_000,
            "property_type": "Apartamento",
        }
    ]
    solicitud = _make_solicitud()
    result = match_properties(props, solicitud)
    assert len(result) == 1


def test_match_property_fails_price():
    props = [
        {
            "id": 1,
            "title": "Apto caro",
            "sale_price": 900_000_000,
            "rooms": 3,
            "area": 100,
            "administration": 400_000,
        }
    ]
    solicitud = _make_solicitud()
    result = match_properties(props, solicitud)
    assert len(result) == 0


def test_match_property_fails_rooms():
    props = [
        {
            "id": 1,
            "title": "Apto pequeño",
            "sale_price": 650_000_000,
            "rooms": 1,
            "area": 90,
            "administration": 400_000,
        }
    ]
    solicitud = _make_solicitud()
    result = match_properties(props, solicitud)
    assert len(result) == 0


def test_match_sorted_by_score():
    props = [
        {"id": 1, "city": "Medellín", "zone_label": "El Poblado", "sale_price": 720_000_000, "rooms": 2, "area": 80, "administration": 500_000, "property_type": "Apartamento"},
        {"id": 2, "city": "Medellín", "zone_label": "El Poblado", "sale_price": 700_000_000, "rooms": 3, "area": 100, "administration": 400_000, "property_type": "Apartamento"},
    ]
    solicitud = _make_solicitud()
    result = match_properties(props, solicitud)
    assert len(result) == 2


def test_empty_properties():
    solicitud = _make_solicitud()
    result = match_properties([], solicitud)
    assert result == []


def test_excluded_zone_is_filtered_out():
    """Propiedad en Las Palmas debe descartarse si el usuario la excluyó."""
    props = [
        {
            "id": 1,
            "city": "Envigado",
            "zone_label": "Las Palmas",
            "sale_price": 650_000_000,
            "rooms": 3,
            "area": 90,
            "property_type": "Casa",
        },
        {
            "id": 2,
            "city": "Envigado",
            "zone_label": "La Frontera",
            "sale_price": 650_000_000,
            "rooms": 3,
            "area": 90,
            "property_type": "Casa",
        },
    ]
    solicitud = _make_solicitud(
        ubicaciones=[Location(barrio="Envigado", ciudad="Envigado")],
        ubicaciones_excluidas=[Location(barrio="Las Palmas", ciudad="Envigado")],
        presupuesto=Budget(min_price=500_000_000, max_price=800_000_000, exact=650_000_000),
        tipo_inmueble="Casa",
        habitaciones_min=3,
        area_min=80,
        administracion_max=None,
    )
    result = match_properties(props, solicitud)
    ids = [p["id"] for p in result]
    assert 1 not in ids, "La propiedad en Las Palmas no debería aparecer"
    assert 2 in ids, "La propiedad en La Frontera sí debería aparecer"


def test_excluded_zone_title_fallback():
    """Propiedad con 'palmas' en el título también debe excluirse."""
    props = [
        {
            "id": 1,
            "city": "Envigado",
            "zone_label": "",
            "title": "Casa en Alto de Palmas Envigado",
            "sale_price": 650_000_000,
            "rooms": 3,
            "area": 90,
            "property_type": "Casa",
        },
    ]
    solicitud = _make_solicitud(
        ubicaciones=[Location(barrio="Envigado", ciudad="Envigado")],
        ubicaciones_excluidas=[Location(barrio="Las Palmas", ciudad="Envigado")],
        presupuesto=Budget(min_price=500_000_000, max_price=800_000_000, exact=650_000_000),
        tipo_inmueble="Casa",
        habitaciones_min=3,
        area_min=80,
        administracion_max=None,
    )
    result = match_properties(props, solicitud)
    assert len(result) == 0
