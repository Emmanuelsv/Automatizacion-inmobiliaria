---
name: wasi-domain
description: >
  Reglas de negocio, scoring y lógica de ubicación del sistema Jhaen
  Inmobiliarios. Usar SIEMPRE que se vaya a modificar matcher.py, wasi_client.py,
  locations.py, o cualquier lógica de filtrado, scoring o búsqueda de
  propiedades. También activar cuando el usuario mencione: barrios, ciudades,
  zonas, presupuesto, habitaciones, área, administración, Wasi, filtros de
  propiedades, o quiera agregar nuevas ubicaciones o tipos de inmueble.
---

# Dominio Inmobiliario Jhaen — Wasi

## Visión general del flujo

```
WhatsApp → parse_message() → SolicitudParseada
                                    ↓
                       search_all_locations()  ← Wasi API
                                    ↓
                          match_properties()
                                    ↓
                       build_response_message()
```

---

## Reglas de ubicación — CRÍTICAS

### Ciudad: filtro DURO (no negociable)
Si el usuario pide una ciudad específica, **se descartan sin excepción** todas las
propiedades de otros municipios. No hay puntaje parcial ni fallback.

```python
# En matcher.py — nunca suavizar esta lógica
if requested_city_ids and not city_match:
    continue  # descarte total
```

### Barrio: filtro estricto con expansión de zonas
Si se pide un barrio específico y la propiedad tiene `zone_label` o `title`,
se descarta si no coincide. Los barrios se expanden via `ZONE_ALIASES`.

**Flujo de matching de ubicación:**
1. Comparar `id_city` de la propiedad contra `CITY_ID_MAP` → más confiable
2. Fallback: comparar nombre de ciudad normalizado
3. Último fallback: buscar nombre de ciudad en `zone_label` + `title` (solo si la
   propiedad no trae campos de ciudad)

---

## Sistema de scoring — 6 capas

| Capa | Criterio                | Puntos | Tipo     |
|------|-------------------------|--------|----------|
| 1    | Precio                  | 0–30   | Filtro + proximidad (solo si hay `exact`) |
| 2    | Ubicación               | 0–30   | Ciudad 15 + Barrio 15 |
| 3    | **Tipo de inmueble**    | **0 ó 20** | Bonus (filtro fuerte) |
| 4    | Habitaciones            | 0 ó 20 | Filtro + puntos |
| 5    | Área                    | 0 ó 15 | Filtro + puntos |
| 6    | Administración          | 0 ó 10 | Filtro + puntos |
| +    | **Características**     | **5 c/u** | 5 puntos por cada característica cumplida |
| +    | Base (pass all)         | 5      | Siempre que pase los filtros |

**Precio — cálculo de proximidad:**
```python
# Solo se calcula si existe presupuesto.exact > 0
diff = abs(price - solicitud.presupuesto.exact)
proximity = 1 - (diff / solicitud.presupuesto.exact)
score += proximity * 30
```
> ⚠️ Si solo hay rango (sin `exact`), la propiedad pasa el filtro pero no
> recibe puntos por precio. `proximity` puede ser fraccional (no siempre 30).

**Tipo de inmueble — ahora 20 puntos (antes 10):**
El tipo (apartamento, casa, local, etc.) es un criterio de alta prioridad.
Si el usuario pide un tipo específico y la propiedad no coincide, **no se
descarta** pero pierde estos 20 puntos.
```python
prop_type = str(prop.get("property_type", prop.get("tipo", ""))).lower()
if solicitud.tipo_inmueble and solicitud.tipo_inmueble.lower() in prop_type:
    score += 20
```

**Características — 5 puntos por cada una:**
Cada característica solicitada que aparezca en la propiedad (en `description`,
`title`, `features`, `amenities` o campos booleanos como `has_pool`) suma
5 puntos al score.
```python
for caracteristica in solicitud.caracteristicas:
    if _has_feature(prop, caracteristica):
        score += 5
```
Ejemplos de características típicas: `parqueadero`, `terraza`, `balcón`,
`piscina`, `gimnasio`, `vista`, `chimenea`, `estudio`, `cuarto de servicio`.

