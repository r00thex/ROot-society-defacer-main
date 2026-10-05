"""HTTP client with retry logic."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .constants import (
    DEFAULT_TIMEOUT, MAX_RETRIES, BACKOFF_FACTOR,
    RETRY_STATUS_CODES, DEFAULT_HEADERS
)


class HTTPClient:
    """HTTP client wrapper with retry and session management."""
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.session = self._make_session()
    
    def _make_session(self) -> requests.Session:
        """Create session with retry logic."""
        session = requests.Session()
        
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_CODES
        )
        
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=20,
            pool_maxsize=20
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(DEFAULT_HEADERS)
        
        return session
    
    def get(self, url: str, timeout: int = None, **kwargs):
        """GET request."""
        return self.session.get(
            url, 
            timeout=timeout or self.timeout,
            **kwargs
        )
    
    def close(self):
        """Close session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
