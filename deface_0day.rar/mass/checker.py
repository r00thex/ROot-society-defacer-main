"""Mass checker module."""

from typing import List, Dict

from core.colors import Colors
from core.http_client import HTTPClient

from exploit.detector import VersionDetector
from exploit.bazar_checker import BazarChecker


class MassChecker:
    """Rapid vulnerability checker."""
    
    def __init__(self, args):
        self.args = args
        self.http = HTTPClient()
        self.detector = VersionDetector(self.http)
        self.bazar_checker = BazarChecker(self.http)
    
    def check_target(self, url: str) -> Dict:
        """Check single target."""
        result = {
            "url": url,
            "version": None,
            "vulnerable": False,
        }
        
        version, _ = self.detector.detect(url)
        result["version"] = version
        
        if version:
            from core.utils import is_vulnerable_version
            result["vulnerable"] = is_vulnerable_version(version)
        
        return result
    
    def close(self):
        self.http.close()
