# ==========================================
# utils.py — Funciones de uso compartido
# ==========================================
import logging
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

log = logging.getLogger(__name__)

# Parámetros de tracking/campaña que varían entre visitas y no identifican al producto
_PARAMS_DINAMICOS = {
    'source', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
    'utm_content', 'ref', 'fbclid', 'gclid', 'WT.srch', 'WT.mc_id',
    's_kwcid', '_lrsc', 'cid', 'icid', 'awc',
}

def normalizar_url(url: str) -> str:
    """Elimina parámetros dinámicos y normaliza la URL para comparación consistente."""
    try:
        parsed = urlparse(url)
        query_limpia = {
            k: v for k, v in parse_qs(parsed.query).items()
            if k not in _PARAMS_DINAMICOS
        }
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip('/'),
            parsed.params,
            urlencode(query_limpia, doseq=True),
            ''
        )).lower()
    except Exception:
        return url.lower().strip()


def extraer_sku_ripley(url: str) -> str | None:
    """Extrae el SKU del final de una URL de Ripley: .../producto--MPE123456"""
    try:
        path = urlparse(url).path
        partes = path.split('--')
        if len(partes) > 1:
            sku = partes[-1].strip('/')
            if sku:
                return f"RIPLEY-{sku.upper()}"
    except Exception:
        pass
    return None


def extraer_sku_falabella(url: str) -> str | None:
    """Extrae el SKU del final de una URL de Falabella: .../producto/123456789"""
    try:
        path = urlparse(url).path.rstrip('/')
        ultimo = path.split('/')[-1]
        if ultimo.isdigit():
            return f"FALABELLA-{ultimo}"
    except Exception:
        pass
    return None


def extraer_sku_paris(url: str) -> str | None:
    """Extrae el SKU de una URL de Paris: .../producto-P123456CL"""
    try:
        path = urlparse(url).path.rstrip('/')
        ultimo = path.split('/')[-1]
        if ultimo:
            return f"PARIS-{ultimo.upper()}"
    except Exception:
        pass
    return None


def extraer_sku_pcfactory(url: str) -> str | None:
    """Extrae el ID de producto de PCFactory: .../producto?id=1234"""
    try:
        params = parse_qs(urlparse(url).query)
        if 'id' in params:
            return f"PCF-{params['id'][0]}"
        # Fallback: último segmento del path
        path = urlparse(url).path.rstrip('/')
        ultimo = path.split('/')[-1]
        if ultimo:
            return f"PCF-{ultimo.upper()}"
    except Exception:
        pass
    return None


def limpiar_precio(precio_str: str) -> int:
    """'$19.990' → 19990. Retorna 0 si no puede parsear."""
    if not precio_str:
        return 0
    limpio = (
        precio_str
        .replace('$', '').replace('.', '')
        .replace(',', '').replace('\xa0', '')
        .strip()
    )
    return int(limpio) if limpio.isdigit() else 0


def formatear_precio(precio: int) -> str:
    """19990 → '$19.990'"""
    return f"${precio:,.0f}".replace(',', '.')
