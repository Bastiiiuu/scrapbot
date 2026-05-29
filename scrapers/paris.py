# ==========================================
# scrapers/paris.py
# Sitio: https://www.paris.cl
#
# Paris (Cencosud) sirve HTML estático para la mayoría de las listas.
# ==========================================
import logging
from config import URLS_TIENDAS
from utils import normalizar_url, limpiar_precio, extraer_sku_paris
from .base import get_soup, deduplicar

log = logging.getLogger(__name__)


def scrape_paris() -> list[dict]:
    todos = []

    for url_pagina in URLS_TIENDAS.get('paris', []):
        log.info(f"[Paris] Scrapeando: {url_pagina}")
        soup = get_soup(url_pagina)
        if not soup:
            continue

        # Paris usa tarjetas con clase "catalog-product-item"
        items = soup.find_all('div', class_='catalog-product-item')
        if not items:
            items = soup.find_all('article', class_='product-item')
        log.info(f"[Paris] {len(items)} items encontrados")

        for item in items:
            try:
                enlace_tag = item.find('a', class_='product-link') or item.find('a')
                if not enlace_tag:
                    continue
                enlace  = enlace_tag.get('href', '')
                url_raw = enlace if enlace.startswith('http') else f"https://www.paris.cl{enlace}"
                url     = normalizar_url(url_raw)
                sku     = extraer_sku_paris(url)

                nombre_tag = (
                    item.find('div',  class_='product-name') or
                    item.find('span', class_='product-name')
                )
                marca_tag = item.find('div', class_='product-brand')

                precio_oferta_tag = (
                    item.find('span', class_='price-sales') or
                    item.find('span', class_='product-price-sales')
                )
                precio_normal_tag = (
                    item.find('span', class_='price-standard') or
                    item.find('s',    class_='product-price-old')
                )
                descuento_tag = item.find('span', class_='discount-percentage')

                if not precio_oferta_tag or not nombre_tag:
                    continue

                nombre   = nombre_tag.text.strip()
                marca    = marca_tag.text.strip() if marca_tag else "Sin marca"
                p_oferta = limpiar_precio(precio_oferta_tag.text)
                p_normal = limpiar_precio(precio_normal_tag.text) if precio_normal_tag else p_oferta
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
                log.debug(f"[Paris] Error en item: {e}")

    resultado = deduplicar(todos)
    log.info(f"[Paris] Total únicos: {len(resultado)}")
    return resultado