---

## Campos de la API Wasi

Los campos que devuelve Wasi no siempre son consistentes. El matcher
prueba múltiples claves por cada dato:

```python
# Precio
["sale_price", "price", "valor_venta", "precio_venta", "precio"]

# Habitaciones
["rooms", "bedrooms", "habitaciones", "alcobas", "num_rooms", "num_bedrooms"]

# Área
["area", "built_area", "area_construida", "area_total", "metros"]

# Administración
["administration", "admin_fee", "administracion"]

# Ciudad
["id_city"]  # numérico → comparar contra CITY_ID_MAP
prop.get("city") or prop.get("city_label") or prop.get("ciudad")

# Zona/barrio
["zone_label", "neighborhood", "zone"]
```

> Ver `references/wasi-fields.md` para el listado completo de campos observados
> en producción y sus tipos.

---

## CITY_ID_MAP — IDs de Wasi por municipio

```python
CITY_ID_MAP = {
    "Medellín":   <id_medellin>,
    "Envigado":   <id_envigado>,
    "Sabaneta":   <id_sabaneta>,
    "Bello":      <id_bello>,
    "Itagüí":     <id_itagui>,
    "La Estrella":<id_la_estrella>,
    "Caldas":     <id_caldas>,
    "Copacabana": <id_copacabana>,
}
```
> ⚠️ Los IDs reales están en `wasi_client.py`. Nunca hardcodear aquí, siempre
> importar desde `app.wasi_client.CITY_ID_MAP`.

---

## ZONE_ALIASES — expansión de zonas conceptuales

Cuando el usuario pide una zona amplia (ej: "Poblado Alto", "Envigado Bajo"),
se expande a sus barrios reales antes del matching:

```
"poblado alto"   → altos del poblado, los balsos, loma de los balsos,
                   las lomas, el tesoro, patio bonito, manila ...

"poblado bajo"   → san lucas, la florida, la aguacatala, lalinde,
                   astorga, provenza, parque lleras ...

"envigado alto"  → loma del chocho, el esmeraldal, loma de los balsos,
                   las brujas, escobero, el salado, las palmas ...

"envigado bajo"  → zuniga, la frontera, la abadia, las orquideas,
                   el campestre, santa maria de los angeles ...
```

> Lista completa en `matcher.py → ZONE_ALIASES`. Al agregar nuevas zonas,
> actualizar tanto `ZONE_ALIASES` en matcher.py como `BARRIOS` en locations.py.

---

## SolicitudParseada — estructura del objeto central

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

1. **Nunca relajar el filtro de ciudad** — es una restricción de negocio explícita.
2. **Al agregar barrios:** actualizar `locations.py → BARRIOS` Y `matcher.py → ZONE_ALIASES`
   si el barrio pertenece a una zona conceptual.
3. **Al agregar ciudades:** actualizar `locations.py → CIUDADES`, `ALIAS_CIUDADES`,
   `locations.py → BARRIOS` (barrios de esa ciudad), y `wasi_client.py → CITY_ID_MAP`.
4. **El scoring es aditivo** — no reemplazar puntos, sumar sobre el acumulado.
5. **`_get_number()`** — usar siempre esta función para leer campos numéricos de
   propiedades Wasi; nunca acceder directamente con `prop["campo"]`.

---

## Referencias

- `references/wasi-fields.md` — campos observados en respuestas reales de Wasi
- `app/matcher.py` — lógica completa de scoring y ZONE_ALIASES
- `app/locations.py` — CIUDADES, ALIAS_CIUDADES, BARRIOS
- `app/wasi_client.py` — CITY_ID_MAP y llamadas a la API
