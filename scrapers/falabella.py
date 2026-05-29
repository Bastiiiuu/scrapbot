# ==========================================
# scrapers/falabella.py
# ==========================================
import logging
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import URLS_TIENDAS
from utils import normalizar_url, limpiar_precio, extraer_sku_falabella
from .base import get_selenium_driver, deduplicar

log = logging.getLogger(__name__)

def scrape_falabella() -> list[dict]:
    todos = []
    
    # 1. Obtenemos el driver de Selenium (desde base.py)
    driver = get_selenium_driver()

    try:
        for url_pagina in URLS_TIENDAS.get('falabella', []):
            log.info(f"[Falabella] Scrapeando con Selenium: {url_pagina}")
            
            try:
                driver.get(url_pagina)
                
                # 2. ESPERA EXPLÍCITA: Falabella tarda en renderizar.
                # Esperamos hasta 15 segundos a que aparezca al menos un "pod" (tarjeta de producto)
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.pod, li.grid-pod"))
                )
                
                # 3. SCROLL: Falabella a veces no carga precios si no haces scroll
                driver.execute_script("window.scrollTo(0, 1500);")
                time.sleep(2) # Pausa breve para renderizado de imágenes/precios
                
                # 4. PASAR A SOUP: Una vez cargado el JS, usamos BeautifulSoup para procesar rápido
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Buscamos los items con los selectores que ya conoces
                items = soup.find_all('div', class_='pod')
                if not items:
                    items = soup.find_all('li', class_='grid-pod')
                
                log.info(f"[Falabella] {len(items)} items encontrados")

                for item in items:
                    try:
                        # Extraer URL
                        enlace_tag = item.find('a', class_='pod-link') or item.find('a')
                        if not enlace_tag: continue
                        
                        enlace = enlace_tag.get('href', '')
                        url_raw = enlace if enlace.startswith('http') else f"https://www.falabella.com{enlace}"
                        url = normalizar_url(url_raw)
                        sku = extraer_sku_falabella(url)

                        # Extraer Nombre y Marca
                        nombre_tag = (
                            item.find('b', class_='pod-subTitle') or
                            item.find('b', class_='subTitle-rebrand') or
                            item.find('b', attrs={'data-id': 'pod-subTitle'})
                        )
                        marca_tag = (
                            item.find('b', class_='pod-title') or
                            item.find('b', class_='title-rebrand')
                        )

                        # Extraer Precios
                        precio_oferta_tag = item.find('li', class_='prices-0')
                        precio_normal_tag = item.find('li', class_='prices-1')

                        if not precio_oferta_tag or not nombre_tag:
                            continue

                        nombre = nombre_tag.text.strip()
                        marca = marca_tag.text.strip() if marca_tag else "Sin marca"
                        p_oferta = limpiar_precio(precio_oferta_tag.text)
                        p_normal = limpiar_precio(precio_normal_tag.text) if precio_normal_tag else p_oferta

                        if p_oferta <= 0 or not nombre:
                            continue

                        todos.append({
                            'url': url, 
                            'sku': sku,
                            'nombre': nombre, 
                            'marca': marca,
                            'precio_normal': p_normal, 
                            'precio_oferta': p_oferta,
                            'descuento': '',
                        })
                    except Exception as e:
                        log.debug(f"[Falabella] Error en item: {e}")
                        
            except Exception as e:
                log.error(f"[Falabella] Error cargando página {url_pagina}: {e}")
                continue # Pasa a la siguiente URL de Falabella si una falla

    finally:
        # 5. CERRAR NAVEGADOR: Es vital para no saturar la memoria RAM
        driver.quit()

    resultado = deduplicar(todos)
    log.info(f"[Falabella] Total únicos extraídos: {len(resultado)}")
    return resultado