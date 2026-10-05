"""Configuration constants."""

DEFAULT_TIMEOUT = 10
DEFAULT_THREADS = 10
MAX_FORM_ID = 30
VULNERABLE_VERSION = "4.6.6"

# Bazar template paths
BAZAR_TEMPLATE_PATHS = [
    "/tools/bazar/presentation/templates/widget.tpl.html",
    "/tools/bazar/templates/widget.tpl.html",
]

# Version detection patterns
VERSION_PATTERNS = [
    r'doryphore\s+([\d.]+)',
    r'content="YesWiki\s+v?([\d.]+)"',
    r'yeswiki[/-]v?([\d.]+)',
]

# Widget handler URL
WIDGET_HANDLER = "?wiki=NoSuchPage/widget&id="

# Output files
VULNERABLE_FILE = "vuln.txt"
HOSTILE_PAGE_FILE = "hostile.html"
TARGETS_FILE = "list.txt"

# HTTP Headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# Retry configuration
MAX_RETRIES = 2
BACKOFF_FACTOR = 0.5
RETRY_STATUS_CODES = [500, 502, 503, 504]
