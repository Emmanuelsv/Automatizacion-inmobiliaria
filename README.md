# Jhaen Inmobiliarios — Automatización WhatsApp + Wasi

Automatización que recibe solicitudes de inmuebles desde grupos de WhatsApp (vía Evolution API), extrae los datos con regex Python, busca en el inventario Wasi y envía los resultados al asesor.

**Sin IA** — toda la extracción es con `re`, diccionarios y lógica condicional.

---

## Arquitectura

```
WhatsApp (Grupo)
    ↓ webhook
Evolution API (localhost:8080)
    ↓ HTTP POST
n8n (localhost:5678)  →  Webhook → IF grupo → Extraer texto → API Python → IF solicitud → Enviar WA
                                                                    ↓
                                                         FastAPI (localhost:5000)
                                                         parser + Wasi + matcher
```

---

## Levantar todo con Docker

### 1. Clonar y configurar credenciales

```bash
cd jhaen-whatsapp-automation
cp .env.example .env
```

Editar `.env` con tus credenciales reales:

```env
WASI_COMPANY_ID=123456          # Panel Wasi → Configuración → API
WASI_TOKEN=tu_token_secreto
EVOLUTION_API_KEY=jhaen-inmobiliarios-2026-key-evolution-api
```

### 2. Subir el stack

```bash
docker compose up -d --build
```

Servicios disponibles:
| Servicio | URL |
|----------|-----|
| n8n | http://localhost:5678 |
| Evolution API | http://localhost:8080 |
| API Python | http://localhost:5000 |
docker compose up -d --build
---

## Obtener credenciales de Wasi

1. Ingresar al panel Wasi: https://app.wasi.co
2. Ir a **Configuración → Integración → API**
3. Copiar `Company ID` y `Token`
4. Pegarlos en `.env`

---

## Conectar WhatsApp (escanear QR)

1. Abrir http://localhost:8080/manager (Evolution API Manager)
2. Crear instancia con nombre `jhaen-inmobiliarios`
3. Hacer clic en **Connect** y escanear el QR con WhatsApp del asesor/número de la inmobiliaria
4. Configurar el webhook en la instancia:
   - URL: `http://n8n:5678/webhook/whatsapp-inmobiliaria`
   - Eventos: `MESSAGES_UPSERT`

---

## Importar el workflow en n8n

1. Abrir http://localhost:5678 (usuario: `admin`, contraseña: `mye-n8n-2025`)
2. Ir a **Workflows → Import from file**
3. Seleccionar `n8n_workflow.json`
4. Activar el workflow con el toggle

---

## Verificar que la API Python funciona

```bash
# Health check
curl http://localhost:5000/health
# {"status":"ok","service":"mye-parser"}

# Test de parseo (sin Wasi)
curl -X POST http://localhost:5000/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Busco apartamento en El Poblado\nPresupuesto: $500.000.000\n2 habitaciones\nAsesor: Emmanuel Sanchez\nContacto: 3021222188"
  }'

# Proceso completo (requiere credenciales Wasi en .env)
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Solicitud de Propiedad – Apartamento\nUbicación deseada: Loma del Chocho, El Campestre\nPresupuesto máximo: $700.000.000\nMínimo 2 habitaciones\nÁrea desde 80 m²\nAdministración máximo $600.000\nCliente: Valentina Carvajal\nAsesor: Emmanuel Sanchez\nContacto: 3021222188\nMYE Inmobiliaria"
  }'
```

---

## Probar con un mensaje de ejemplo

Enviar al grupo de WhatsApp:

```
Solicitud de Propiedad – Apartamento 🏡
📍 Ubicación deseada: Loma del Chocho, El Campestre, Zúñiga
💰 Presupuesto máximo: $700.000.000
💳 Modo de pago: Crédito hipotecario
🔑 Características:
  • Área desde 80 m² en adelante
  • Mínimo 2 habitaciones
  • Administración máximo $600.000

👩‍💼 Cliente: Valentina Carvajal
👨‍💼 Asesor: Emmanuel Sanchez
📱 Contacto: 3021222188
MYE Inmobiliaria 🏡
```

El asesor recibirá automáticamente por WhatsApp los inmuebles del inventario Wasi que coincidan.

---

## Correr tests

```bash
cd jhaen-whatsapp-automation
pip install -r requirements.txt
python3 -m pytest tests/ -v
```

---

## Agregar barrios

Editar [app/locations.py](app/locations.py) — agregar entradas al diccionario `BARRIOS`:

```python
"nombre del barrio": {"nombre": "Nombre Oficial", "ciudad": "Ciudad"},
```

---

## URLs entre servicios Docker

| Desde | Hacia | URL |
|-------|-------|-----|
| n8n | API Python | `http://mye-parser:5000` |
| n8n | Evolution API | `http://evolution-api:8080` |
| API Python | Wasi | `https://api.wasi.co/v1` (externo) |
| Evolution API | n8n (webhook) | `http://n8n:5678/webhook/whatsapp-inmobiliaria` |
| Navegador | n8n | `http://localhost:5678` |
| Navegador | API Python | `http://localhost:5000` |
| Navegador | Evolution API | `http://localhost:8080` |
