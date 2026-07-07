# Campos observados en respuestas de la API Wasi

## Identificación

| Campo        | Tipo    | Notas                                  |
|--------------|---------|----------------------------------------|
| `id`         | string  | ID único de la propiedad               |
| `code`       | string  | Código interno Wasi (ej: "AP-1234")    |
| `title`      | string  | Título del aviso                       |
| `slug`       | string  | URL amigable                           |

## Precio

| Campo          | Tipo  | Notas                                        |
|----------------|-------|----------------------------------------------|
| `sale_price`   | float | Precio de venta (campo principal)            |
| `price`        | float | Alias de sale_price en algunos endpoints     |
| `valor_venta`  | float | Variante en español                          |
| `precio_venta` | float | Variante en español                          |
| `precio`       | float | Variante genérica                            |
| `rent_price`   | float | Precio de arriendo (si aplica)               |

> ⚠️ El campo puede llegar como string o float. Usar `_get_number()` siempre.

## Ubicación

| Campo          | Tipo    | Notas                                          |
|----------------|---------|------------------------------------------------|
| `id_city`      | int     | ID numérico del municipio en Wasi              |
| `city`         | string  | Nombre de la ciudad                            |
| `city_label`   | string  | Nombre legible de la ciudad (más confiable)    |
| `ciudad`       | string  | Variante en español                            |
| `zone_label`   | string  | Nombre de la zona/barrio (campo más útil)      |
| `neighborhood` | string  | Barrio                                         |
| `zone`         | string  | Código o nombre de zona                        |
| `address`      | string  | Dirección (no usar para matching de barrio)    |

## Características físicas

| Campo             | Tipo  | Notas                                   |
|-------------------|-------|-----------------------------------------|
| `rooms`           | int   | Habitaciones (campo principal)          |
| `bedrooms`        | int   | Alias de rooms                          |
| `habitaciones`    | int   | Variante en español                     |
| `alcobas`         | int   | Variante colombiana                     |
| `num_rooms`       | int   | Variante numérica                       |
| `num_bedrooms`    | int   | Variante numérica                       |
| `bathrooms`       | int   | Baños                                   |
| `area`            | float | Área construida en m²                   |
| `built_area`      | float | Alias de area                           |
| `area_construida` | float | Variante en español                     |
| `area_total`      | float | Puede incluir zonas comunes             |
| `metros`          | float | Variante informal                       |
| `parking`         | int   | Parqueaderos                            |
| `stratum`         | int   | Estrato socioeconómico (1-6)            |

## Administración y costos

| Campo            | Tipo  | Notas                                    |
|------------------|-------|------------------------------------------|
| `administration` | float | Cuota de administración mensual          |
| `admin_fee`      | float | Alias de administration                  |
| `administracion` | float | Variante en español                      |

## Tipo de inmueble

| Campo           | Tipo   | Notas                                      |
|-----------------|--------|--------------------------------------------|
| `property_type` | string | Tipo principal (campo más confiable)       |
| `tipo`          | string | Variante en español                        |

**Valores observados en `property_type`:**
- `"apartamento"` / `"apartment"`
- `"casa"` / `"house"`
- `"local"` / `"local comercial"`
- `"oficina"` / `"office"`
- `"bodega"`
- `"lote"` / `"lot"`
- `"finca"`

## Imágenes y multimedia

| Campo      | Tipo         | Notas                              |
|------------|--------------|------------------------------------|
| `images`   | list[string] | URLs de imágenes                   |
| `cover`    | string       | URL de imagen principal            |

## Campos calculados (agregados por el matcher)

| Campo               | Tipo       | Notas                                                            |
|---------------------|------------|-------------------------------------------------------------------|
| `matched_criteria`  | list[str]  | Criterios verificados y cumplidos, solo para trazabilidad/debug. No se usa para ordenar ni para decidir inclusión — la inclusión ya es binaria (ver skill `wasi-domain`). |

> El antiguo campo `match_score` (int 0-100) fue eliminado junto con el
> sistema de scoring. El matching ahora es estrictamente booleano: una
> propiedad se incluye solo si cumple el 100% de los criterios solicitados.

---

## Notas de integración

- La API de Wasi puede devolver campos nulos, strings vacíos, o no incluirlos.
  Siempre usar `prop.get("campo")` y nunca `prop["campo"]`.
- Los campos numéricos pueden llegar como `"850000000"` (string) o `850000000` (int/float).
  La función `_get_number()` en matcher.py maneja esto con try/except float().
- `zone_label` es el campo más útil para matching de barrio; `neighborhood` suele
  ser menos consistente.
- El endpoint de búsqueda por ubicación filtra preliminarmente, pero el matcher
  aplica los filtros definitivos por precio, área, habitaciones, etc.
