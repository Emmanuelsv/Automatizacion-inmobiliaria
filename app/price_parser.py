import re
from dataclasses import dataclass

from app.config import PRICE_MARGIN_ABOVE, PRICE_MARGIN_BELOW


@dataclass
class Budget:
    min_price: int | None = None
    max_price: int | None = None
    exact: int | None = None


def parse_price(text: str) -> int | None:
    if not text:
        return None

    cleaned = re.sub(r"\s+", " ", text)

    # 850'000.000 o 1'500.000.000 — comilla recta (U+0027) o tipográfica de móvil (U+2019)
    match = re.search(r"\$?\s*(\d{1,3})['’](\d{3})((?:\.\d{3})*)", cleaned)
    if match:
        num_str = match.group(1) + match.group(2) + match.group(3).replace(".", "")
        num = int(num_str)
        if num >= 30_000_000:
            return num

    # $700.000.000 o 700.000.000 (puntos como separadores de miles)
    # También "1.340" → 1340 → se asume millones (igual que número suelto)
    match = re.search(r"\$?\s*(\d{1,5}(?:\.\d{3})+)", cleaned)
    if match:
        num = int(match.group(1).replace(".", ""))
        if num >= 30_000_000:
            return num
        if 100 <= num <= 10_000:
            return num * 1_000_000

    # $700,000,000 (comas como separadores)
    match = re.search(r"\$?\s*(\d{1,5}(?:,\d{3})+)", cleaned)
    if match:
        num = int(match.group(1).replace(",", ""))
        if num >= 30_000_000:
            return num

    # 700 millones, 1.200 millones, 1200 millones, 700 mll, 700 mls
    match = re.search(r"(\d{1,5}(?:\.\d{3})?)\s*(?:millones|millon|mills?|mll|mls)\b", cleaned, re.IGNORECASE)
    if match:
        base = float(match.group(1).replace(".", ""))
        return int(base * 1_000_000)

    # 700M o 700m
    match = re.search(r"(\d{1,4})\s*[Mm]\b", cleaned)
    if match:
        return int(match.group(1)) * 1_000_000

    # Número sin separadores: 1300000000 (mínimo 9 cifras para no confundir con teléfonos)
    match = re.search(r"\$?\s*(\d{9,12})(?!\d)", cleaned)
    if match:
        num = int(match.group(1))
        if num >= 30_000_000:
            return num

    # Número solo (3-6 dígitos): se asume en millones (ej: "5000" → 5.000M, "800" → 800M)
    match = re.search(r"(?<!\d)(\d{3,6})(?!\d)", cleaned)
    if match:
        num = int(match.group(1))
        if 100 <= num <= 50_000:
            return num * 1_000_000

    return None


def extract_budget(text: str) -> Budget:
    if not text:
        return Budget()

    budget_patterns = [
        r"presupuesto\s*(?:m[aá]ximo|max|:)?\s*[:.]?\s*(.+?)(?:\n|$)",
        r"(?:m[aá]ximo|max|hasta|tope)\s*[:.]?\s*\$?\s*(.+?)(?:\n|$)",
        r"💰\s*(.+?)(?:\n|$)",
        r"valor\s*(?:m[aá]ximo|max)?\s*[:.]?\s*(.+?)(?:\n|$)",
        r"rango\s*[:.]?\s*(.+?)(?:\n|$)",
    ]

    max_price = None

    for pattern in budget_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted = parse_price(match.group(1))
            if extracted:
                max_price = extracted
                break

    if max_price is None:
        all_prices = []
        for match in re.finditer(r"(\d{1,3})[‘’](\d{3})((?:\.\d{3})*)", text):
            num_str = match.group(1) + match.group(2) + match.group(3).replace(".", "")
            num = int(num_str)
            if num >= 30_000_000:
                all_prices.append(num)
        for match in re.finditer(r"\$?\s*(\d{1,3}(?:\.\d{3}){2,})", text):
            num = int(match.group(1).replace(".", ""))
            if num >= 30_000_000:
                all_prices.append(num)
        # "750 mill", "650 millones", "700 mll", etc.
        for match in re.finditer(
            r"(\d{1,5}(?:[.,]\d{3})?)\s*(?:millones?|millon|mills?|mll|mls)\b",
            text, re.IGNORECASE,
        ):
            base = float(match.group(1).replace(".", "").replace(",", ""))
            num = int(base * 1_000_000)
            if num >= 30_000_000:
                all_prices.append(num)
        # "no sea mas 650", "no mas de 750", etc. (precio informal sin sufijo)
        for match in re.finditer(
            r"(?:no\s+(?:sea\s+)?m[aá]s\s+(?:de\s+)?)(\d{3,5})\b",
            text, re.IGNORECASE,
        ):
            num = int(match.group(1))
            if 100 <= num <= 50_000:
                all_prices.append(num * 1_000_000)
        # Sufijo M/m suelto sin keyword de presupuesto (ej: "* $550 m")
        for match in re.finditer(r"\$?\s*(\d{1,4})\s*[Mm]\b", text):
            num = int(match.group(1)) * 1_000_000
            if num >= 30_000_000:
                all_prices.append(num)
        if all_prices:
            max_price = max(all_prices)

    if max_price is None:
        return Budget()

    if max_price <= 1000_000_000:
        return Budget(
            min_price=max(0, max_price - PRICE_MARGIN_BELOW),
            max_price=max_price + PRICE_MARGIN_ABOVE,
            exact=max_price,
        )
    else:
        return Budget(
            min_price=int(max(0, max_price - max_price * 0.07)),
            max_price=int(max_price + max_price * 0.07),
            exact=max_price,
        )
        