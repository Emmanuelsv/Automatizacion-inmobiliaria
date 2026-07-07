---
name: wasi-domain
description: >
  Reglas de negocio, filtrado estricto y lógica de ubicación del sistema Jhaen
  Inmobiliarios. Usar SIEMPRE que se vaya a modificar matcher.py, wasi_client.py,
  locations.py, o cualquier lógica de filtrado o búsqueda de propiedades.
  También activar cuando el usuario mencione: barrios, ciudades, zonas,
  presupuesto, habitaciones, área, administración, Wasi, filtros de
  propiedades, o quiera agregar nuevas ubicaciones o tipos de inmueble.
---

# Dominio Inmobiliario Jhaen — Wasi (Matching Estricto)

## Visión general del flujo

```
WhatsApp → parse_message() → SolicitudParseada
                                    ↓
                       search_all_locations()  ← Wasi API
                                    ↓
                          match_properties()      ← filtrado 100% estricto
                                    ↓
                       build_response_message()
```

---

## Filosofía de matching — CAMBIO DE PARADIGMA

**Antes:** sistema de scoring aditivo (0-100 puntos). Una propiedad podía
enviarse aunque solo cumpliera parcialmente los criterios, siempre que
sumara puntos suficientes. El tipo de inmueble y las características eran
"bonus", no filtros.

**Ahora:** el matching es **estrictamente booleano**. Una propiedad se envía
al asesor **si y solo si cumple el 100% de los criterios que el usuario
especificó explícitamente** en su solicitud. No existe:

- Puntaje ni ranking de relevancia.
- "Casi coincide" — o cumple todo, o se descarta.
- Compensación entre criterios (ej. un precio excelente ya no compensa un
  tipo de inmueble incorrecto).

El único orden que se aplica a los resultados es de **presentación**
(ej. precio ascendente), nunca de relevancia.

---

## Regla global: dato faltante = no verificable = se descarta

Si el usuario pidió un criterio (ej. "mínimo 2 habitaciones") y la propiedad
de Wasi **no trae ese campo** (`None` tras probar todas las claves conocidas),
la propiedad **se descarta**. No se asume que "podría cumplir".

```python
# Correcto
if solicitud.habitaciones_min is not None:
    rooms = _get_number(prop, ROOM_KEYS)
    if rooms is None or rooms < solicitud.habitaciones_min:
        return False  # dato faltante también descarta

# Incorrecto — NO hacer esto
if rooms is not None and rooms < solicitud.habitaciones_min:
    return False  # deja pasar propiedades sin dato de habitaciones
```

> ⚠️ Consecuencia conocida: con datos de Wasi inconsistentes (sobre todo en
> descripciones/características), esta regla puede reducir mucho el número
> de resultados, incluso a cero en algunas búsquedas. Es el trade-off
> esperado de un sistema 100% estricto. Ver sección "Riesgo conocido" abajo.

---

## Reglas de ubicación — CRÍTICAS (sin cambios)

### Ciudad: filtro DURO (no negociable)
Si el usuario pide una ciudad específica, se descartan sin excepción todas
las propiedades de otros municipios.

```python
if requested_city_ids and not city_match:
    continue  # descarte total
```

### Barrio: filtro estricto con expansión de zonas
Si se pide un barrio específico y la propiedad tiene `zone_label` o `title`,
se descarta si no coincide. Los barrios se expanden vía `ZONE_ALIASES`.

**Flujo de matching de ubicación:**
1. Comparar `id_city` de la propiedad contra `CITY_ID_MAP` → más confiable.
2. Fallback: comparar nombre de ciudad normalizado.
3. Último fallback: buscar nombre de ciudad en `zone_label` + `title` (solo
   si la propiedad no trae campos de ciudad).

---

## Sistema de filtrado estricto (reemplaza el scoring de 6 capas)

Solo se aplican los filtros correspondientes a los criterios que el usuario
**mencionó explícitamente**. Si no pidió administración máxima, ese filtro
no se evalúa. Pero si pidió un criterio, es obligatorio al 100%.

| # | Criterio | Regla | Tipo |
|---|----------|-------|------|
| 1 | Ciudad | Coincidencia exacta (o ninguna ciudad pedida) | Filtro duro |
| 2 | Barrio/Zona | Coincidencia exacta con expansión de alias | Filtro duro |
| 3 | Precio | Dentro de `[exact - MARGIN_BELOW, exact + MARGIN_ABOVE]` o `[min, max]` | Filtro duro (sin puntos de proximidad) |
| 4 | Tipo de inmueble | Coincidencia exacta si se especificó | **Filtro duro** (antes era bonus) |
| 5 | Habitaciones | `rooms >= habitaciones_min` | Filtro duro |
| 6 | Área | `area >= area_min` | Filtro duro |
| 7 | Administración | `admin <= administracion_max` | Filtro duro |
| 8 | Características | **Todas** las solicitadas deben estar presentes | **Filtro duro** (antes 5 pts c/u) |

No hay "+" de puntos base ni suma acumulada. Una propiedad que pasa los 8
filtros aplicables se incluye; si falla en cualquiera, se descarta.

---

## Pseudocódigo — nuevo `matcher.py`

