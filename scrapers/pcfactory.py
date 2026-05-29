# ==========================================
# scrapers/pcfactory.py
# Sitio: https://www.pcfactory.cl
#
# PCFactory tiene HTML muy limpio y estático. Es de los más fáciles.
# ==========================================
import logging
from config import URLS_TIENDAS
from utils import normalizar_url, limpiar_precio, extraer_sku_pcfactory
from .base import get_soup, deduplicar

log = logging.getLogger(__name__)


def scrape_pcfactory() -> list[dict]:
    todos = []

    for url_pagina in URLS_TIENDAS.get('pcfactory', []):
        log.info(f"[PCFactory] Scrapeando: {url_pagina}")
        soup = get_soup(url_pagina)
        if not soup:
            continue

        # PCFactory usa <div class="product-box"> o <li class="product-item">
        items = soup.find_all('div', class_='product-box')
        if not items:
            items = soup.find_all('li', class_='product-item')
        log.info(f"[PCFactory] {len(items)} items encontrados")

        for item in items:
            try:
                enlace_tag = item.find('a', class_='product-name') or item.find('a')
                if not enlace_tag:
                    continue
                enlace  = enlace_tag.get('href', '')
                url_raw = enlace if enlace.startswith('http') else f"https://www.pcfactory.cl{enlace}"
                url     = normalizar_url(url_raw)
                sku     = extraer_sku_pcfactory(url)

                nombre_tag = (
                    item.find('span', class_='description') or
                    item.find('p',    class_='product-description') or
                    enlace_tag
                )
                marca_tag = item.find('span', class_='brand')

                # PCFactory muestra precio CLP directamente, sin precio tachado siempre
                precio_oferta_tag = (
                    item.find('span', class_='price') or
                    item.find('div',  class_='product-price')
                )
                precio_normal_tag = item.find('span', class_='price-before')
                descuento_tag     = item.find('span', class_='discount')

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
                log.debug(f"[PCFactory] Error en item: {e}")

    resultado = deduplicar(todos)
    log.info(f"[PCFactory] Total únicos: {len(resultado)}")
    return resultado
