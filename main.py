# ==========================================
# main.py — Orquestador principal
# ==========================================
print("Iniciando bot de ofertas...")

import sys
import time
import logging
import sqlite3
from config import INTERVALO_MINUTOS, TIENDAS_ACTIVAS, UMBRAL_BAJADA_PORCENTAJE
from database import init_db, buscar_producto, insertar_producto, actualizar_precio, actualizar_precio_silencioso
from notifier import alerta_nuevo_producto, alerta_precio_bajo, alerta_resumen
from scrapers import SCRAPERS

# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8'),
    ]
)
log = logging.getLogger(__name__)


# ==========================================
# PROCESAMIENTO
# ==========================================
def procesar_tienda(conn: sqlite3.Connection, tienda: str, productos: list[dict]) -> dict:
    """
    Compara los productos scrapeados con la DB y dispara notificaciones.
    Retorna un resumen {'nuevos': int, 'bajadas': int, 'subidas': int, 'sin_cambios': int}.
    """
    cursor = conn.cursor()
    stats  = {'nuevos': 0, 'bajadas': 0, 'subidas': 0, 'sin_cambios': 0}

    for p in productos:
        url      = p['url']
        sku      = p.get('sku')
        p_oferta = p['precio_oferta']

        existente = buscar_producto(cursor, url, sku)

        if existente is None:
            # ── NUEVO ────────────────────────────────
            insertar_producto(cursor, p, tienda)
            if alerta_nuevo_producto(p, tienda):
                stats['nuevos'] += 1
                log.info(f"[{tienda.upper()}] NUEVO → {p['nombre']} | {p['precio_oferta']:,}")

        else:
            url_db, precio_db, _ = existente

            if precio_db and precio_db > 0:
                variacion = ((precio_db - p_oferta) / precio_db) * 100
            else:
                variacion = 0

            if p_oferta < precio_db:
                if variacion >= UMBRAL_BAJADA_PORCENTAJE:
                    # ── BAJÓ (notificar) ──────────────────
                    actualizar_precio(cursor, url_db, p_oferta)
                    if alerta_precio_bajo(p, precio_db, tienda):
                        stats['bajadas'] += 1
                        log.info(f"[{tienda.upper()}] BAJÓ {variacion:.1f}% → {p['nombre']} | {precio_db:,} → {p_oferta:,}")
                else:
                    # Bajó menos del umbral, actualizar sin alertar
                    actualizar_precio_silencioso(cursor, url_db, p_oferta)

            elif p_oferta > precio_db:
                # ── SUBIÓ (silencioso) ────────────────────
                actualizar_precio_silencioso(cursor, url_db, p_oferta)
                stats['subidas'] += 1

            else:
                stats['sin_cambios'] += 1

    conn.commit()
    return stats


# ==========================================
# CICLO PRINCIPAL
# ==========================================
def ejecutar_ciclo(conn: sqlite3.Connection):
    resumen_global = {}

    for tienda in TIENDAS_ACTIVAS:
        scraper = SCRAPERS.get(tienda)
        if not scraper:
            log.warning(f"No existe scraper para '{tienda}', omitiendo.")
            continue

        log.info(f"━━━ Procesando {tienda.upper()} ━━━")
        try:
            productos = scraper()

            if not productos:
                log.warning(f"[{tienda}] Sin productos extraídos. ¿Cambió el HTML?")
                continue

            stats = procesar_tienda(conn, tienda, productos)
            resumen_global[tienda] = stats
            log.info(
                f"[{tienda.upper()}] Nuevos:{stats['nuevos']} Bajadas:{stats['bajadas']} "
                f"Subidas:{stats['subidas']} Sin cambios:{stats['sin_cambios']}"
            )

        except Exception as e:
            log.exception(f"[{tienda}] Error inesperado: {e}")

    # Enviar resumen consolidado solo si hubo novedades
    alerta_resumen(resumen_global)


if __name__ == "__main__":
    log.info("=" * 55)
    log.info("  BOT DE OFERTAS — Tiendas: " + ", ".join(TIENDAS_ACTIVAS))
    log.info(f"  Intervalo: {INTERVALO_MINUTOS} min | Umbral bajada: {UMBRAL_BAJADA_PORCENTAJE}%")
    log.info("=" * 55)

    conexion = init_db()

    try:
        while True:
            log.info("─── Nuevo ciclo ───────────────────────────────")
            ejecutar_ciclo(conexion)
            log.info(f"Durmiendo {INTERVALO_MINUTOS} min...\n")
            time.sleep(INTERVALO_MINUTOS * 60)

    except KeyboardInterrupt:
        log.info("Bot detenido manualmente.")
    finally:
        conexion.close()
        log.info("Conexión a la base de datos cerrada.")