```python
def matches_request(prop: dict, solicitud: SolicitudParseada) -> bool:
    # 1. Ciudad — filtro duro
    if solicitud.ubicaciones and not _city_matches(prop, solicitud.ubicaciones):
        return False

    # 2. Barrio — filtro duro (con expansión de zonas)
    if solicitud.ubicaciones and not _barrio_matches(prop, solicitud.ubicaciones):
        return False

    # 3. Precio — filtro duro, sin puntos de proximidad
    if solicitud.presupuesto and not _price_in_range(prop, solicitud.presupuesto):
        return False

    # 4. Tipo de inmueble — ahora filtro duro (antes bonus)
    if solicitud.tipo_inmueble:
        prop_type = str(prop.get("property_type", prop.get("tipo", ""))).lower()
        if solicitud.tipo_inmueble.lower() not in prop_type:
            return False

    # 5. Habitaciones mínimas
    if solicitud.habitaciones_min is not None:
        rooms = _get_number(prop, ROOM_KEYS)
        if rooms is None or rooms < solicitud.habitaciones_min:
            return False

    # 6. Área mínima
    if solicitud.area_min is not None:
        area = _get_number(prop, AREA_KEYS)
        if area is None or area < solicitud.area_min:
            return False

    # 7. Administración máxima
    if solicitud.administracion_max is not None:
        admin = _get_number(prop, ADMIN_KEYS)
        if admin is None or admin > solicitud.administracion_max:
            return False

    # 8. Características — TODAS deben cumplirse
    for caracteristica in solicitud.caracteristicas:
        if not _has_feature(prop, caracteristica):
            return False

    return True


def match_properties(properties: list[dict], solicitud: SolicitudParseada) -> list[dict]:
    matched = [p for p in properties if matches_request(p, solicitud)]
    # Orden de presentación neutral — NO es un ranking de relevancia.
    matched.sort(key=lambda p: _get_number(p, PRICE_KEYS) or float("inf"))
    return matched
```

---

## Qué se elimina del sistema anterior

- Scoring aditivo de 6 capas (0–100 puntos).
- Cálculo de proximidad de precio (`proximity * 30`).
- Bonus de 20 pts por tipo de inmueble sin excluir al que no coincide.
- Puntos por característica cumplida (5 c/u) — ahora es filtro obligatorio
  total (todas o ninguna).
- Puntos base de 5 por pasar filtros.
- Campo `match_score` (int 0-100) en la propiedad procesada.

## Nuevo campo calculado

En vez de `match_score`, el matcher agrega (solo para trazabilidad/debug,
**no** se usa para ordenar ni para decidir inclusión — la inclusión ya es
binaria):

```python
prop["matched_criteria"] = ["ciudad", "barrio", "precio", "tipo_inmueble",
                             "habitaciones", "area", "administracion",
                             "caracteristicas"]
```

---

## Riesgo conocido: resultados vacíos con más frecuencia

Un filtrado 100% estricto —especialmente el requisito de que **todas** las
características solicitadas estén presentes en `description`/`title`/
`features`— puede llevar a 0 resultados con más frecuencia que antes, dado
que la redacción de los avisos en Wasi es inconsistente.

Recomendaciones para mitigar sin romper la filosofía "todo o nada":

- Asegurar que `build_response_message()` tenga un mensaje claro para 0
  resultados (distinto de "no hay inventario" vs "no hay coincidencias
  exactas").
- Si en el futuro se quiere flexibilizar solo las características (dejarlas
  fuera del filtro duro, o exigir "al menos N de M"), debe ser una decisión
  de negocio explícita y documentada aquí — no relajar el filtro de
  ciudad/barrio/precio/tipo bajo ningún escenario.

---

## SolicitudParseada — estructura del objeto central (sin cambios)

```python
@dataclass
class SolicitudParseada:
    es_solicitud: bool
    ubicaciones: list[Ubicacion]      # [{"barrio": str, "ciudad": str}]
    presupuesto: Budget               # {min_price, max_price, exact}
    tipo_inmueble: str | None         # "apartamento", "casa", "local"...
    habitaciones_min: int | None
    area_min: float | None
    administracion_max: int | None
    asesor: str | None
    cliente: str | None
    telefono: str | None
    caracteristicas: list[str]
```

---

## Reglas al modificar este sistema

1. **Nunca relajar el filtro de ciudad** — es una restricción de negocio
   explícita.
2. **Nunca convertir un filtro duro en puntaje.** Cualquier criterio nuevo
   que se agregue debe ser booleano (cumple / no cumple), nunca sumar
   puntos parciales.
3. **Al agregar barrios:** actualizar `locations.py → BARRIOS` Y
   `matcher.py → ZONE_ALIASES` si el barrio pertenece a una zona conceptual.
4. **Al agregar ciudades:** actualizar `locations.py → CIUDADES`,
   `ALIAS_CIUDADES`, `locations.py → BARRIOS` (barrios de esa ciudad), y
   `wasi_client.py → CITY_ID_MAP`.
5. **El filtrado es estricto, no aditivo:** todos los filtros aplicables
   (solo los que correspondan a criterios que el usuario mencionó) deben
   pasar. No hay compensación entre criterios.
6. **Dato faltante en un campo requerido por un filtro activo = descarte.**
   Nunca asumir "podría cumplir" cuando el dato no está.
7. **`_get_number()`** — usar siempre esta función para leer campos
   numéricos de propiedades Wasi; nunca acceder directamente con
   `prop["campo"]`.

---

## Referencias

- `references/wasi-fields.md` — campos observados en respuestas reales de Wasi
- `app/matcher.py` — lógica completa de filtrado y ZONE_ALIASES
- `app/locations.py` — CIUDADES, ALIAS_CIUDADES, BARRIOS
- `app/wasi_client.py` — CITY_ID_MAP y llamadas a la API
