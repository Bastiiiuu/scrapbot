from .ripley    import scrape_ripley
from .falabella import scrape_falabella
from .paris     import scrape_paris
from .pcfactory import scrape_pcfactory

SCRAPERS = {
    'ripley':    scrape_ripley,
    'falabella': scrape_falabella,
    'paris':     scrape_paris,
    'pcfactory': scrape_pcfactory,
}
