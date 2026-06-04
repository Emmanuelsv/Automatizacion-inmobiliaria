import pytest
from app.price_parser import parse_price, extract_budget


@pytest.mark.parametrize(
    "text, expected",
    [
        ("$700.000.000", 700_000_000),
        ("700.000.000", 700_000_000),
        ("$350.000.000", 350_000_000),
        ("$700,000,000", 700_000_000),
        ("850'000.000", 850_000_000),
        ("500 millones", 500_000_000),
        ("1.200 millones", 1_200_000_000),
        ("400M", 400_000_000),
        ("400m", 400_000_000),
        ("hola mundo", None),
        ("$50.000", None),
    ],
)
def test_parse_price(text, expected):
    assert parse_price(text) == expected


def test_extract_budget_with_context():
    text = "Presupuesto máximo: $700.000.000"
    budget = extract_budget(text)
    assert budget.exact == 700_000_000
    assert budget.min_price == 600_000_000  # 700M - 100M
    assert budget.max_price == 730_000_000  # 700M + 30M


def test_extract_budget_emoji():
    text = "💰 Presupuesto máximo: $500.000.000"
    budget = extract_budget(text)
    assert budget.exact == 500_000_000


def test_extract_budget_informal_mill_and_no_sea_mas():
    text = (
        "BUSCO ENVIGADO PARTE BAJA OTRA PARTE, PONTEVEDRA, SAN MARCOS, "
        "UNIDAD CERRADA, ASCENSOR , 3 HABITACIONES, NO MAS DE 3CER PISO, "
        "SE PUEDE PARA REMODELAR PERO QUE NO SEA MAS 650, "
        "SI YA ESTA REMODELADO 750 MILL"
    )
    budget = extract_budget(text)
    assert budget.exact == 750_000_000


def test_extract_budget_solo_mill():
    assert extract_budget("apartamento 750 mill").exact == 750_000_000


def test_extract_budget_no_sea_mas_sin_sufijo():
    assert extract_budget("que no sea mas 650").exact == 650_000_000


def test_parse_price_dot_thousands_as_millions():
    # "1.340" → 1,340 millones → 1,340,000,000
    assert parse_price("1.340") == 1_340_000_000
    assert parse_price("1.500") == 1_500_000_000
    assert parse_price("2.000") == 2_000_000_000


def test_extract_budget_presupuesto_dot_thousands():
    text = "PRESUPUESTO 1.340"
    budget = extract_budget(text)
    assert budget.exact == 1_340_000_000
