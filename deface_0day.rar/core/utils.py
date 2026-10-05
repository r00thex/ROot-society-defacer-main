"""Utility functions."""

import re
from typing import Optional, List
from urllib.parse import urljoin, urlparse, quote


def normalize_target(raw: str) -> Optional[str]:
    """Normalize target URL."""
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None
    
    if "://" not in raw:
        raw = "https://" + raw
    
    return raw.rstrip("/")


def parse_targets_file(filepath: str) -> List[str]:
    """Parse targets file."""
    targets = []
    seen = set()
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                target = normalize_target(line)
                if target and target not in seen:
                    seen.add(target)
                    targets.append(target)
    except OSError as e:
        raise IOError(f"Cannot read file {filepath}: {e}")
    
    return targets


def is_vulnerable_version(version: str) -> bool:
    """Check if version is vulnerable (< 4.6.6)."""
    try:
        parts = [int(x) for x in version.split(".")]
        
        if parts[0] < 4:
            return True
        if parts[0] > 4:
            return False
        if parts[1] < 6:
            return True
        if parts[1] > 6:
            return False
        return parts[2] < 6 if len(parts) > 2 else True
    
    except (ValueError, IndexError):
        return False


def save_results(results: List[dict], outfile: str = "vuln.txt") -> None:
    """Save vulnerable results to file."""
    with open(outfile, "a", encoding="utf-8") as f:
        for r in results:
            if r.get("vulnerable"):
                xss = r.get("xss_url") or "N/A"
                version = r.get("version") or "unknown"
                form_id = r.get("forms", ["?"])[0] if r.get("forms") else "?"
                line = f"{r['url']} | {version} | {form_id} | XSS:{xss}"
                f.write(line + "\n")


def save_defacement_page(victim_url: str, outfile: str = "ROotsociety.html") -> str:
    """Save defacement page."""
    from exploit.payload_generator import PayloadGenerator
    
    return PayloadGenerator.save_defacement_page(victim_url, outfile)
