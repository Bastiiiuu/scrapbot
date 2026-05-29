# 🤖 ScrapBot — Bot de Ofertas para Tiendas Chilenas

Bot de Python que monitorea precios en Ripley, Falabella, Paris y PCFactory, y envía alertas automáticas a Telegram cuando detecta nuevas ofertas o bajadas de precio significativas.

---

## ✨ Funcionalidades

- Scraping periódico de múltiples tiendas (Ripley, Falabella, Paris, PCFactory)
- Detección de productos nuevos y bajadas de precio
- Alertas en Telegram con formato visual (precio tachado, barra de descuento, ahorro en pesos)
- Resumen consolidado al final de cada ciclo
- Umbral configurable: solo alerta si el precio baja un % mínimo
- Historial de precios en base de datos SQLite local

---

## 📁 Estructura del proyecto

```
scrapbot/
├── main.py           # Orquestador principal y ciclo de ejecución
├── config.py         # Configuración central (lee variables del .env)
├── database.py       # Inicialización y operaciones sobre SQLite
├── notifier.py       # Envío de mensajes a Telegram
├── utils.py          # Utilidades (formateo de precios, etc.)
├── scrapers/
│   ├── __init__.py   # Registro de scrapers disponibles
│   ├── base.py       # Clase base para scrapers
│   ├── ripley.py
│   ├── falabella.py
│   ├── paris.py
│   └── pcfactory.py
├── .env              # Variables de entorno sensibles (NO subir a Git)
├── .env.example      # Plantilla del .env para nuevos colaboradores
├── ofertas.db        # Base de datos SQLite (se crea automáticamente)
└── bot.log           # Log de ejecución
```

---

## ⚙️ Requisitos

- Python 3.10 o superior
- Las dependencias del proyecto (ver abajo)

---

## 🚀 Instalación y configuración

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/scrapbot.git
cd scrapbot
```

### 2. Crea y activa un entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

Si no tienes un `requirements.txt` todavía, las dependencias principales son:

```
requests
python-dotenv
beautifulsoup4
```

### 4. Configura las variables de entorno

Copia el archivo de ejemplo y rellena con tus datos reales:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales de Telegram:

```env
TELEGRAM_TOKEN=123456789:ABCDefgh...
TELEGRAM_CHAT_ID=-1001234567890
```

> **¿Cómo obtener el token?** Habla con [@BotFather](https://t.me/BotFather) en Telegram y crea un bot nuevo.  
> **¿Cómo obtener el Chat ID?** Añade el bot a un grupo y usa [@userinfobot](https://t.me/userinfobot) o consulta la API de Telegram.

### 5. Ejecuta el bot

```bash
python main.py
```

El bot correrá en un loop continuo, ejecutando un ciclo de scraping cada `INTERVALO_MINUTOS` minutos (por defecto, 5).

---

## 🔧 Configuración avanzada

Todas las opciones de comportamiento se pueden ajustar desde el `.env` sin tocar el código:

| Variable                  | Por defecto | Descripción                                              |
|---------------------------|-------------|----------------------------------------------------------|
| `TELEGRAM_TOKEN`          | —           | Token del bot de Telegram **(obligatorio)**              |
| `TELEGRAM_CHAT_ID`        | —           | ID del chat o grupo destino **(obligatorio)**            |
| `INTERVALO_MINUTOS`       | `5`         | Minutos entre cada ciclo de scraping                     |
| `UMBRAL_BAJADA_PORCENTAJE`| `3`         | % mínimo de bajada para enviar alerta                    |
| `TIMEOUT_REQUEST`         | `20`        | Segundos de espera máxima por petición HTTP              |
| `DB_PATH`                 | `ofertas.db`| Ruta del archivo de base de datos SQLite                 |

Para activar o desactivar tiendas, edita la lista `TIENDAS_ACTIVAS` en `config.py`. Para cambiar las URLs monitoreadas por tienda, edita el diccionario `URLS_TIENDAS` en el mismo archivo.

---

## 🔒 Seguridad

El archivo `.env` contiene información sensible (tokens de API). Asegúrate de que esté incluido en `.gitignore`:

```
# .gitignore
.env
ofertas.db
bot.log
.venv/
__pycache__/
```

**Nunca** subas el `.env` a un repositorio público.

---

## 📊 Tipos de alertas en Telegram

**Nueva oferta detectada:**
```
🟣 RIPLEY — NUEVA OFERTA
━━━━━━━━━━━━━━━━━━━━━
🏷  Samsung
📦  Smart TV 55" QLED
━━━━━━━━━━━━━━━━━━━━━
💵  ~~$699.990~~  →  $499.990
💰 Ahorras: $200.000  [████████░░] 28%
━━━━━━━━━━━━━━━━━━━━━
🛒  Ver en Ripley
```

**Bajada de precio:**
```
🟢 FALABELLA — ¡PRECIO MÁS BAJO!
━━━━━━━━━━━━━━━━━━━━━
🏷  LG
📦  Monitor 27" IPS 144Hz
━━━━━━━━━━━━━━━━━━━━━
📈  ~~$289.990~~
🔥  $239.990  (↓17.2%)
💰  Ahorras $50.000
    [█████████░] 17%
━━━━━━━━━━━━━━━━━━━━━
🛒  Ver en Falabella
```

---

## 🤝 Contribuir

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-tienda`)
3. Haz commit de tus cambios (`git commit -m 'Agrega scraper para XYZ'`)
4. Abre un Pull Request

---

## 📝 Licencia

MIT
