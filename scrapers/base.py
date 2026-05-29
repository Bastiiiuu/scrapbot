# scrapers/base.py corregido
import requests
import logging
from bs4 import BeautifulSoup
from utils import normalizar_url, limpiar_precio
from config import TIMEOUT_REQUEST

# --- NUEVAS IMPORTACIONES PARA SELENIUM ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
# ------------------------------------------

log = logging.getLogger(__name__)

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

def get_soup(url: str, headers: dict | None = None) -> BeautifulSoup | None:
    # ... (tu función actual se mantiene igual para Ripley)
    hdrs = {**BASE_HEADERS, **(headers or {})}
    try:
        r = requests.get(url, headers=hdrs, timeout=TIMEOUT_REQUEST)
        r.raise_for_status()
        return BeautifulSoup(r.text, 'html.parser')
    except requests.RequestException as e:
        log.error(f"Error descargando {url}: {e}")
        return None

# NUEVA FUNCIÓN:
def get_selenium_driver():
    """Configura y retorna un navegador Chrome invisible."""
    options = Options()
    options.add_argument("--headless")  # No abre la ventana
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={BASE_HEADERS['User-Agent']}")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def deduplicar(productos: list[dict]) -> list[dict]:
    # ... (se mantiene igual)
    vistos_url = set()
    resultado  = []
    for p in productos:
        if p['url'] not in vistos_url:
            vistos_url.add(p['url'])
            resultado.append(p)
    return resultado