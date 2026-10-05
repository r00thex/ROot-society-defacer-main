"""Mass scanner module."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from core.colors import Colors
from core.http_client import HTTPClient

from .worker import TargetWorker


class MassScanner:
    """Mass scanner for CVE-2026-52774."""
    
    def __init__(self, args):
        self.args = args
        self._lock = threading.Lock()
        self.results = []
        self.stats = {
            "total": 0,
            "scanned": 0,
            "vulnerable": 0,
            "bazar": 0,
            "skipped": 0,
        }
    
    def run(self, targets: List[str]) -> List[Dict]:
        """Run mass scanner."""
        self.stats["total"] = len(targets)
        
        print()
        print(Colors.cyan("=" * 60))
        print(Colors.bold(f"[*] Mass scan: {len(targets)} targets"))
        print(Colors.cyan("-" * 60))
        print()
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=min(10, len(targets))) as pool:
            futures = {}
            
            for url in targets:
                worker = TargetWorker(self.args)
                futures[pool.submit(worker.process_target, url)] = url
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self._process_result(result)
                except Exception:
                    url = futures[future]
                    print(Colors.error(f"{url}"))
                
                if hasattr(self.args, 'delay') and self.args.delay > 0:
                    time.sleep(self.args.delay)
        
        elapsed = time.time() - start_time
        self._print_summary(elapsed)
        
        return self.results
    
    def _process_result(self, result: Dict):
        """Process and log result."""
        with self._lock:
            self.stats["scanned"] += 1
            self.results.append(result)
            
            url = result["url"]
            
            if result["vulnerable"]:
                self.stats["vulnerable"] += 1
                print(Colors.vulnerable(f"[VULN] {url}"))
                if result["xss_url"]:
                    print(f"       XSS: {result['xss_url'][:80]}...")
            elif result["bazar"]:
                self.stats["bazar"] += 1
                print(Colors.yellow(f"[BAZAR] {url}"))
            else:
                self.stats["skipped"] += 1
                print(Colors.dark(f"[SKIP] {url}"))
    
    def _print_summary(self, elapsed: float):
        """Print summary."""
        total = self.stats["total"]
        vulnerable = self.stats["vulnerable"]
        
        print()
        print(Colors.cyan("-" * 60))
        print(f"[*] Results: {vulnerable}/{total} vulnerable")
        print(f"    Time: {elapsed:.2f}s")
