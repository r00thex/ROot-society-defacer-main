"""
Exploitation Framework - Core Module
YesWiki Bazar Widget Reflected XSS
"""

__version__ = "1.0.0"
__author__ = "ROotsociety"
__description__ = "YesWiki Bazar Widget Reflected XSS Framework"
__cve__ = "0DAY"
__cvss__ = "6.1"
__cwe__ = "CWE-79"

from .colors import Colors
from .http_client import HTTPClient
from .utils import *

__all__ = [
    "Colors",
    "HTTPClient",
]
