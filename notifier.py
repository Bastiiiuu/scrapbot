# ==========================================
# notifier.py — Mensajes de Telegram
# ==========================================
import requests
import logging
from config import TELEGRAM_TOKEN, CHAT_ID

log = logging.getLogger(__name__)

# Emoji e identidad visual por tienda
TIENDA_META = {
    'ripley':    {'emoji': '🟣', 'nombre': 'Ripley'},
    'falabella': {'emoji': '🟢', 'nombre': 'Falabella'},
    'paris':     {'emoji': '🔵', 'nombre': 'Paris'},
    'pcfactory': {'emoji': '🟠', 'nombre': 'PCFactory'},
}


def _send(mensaje: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": mensaje,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }, timeout=10)
        if r.status_code != 200:
            log.warning(f"Telegram {r.status_code}: {r.text[:120]}")
            return False
        return True
    except Exception as e:
        log.error(f"Error Telegram: {e}")
        return False


def _barra_descuento(pct: float) -> str:
    """Genera una barra visual proporcional al descuento."""
    filled = min(int(pct / 10), 10)   # escala 0–100% → 0–10 bloques
    bar = '█' * filled + '░' * (10 - filled)
    return f"[{bar}] {pct:.0f}%"


def alerta_nuevo_producto(producto: dict, tienda: str) -> bool:
    """
    Envía una alerta de producto nuevo detectado.
    
    producto: dict con keys url, nombre, marca, precio_normal, precio_oferta, descuento
    tienda:   clave de tienda (ripley, falabella, etc.)
    """
    meta = TIENDA_META.get(tienda, {'emoji': '🛍', 'nombre': tienda.capitalize()})

    p_normal = producto['precio_normal']
    p_oferta = producto['precio_oferta']
    nombre   = producto['nombre']
    marca    = producto['marca']
    url      = producto['url']
    descuento = producto.get('descuento', '')

    # Calcular ahorro
    ahorro = p_normal - p_oferta if p_normal > p_oferta else 0
    pct    = (ahorro / p_normal * 100) if p_normal > 0 else 0

    from utils import formatear_precio
    linea_precio = (
        f"<s>{formatear_precio(p_normal)}</s>  →  <b>{formatear_precio(p_oferta)}</b>"
        if ahorro > 0
        else f"<b>{formatear_precio(p_oferta)}</b>"
    )

    ahorro_linea = (
        f"\n💰 <b>Ahorras:</b> {formatear_precio(ahorro)}  {_barra_descuento(pct)}"
        if ahorro > 0
        else ""
    )

    mensaje = (
        f"{meta['emoji']} <b>{meta['nombre'].upper()} — NUEVA OFERTA</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷  <b>{marca}</b>\n"
        f"📦  {nombre}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵  {linea_precio}"
        f"{ahorro_linea}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛒  <a href='{url}'>Ver en {meta['nombre']}</a>"
    )
    return _send(mensaje)


def alerta_precio_bajo(producto: dict, precio_anterior: int, tienda: str) -> bool:
    """
    Envía una alerta cuando un producto ya conocido baja de precio.
    """
    meta = TIENDA_META.get(tienda, {'emoji': '🛍', 'nombre': tienda.capitalize()})

    p_oferta = producto['precio_oferta']
    nombre   = producto['nombre']
    marca    = producto['marca']
    url      = producto['url']

    diferencia = precio_anterior - p_oferta
    pct        = (diferencia / precio_anterior * 100) if precio_anterior > 0 else 0

    from utils import formatear_precio

    mensaje = (
        f"{meta['emoji']} <b>{meta['nombre'].upper()} — ¡PRECIO MÁS BAJO!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷  <b>{marca}</b>\n"
        f"📦  {nombre}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📈  <s>{formatear_precio(precio_anterior)}</s>\n"
        f"🔥  <b>{formatear_precio(p_oferta)}</b>  (↓{pct:.1f}%)\n"
        f"💰  Ahorras {formatear_precio(diferencia)}\n"
        f"    {_barra_descuento(pct)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛒  <a href='{url}'>Ver en {meta['nombre']}</a>"
    )
    return _send(mensaje)


def alerta_resumen(resumen: dict):
    """
    Envía un resumen al final de cada ciclo completo.
    Solo se envía si hubo al menos una novedad.
    """
    total_nuevos = sum(v.get('nuevos', 0) for v in resumen.values())
    total_bajas  = sum(v.get('bajadas', 0) for v in resumen.values())

    if total_nuevos == 0 and total_bajas == 0:
        return  # Sin novedades, no molestar

    lineas = ["📊 <b>Resumen del ciclo</b>\n━━━━━━━━━━━━━━━━━━━━━"]
    for tienda, datos in resumen.items():
        meta = TIENDA_META.get(tienda, {'emoji': '🛍', 'nombre': tienda.capitalize()})
        nuevos  = datos.get('nuevos', 0)
        bajadas = datos.get('bajadas', 0)
        if nuevos > 0 or bajadas > 0:
            lineas.append(
                f"{meta['emoji']} <b>{meta['nombre']}:</b>  "
                f"+{nuevos} nuevas  |  ↓{bajadas} bajaron"
            )

    _send('\n'.join(lineas))
