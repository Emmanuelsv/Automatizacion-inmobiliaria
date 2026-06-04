import os
from dotenv import load_dotenv

load_dotenv()

WASI_COMPANY_ID = os.getenv("WASI_COMPANY_ID", "")
WASI_TOKEN = os.getenv("WASI_TOKEN", "")
WASI_BASE_URL = os.getenv("WASI_BASE_URL", "https://api.wasi.co/v1")

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "")
WHAPI_URL = os.getenv("WHAPI_URL", "https://gate.whapi.cloud/")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://angular-studio-doorbell.ngrok-free.dev")


APP_PORT = int(os.getenv("APP_PORT", "5000"))
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "57")

PRICE_MARGIN_ABOVE = int(os.getenv("PRICE_MARGIN_ABOVE", "80000000"))
PRICE_MARGIN_BELOW = int(os.getenv("PRICE_MARGIN_BELOW", "100000000"))

MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))

