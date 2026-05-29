# ==========================================
# config.py — Configuración central
# Las variables sensibles se cargan desde .env
# ==========================================

import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

# --- Telegram (sensibles → vienen del .env) ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID        = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("Faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en el archivo .env")

# --- Comportamiento del bot ---
INTERVALO_MINUTOS        = int(os.getenv('INTERVALO_MINUTOS', 5))   # Cada cuántos minutos corre el ciclo
UMBRAL_BAJADA_PORCENTAJE = int(os.getenv('UMBRAL_BAJADA_PORCENTAJE', 3))  # Alerta solo si baja al menos este %
TIMEOUT_REQUEST          = int(os.getenv('TIMEOUT_REQUEST', 20))    # Segundos de espera máxima por request HTTP

# --- Base de datos ---
DB_PATH = os.getenv('DB_PATH', 'ofertas.db')

# --- Tiendas activas ---
# Comenta las que no quieras monitorear
TIENDAS_ACTIVAS = [
    'ripley',
    'falabella',
    'paris',
    'pcfactory',
]

# --- URLs a monitorear por tienda ---
URLS_TIENDAS = {
    'ripley':    [
        "https://simple.ripley.cl/tecno?source=menu",
        "https://simple.ripley.cl/electro?source=menu",
    ],
    'falabella': [
        "https://www.falabella.com/falabella-cl/category/cat7090034/Tecnologia?&f",
        "https://www.falabella.com/falabella-cl/category/cat4152/Television-y-Video",
    ],
    'paris':     [
        "https://www.paris.cl/tecnologia/computacion/",
        "https://www.paris.cl/tecnologia/television/",
    ],
    'pcfactory': [
        "https://www.pcfactory.cl/notebooks",
        "https://www.pcfactory.cl/monitores",
    ],
}