---
name: data-patterns
description: >
  Formatos colombianos de precio, normalización de texto con tildes, alias de
  ciudades y barrios, y patrones de entrada desde WhatsApp. Usar SIEMPRE que se
  vaya a modificar price_parser.py, locations.py, normalizer.py, o cualquier
  regex de extracción de datos. También activar cuando el usuario quiera agregar
  nuevos formatos de precio, nuevos barrios o alias, o cambiar cómo se parsean
  mensajes de WhatsApp con datos inmobiliarios colombianos.
---

# Patrones de Datos — Jhaen Inmobiliarios

## 1. Formatos de precio colombiano

### Regla de oro
Un precio válido debe ser **≥ 30,000,000** (30 millones). Valores menores se
interpretan como millones implícitos (ej: `"800"` → 800,000,000).

### Formatos soportados — en orden de precedencia

#### 1a. Comilla como separador de miles + puntos para decimales de millón
```
850'000.000     →  850_000_000
1'500.000.000   →  1_500_000_000
```
> Aplica tanto comilla recta `'` (U+0027) como tipográfica `'` (U+2019) de teclado móvil.
> Después de la comilla, se usan **puntos** como separadores adicionales.

#### 1b. Puntos como separadores de miles (estilo europeo)
```
$700.000.000    →  700_000_000
700.000.000     →  700_000_000
1.340           →  1_340_000_000   (interpreta "1.340" como 1340 millones)
```
> El punto NO es decimal. `1.340` se lee como `1340` y al estar en rango
> 100–100.000 se asume que el usuario quiso decir "1.340 millones".

#### 1c. Comas como separadores (estilo americano)
```
$700,000,000    →  700_000_000
```

#### 1d. Sufijos de millones (más común en WhatsApp)
```
700 millones    →  700_000_000
700 millon      →  700_000_000
700 mills       →  700_000_000
700 mll         →  700_000_000
700 mls         →  700_000_000
1.200 millones  →  1_200_000_000
```

#### 1e. Sufijo M
```
700M            →  700_000_000
700m            →  700_000_000
```

#### 1f. Número sin separadores (mínimo 9 dígitos)
```
1300000000      →  1_300_000_000
700000000       →  700_000_000
```

#### 1g. Número corto — implícitamente en millones (100–100.000)
```
800             →  800_000_000
5000            →  5_000_000_000
1300            →  1_300_000_000
```
> ⚠️ Rango: 100 ≤ n ≤ 100.000. Fuera de rango se ignora.

---

### Casos problemáticos conocidos

#### ⚠️ Sufijo `m` minúscula con espacio en mensajes informales
Mensajes como `* $550 m` (con punto-asterisco como bullet de WhatsApp) **no se
parsean correctamente** en el flujo actual. Razón:
1. `extract_budget()` busca primero palabras clave (`presupuesto`, `máximo`,
   `hasta`...). El mensaje no las tiene.
2. Cae al bloque `all_prices` (fallback), pero ese bloque **no incluye el
   patrón del sufijo `M`/`m`** — solo busca comillas, puntos-de-miles,
   "millones/mll" y "no más".
3. Resultado: `Budget()` vacío y la propiedad pasa sin filtro de precio.

**Ejemplo real que falla:**
```
Viva Inmobiliaria busca apto en La Loma del Indio
* 3 habitaciones
* 2 baños
* parqueadero
* $550 m
```

**Solución pendiente:** agregar al bloque `all_prices` de `extract_budget()`:
```python
# Sufijo M/m suelto (sin palabra clave de presupuesto)
for match in re.finditer(r"\$?\s*(\d{1,4})\s*[Mm]\b", text):
    num = int(match.group(1)) * 1_000_000
    if num >= 30_000_000:
        all_prices.append(num)
```

> Cualquier nuevo patrón que se agregue a `parse_price()` debe replicarse en
> el bloque `all_prices` de `extract_budget()` para que funcione sin keywords.

---

### Patrones de presupuesto en texto de WhatsApp

```
presupuesto máximo: 850'000.000
presupuesto max: 850M
hasta $700.000.000
máximo 650 millones
tope: 800M
💰 1.200 millones
valor máximo: 1'300.000.000
rango: 800-900M        (toma el mayor)
no sea mas 650
no mas de 750
```

### Márgenes aplicados al precio detectado

```python
# Precio ≤ 1.000M: margen fijo (configurado en config.py)
min_price = max(0, exact - PRICE_MARGIN_BELOW)
max_price = exact + PRICE_MARGIN_ABOVE

# Precio > 1.000M: margen del 7%
min_price = int(exact * 0.93)
max_price = int(exact * 1.07)
```
> `PRICE_MARGIN_ABOVE` y `PRICE_MARGIN_BELOW` están en `app/config.py`. No
> hardcodear valores aquí.

---

## 2. Normalización de texto

### Función `normalize_text()`
Ubicada en `app/normalizer.py`. Aplica antes de cualquier comparación de strings.

**Qué hace:**
1. Convierte a minúsculas
2. Elimina tildes: á→a, é→e, í→i, ó→o, ú→u, ü→u, ñ→n
3. Elimina caracteres especiales irrelevantes
4. Colapsa espacios múltiples

**Regla crítica:** Siempre normalizar AMBOS lados de la comparación:
```python
# ✅ Correcto
normalize_text(barrio_usuario) in normalize_text(zone_label_wasi)

# ❌ Incorrecto — puede fallar por tildes o mayúsculas
barrio_usuario in zone_label_wasi
```

