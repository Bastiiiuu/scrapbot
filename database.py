# ==========================================
# database.py — Toda la lógica de SQLite
# ==========================================
import sqlite3
import logging
from datetime import datetime
from config import DB_PATH

log = logging.getLogger(__name__)


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            url                   TEXT PRIMARY KEY,
            sku                   TEXT,
            tienda                TEXT,
            nombre                TEXT,
            marca                 TEXT,
            precio_normal         INTEGER,
            precio_oferta         INTEGER,
            descuento             TEXT,
            primera_vez_visto     TEXT,
            ultima_vez_notificado TEXT
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sku ON productos(sku)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tienda ON productos(tienda)')

    # Migración: agrega columnas nuevas si se está actualizando desde versión anterior
    migraciones = [
        ('sku',                   'TEXT'),
        ('tienda',                'TEXT'),
        ('primera_vez_visto',     'TEXT'),
        ('ultima_vez_notificado', 'TEXT'),
    ]
    for col, tipo in migraciones:
        try:
            cursor.execute(f"ALTER TABLE productos ADD COLUMN {col} {tipo}")
            log.info(f"Migración: columna '{col}' añadida.")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    log.info(f"Base de datos '{DB_PATH}' lista.")
    return conn


def buscar_producto(cursor, url: str, sku: str | None) -> tuple | None:
    """
    Busca un producto primero por URL normalizada, luego por SKU como fallback.
    Retorna (url_db, precio_oferta, tienda) o None.
    """
    cursor.execute(
        "SELECT url, precio_oferta, tienda FROM productos WHERE url = ?", (url,)
    )
    row = cursor.fetchone()
    if row:
        return row

    if sku:
        cursor.execute(
            "SELECT url, precio_oferta, tienda FROM productos WHERE sku = ?", (sku,)
        )
        row = cursor.fetchone()
        if row:
            # Actualizar la URL a la versión normalizada actual
            cursor.execute("UPDATE productos SET url = ? WHERE sku = ?", (url, sku))
            return row

    return None


def insertar_producto(cursor, producto: dict, tienda: str):
    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO productos
            (url, sku, tienda, nombre, marca, precio_normal, precio_oferta,
             descuento, primera_vez_visto, ultima_vez_notificado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        producto['url'], producto.get('sku'), tienda,
        producto['nombre'], producto['marca'],
        producto['precio_normal'], producto['precio_oferta'],
        producto.get('descuento', ''),
        ahora, ahora
    ))


def actualizar_precio(cursor, url: str, nuevo_precio: int):
    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "UPDATE productos SET precio_oferta = ?, ultima_vez_notificado = ? WHERE url = ?",
        (nuevo_precio, ahora, url)
    )


def actualizar_precio_silencioso(cursor, url: str, nuevo_precio: int):
    """Actualiza precio sin tocar ultima_vez_notificado (para subidas)."""
    cursor.execute(
        "UPDATE productos SET precio_oferta = ? WHERE url = ?",
        (nuevo_precio, url)
    )
