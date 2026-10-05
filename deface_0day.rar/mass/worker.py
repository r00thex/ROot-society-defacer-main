"""Target worker module."""

from typing import Dict

from core.http_client import HTTPClient
from core.colors import Colors

from exploit.detector import VersionDetector
from exploit.bazar_checker import BazarChecker
from exploit.form_enumerator import FormEnumerator
from exploit.xss_tester import XSSTester
from exploit.payload_generator import PayloadGenerator


class TargetWorker:
    """Worker for processing individual targets."""
    
    def __init__(self, args, http_client: HTTPClient = None):
        self.args = args
        self.http = http_client or HTTPClient()
        self.detector = VersionDetector(self.http)
        self.bazar_checker = BazarChecker(self.http)
        self.form_enumerator = FormEnumerator(self.http)
        self.xss_tester = XSSTester(self.http)
        self.payload_generator = PayloadGenerator()
    
    def process_target(self, url: str) -> Dict:
        """Process single target."""
        result = {
            "url": url,
            "version": None,
            "bazar": False,
            "vulnerable": False,
            "forms": [],
            "xss_url": None,
        }
        
        # Detect version
        version, status = self.detector.detect(url)
        result["version"] = version
        
        # Check Bazar
        bazar = self.bazar_checker.check(url)
        result["bazar"] = bazar
        
        if not bazar:
            return result
        
        # Enumerate forms
        forms = self.form_enumerator.enumerate(url)
        result["forms"] = forms
        
        if not forms:
            return result
        
        # Test XSS
        vulnerable, _, _ = self.xss_tester.test(url, forms[0])
        result["vulnerable"] = vulnerable
        
        if vulnerable:
            result["xss_url"] = self.payload_generator.build_xss_url(url, forms[0])
        
        return result
    
    def close(self):
        """Close HTTP client."""
        self.http.close()