### Pares con/sin tilde más comunes en el dataset

```
Medellín    ↔  medellin
Itagüí      ↔  itagui
Zúñiga      ↔  zuniga
La Abadía   ↔  la abadia
Abadía      ↔  abadia
Las Orquídeas ↔ las orquideas
Alcalá      ↔  alcala
Fátima      ↔  fatima
Jardines    ↔  jardines (sin tilde pero con variante "jardín")
Belén       ↔  belen
```

---

## 3. Alias de ciudades

Entradas válidas en mensajes de WhatsApp que se mapean a nombre canónico:

```
"med", "mede", "medallo", "medellin"  →  "Medellín"
"saba", "sabaneta"                    →  "Sabaneta"
"itag", "itagui", "itagüí"            →  "Itagüí"
"estrella", "la estrella"             →  "La Estrella"
"copa", "copacabana"                  →  "Copacabana"
"envigado"                            →  "Envigado"
"bello"                               →  "Bello"
"caldas"                              →  "Caldas"
```

> Lista completa en `app/locations.py → ALIAS_CIUDADES`.
> Al agregar alias nuevos, agregarlos también normalizados (sin tilde).

---

## 4. Alias de barrios — colisiones conocidas

Algunos nombres de barrio aparecen en **múltiples ciudades**. Cuando esto pasa,
el parser resuelve la ambigüedad por contexto del mensaje:

### Reglas de resolución

**Caso 1 — La solicitud incluye una sola ciudad:**
Si el usuario menciona solo una ciudad y un barrio que existe en varias, se
busca **únicamente en la ciudad mencionada**.
```
"Apto en Poblado, Santa María de los Ángeles"  →  Solo Medellín
"Casa en Envigado, El Campestre"               →  Solo Envigado
```

**Caso 2 — La solicitud incluye ambas ciudades:**
Si el usuario menciona explícitamente ambos municipios y un barrio que existe
en los dos, se busca en **ambos**.
```
"Apto en Medellín o Envigado, sector Campestre"  →  Medellín + Envigado
"Busco en El Poblado o Envigado, Los Balsos"     →  Medellín + Envigado
```

**Caso 3 — Solo se menciona el barrio sin ciudad:**
Se buscan todas las ciudades donde el barrio existe (último recurso).

### Tabla de colisiones

| Barrio                       | Ciudades posibles      |
|------------------------------|------------------------|
| `campestre`                  | Envigado, Medellín     |
| `santa maria de los angeles` | Envigado, Medellín     |
| `los balsos` / `balsos`      | Envigado, Medellín     |
| `san jose`                   | Sabaneta, Envigado     |

> ⚠️ Al agregar barrios con nombre ambiguo:
> - Mantener entradas separadas por ciudad en `BARRIOS` cuando sea posible
>   (ej: `"campestre envigado"`, `"campestre medellin"`).
> - Asegurarse de que el parser tenga acceso a la lista de ciudades
>   mencionadas en el mensaje antes de resolver el barrio.

---

## 5. Formatos de remitente WhatsApp (Whapi)

```
"573026218105@s.whatsapp.net"  →  teléfono local: "3026218105"
"573026218105"                 →  teléfono local: "3026218105"
"120363xxxxxxxx@g.us"         →  grupo, no extrae teléfono
```

**Extracción:**
1. Si contiene `@g.us` → es un grupo, `telefono = None`
2. Separar por `@`, tomar parte izquierda
3. Si empieza con `COUNTRY_CODE` (ej: "57") y tiene más dígitos → remover prefijo
4. Validar: solo dígitos, largo entre 8 y 12 caracteres

> `COUNTRY_CODE` configurado en `app/config.py`.

---

## 6. Patrones de mensaje de WhatsApp — ejemplos reales

### Solicitud típica de asesor
```
Cliente busca apartamento en Envigado, zona baja
Presupuesto máximo: 650 millones
Habitaciones: 3
Área mínima: 90m²
Admon máxima: 400.000
```

### Solicitud informal
```
Hola necesito casa en el poblado alto
hasta 1'200.000.000
3 cuartos mínimo
```

### Con múltiples ubicaciones
```
Busco apto en Sabaneta o Envigado bajo
presupuesto 550 mll
```

### Con bullets de WhatsApp y precio sin keyword
```
Viva Inmobiliaria busca apto en La Loma del Indio
* 3 habitaciones
* 2 baños
* parqueadero
* $550 m
```
> ⚠️ Este formato es común entre asesoras. El parser actual **no captura el
> precio** (`$550 m`) porque no hay palabra clave de presupuesto y el bloque
> de fallback no incluye el patrón de sufijo `M`. Ver "Casos problemáticos
> conocidos" más arriba.

### Sin ubicación (debe retornar advertencia)
```
Busco apartamento de 3 habitaciones
presupuesto 600M
```

---

## 7. Checklist al agregar nuevos patrones

- [ ] Agregar el formato en `price_parser.py → parse_price()` con regex
- [ ] Agregar caso de prueba en el test correspondiente
- [ ] Si es un nuevo barrio: actualizar `locations.py → BARRIOS`
- [ ] Si el barrio pertenece a una zona conceptual: actualizar `matcher.py → ZONE_ALIASES`
- [ ] Si es un nuevo alias de ciudad: actualizar `locations.py → ALIAS_CIUDADES`
- [ ] Verificar colisiones con barrios de otras ciudades
- [ ] Normalizar la nueva entrada (sin tildes, minúsculas) para la clave del dict
