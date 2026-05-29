# ==========================================
# scrapers/ripley.py
# Sitio: https://simple.ripley.cl
# ==========================================
import logging
from config import URLS_TIENDAS
from utils import normalizar_url, limpiar_precio, extraer_sku_ripley
from .base import get_soup, deduplicar

log = logging.getLogger(__name__)


def scrape_ripley() -> list[dict]:
    """Extrae productos de todas las URLs configuradas para Ripley."""
    todos = []

    for url_pagina in URLS_TIENDAS.get('ripley', []):
        log.info(f"[Ripley] Scrapeando: {url_pagina}")
        soup = get_soup(url_pagina)
        if not soup:
            continue

        items = soup.find_all('a', class_='product-link')
        log.info(f"[Ripley] {len(items)} items encontrados en {url_pagina}")

        for item in items:
            try:
                enlace = item.get('href', '')
                if not enlace:
                    continue

                url_raw = enlace if enlace.startswith('http') else f"https://simple.ripley.cl{enlace}"
                url     = normalizar_url(url_raw)
                sku     = extraer_sku_ripley(url)

                nombre_tag        = item.find('p',    class_='jsx-a5660653bf8d0e9f product-item--name')
                marca_tag         = item.find('span', class_='jsx-a5660653bf8d0e9f product-item--brand')
                precio_normal_tag = item.find('span', class_='jsx-3118646438 product-price-old-price product-price-strikethrough')
                precio_oferta_tag = item.find('span', class_='jsx-3118646438 product-price-price product-price-country-cl product-price-no-strikethrough')
                descuento_tag     = item.find('span', class_='jsx-3118646438 product-price-discount')

                if not precio_oferta_tag or not nombre_tag:
                    continue

                nombre    = nombre_tag.text.strip()
                marca     = marca_tag.text.strip() if marca_tag else "Sin marca"
                p_oferta  = limpiar_precio(precio_oferta_tag.text)
                p_normal  = limpiar_precio(precio_normal_tag.text) if precio_normal_tag else p_oferta
                descuento = descuento_tag.text.strip() if descuento_tag else ""

                if p_oferta <= 0 or not nombre:
                    continue

                todos.append({
                    'url': url, 'sku': sku,
                    'nombre': nombre, 'marca': marca,
                    'precio_normal': p_normal, 'precio_oferta': p_oferta,
                    'descuento': descuento,
                })
            except Exception as e:
                log.debug(f"[Ripley] Error en item: {e}")

    resultado = deduplicar(todos)
    log.info(f"[Ripley] Total únicos: {len(resultado)}")
    return resultado
