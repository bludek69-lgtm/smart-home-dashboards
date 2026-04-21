"""
Smart Home Dashboard Server
Spustí lokální server na portu 8080:
 - Servíruje HTML dashboard soubory
 - Proxuje API požadavky na Homey Pro (žádné CORS problémy)

POUŽITÍ:
  1. Ulož tento soubor do složky s dashboardy
  2. Spusť: python dashboard_server.py
  3. Otevři: http://localhost:8080/smart_home_dashboard_v2.html
"""

import http.server
import json
import urllib.request
import urllib.error
import os
import sys

PORT = 8080
HOMEY_HOST = "http://192.168.1.142"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Proxy API requests to Homey
        if self.path.startswith('/api/'):
            self._proxy_to_homey('GET')
            return
        # Serve static files normally
        super().do_GET()

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self._proxy_to_homey('PUT')
            return
        self.send_error(405)

    def do_POST(self):
        if self.path.startswith('/api/'):
            self._proxy_to_homey('POST')
            return
        self.send_error(405)

    def _proxy_to_homey(self, method):
        try:
            url = HOMEY_HOST + self.path
            # Read request body for PUT/POST
            body = None
            if method in ('PUT', 'POST'):
                length = int(self.headers.get('Content-Length', 0))
                if length > 0:
                    body = self.rfile.read(length)

            # Build request to Homey
            req = urllib.request.Request(url, data=body, method=method)

            # Forward Authorization header
            auth = self.headers.get('Authorization', '')
            if auth:
                req.add_header('Authorization', auth)
            if body:
                req.add_header('Content-Type', 'application/json')

            # Execute request
            resp = urllib.request.urlopen(req, timeout=10)
            data = resp.read()

            # Send response back
            self.send_response(resp.status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        # Color API requests differently
        msg = format % args
        if '/api/' in msg:
            print(f"  🔗 PROXY {msg}")
        else:
            print(f"  📄 {msg}")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(__file__) else '.')
    print(f"""
╔══════════════════════════════════════════════╗
║   Smart Home Dashboard Server                ║
║   http://localhost:{PORT}                      ║
║   Proxy → {HOMEY_HOST}            ║
║                                              ║
║   Otevři v Chrome:                           ║
║   http://localhost:{PORT}/smart_home_dashboard_v2.html  ║
║                                              ║
║   Ctrl+C pro zastavení                       ║
╚══════════════════════════════════════════════╝
""")

    # V dashboardu nastav IP na: http://localhost:8080
    # (proxy přesměruje /api/ požadavky na Homey)
    print(f"⚠  V dashboardu CONFIG nastav Homey IP na: http://localhost:{PORT}")
    print(f"   Proxy automaticky přesměruje na {HOMEY_HOST}\n")

    server = http.server.HTTPServer(('', PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server zastaven.")
        server.server_close()
