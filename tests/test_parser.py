import pytest
from app.parser import parse_message, extract_negative_locations
from tests.fixtures.sample_messages import SAMPLE_MESSAGES


@pytest.mark.parametrize("sample", SAMPLE_MESSAGES, ids=[s["id"] for s in SAMPLE_MESSAGES])
def test_parse_message(sample):
    result = parse_message(sample["text"])
    expected = sample["expected"]

    assert result.es_solicitud == expected["es_solicitud"], (
        f"es_solicitud: esperado {expected['es_solicitud']}, obtenido {result.es_solicitud}"
    )

    if not expected["es_solicitud"]:
        return

    if "tipo_inmueble" in expected:
        assert result.tipo_inmueble == expected["tipo_inmueble"], (
            f"tipo_inmueble: esperado {expected['tipo_inmueble']}, obtenido {result.tipo_inmueble}"
        )

    if "presupuesto_exact" in expected:
        assert result.presupuesto.exact == expected["presupuesto_exact"], (
            f"presupuesto: esperado {expected['presupuesto_exact']}, obtenido {result.presupuesto.exact}"
        )

    if "habitaciones_min" in expected:
        assert result.habitaciones_min == expected["habitaciones_min"], (
            f"habitaciones: esperado {expected['habitaciones_min']}, obtenido {result.habitaciones_min}"
        )

    if "area_min" in expected:
        assert result.area_min == expected["area_min"], (
            f"area: esperado {expected['area_min']}, obtenido {result.area_min}"
        )

    if "administracion_max" in expected:
        assert result.administracion_max == expected["administracion_max"], (
            f"admin: esperado {expected['administracion_max']}, obtenido {result.administracion_max}"
        )

    if "telefono" in expected:
        assert result.telefono == expected["telefono"], (
            f"telefono: esperado {expected['telefono']}, obtenido {result.telefono}"
        )

    if "asesor" in expected:
        assert result.asesor == expected["asesor"], (
            f"asesor: esperado {expected['asesor']}, obtenido {result.asesor}"
        )

    if "cliente" in expected:
        assert result.cliente == expected["cliente"], (
            f"cliente: esperado {expected['cliente']}, obtenido {result.cliente}"
        )

    if "min_barrios" in expected:
        assert len(result.ubicaciones) >= expected["min_barrios"], (
            f"barrios: esperado mín {expected['min_barrios']}, obtenido {len(result.ubicaciones)} "
            f"({[u.barrio for u in result.ubicaciones]})"
        )


@pytest.mark.parametrize("text,expected_barrios", [
    ("BUSCO CASA Poblado-Envigado (No palmas) 3-4 alcobas", ["Las Palmas"]),
    ("busco apto, sin palmas, 3 hab", ["Las Palmas"]),
    ("excluye palmas y bello", ["Las Palmas"]),
    ("no le gusta palmas ni sabaneta", ["Las Palmas"]),
    ("busco en envigado, no le gusta las palmas", ["Las Palmas"]),
])
def test_extract_negative_locations(text, expected_barrios):
    result = extract_negative_locations(text)
    found_barrios = [loc.barrio for loc in result]
    for b in expected_barrios:
        assert b in found_barrios, f"'{b}' debería estar en las zonas excluidas; obtenido: {found_barrios}"


def test_parse_message_excludes_negative_zones():
    text = "BUSCO CASA Poblado-Envigado (No palmas) 3-4 alcobas presupuesto 650 mill"
    result = parse_message(text)
    excluidos = [u.barrio for u in result.ubicaciones_excluidas]
    positivos = [u.barrio for u in result.ubicaciones]
    assert "Las Palmas" in excluidos
    assert "Las Palmas" not in positivos
