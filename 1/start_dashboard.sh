#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  Smart Home Dashboard — Raspberry Pi INSTALLER
#  Spusť z Downloads: chmod +x install_dashboard.sh && ./install_dashboard.sh
# ═══════════════════════════════════════════════════════════

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="/home/$USER/dashboard"
PORT=8080

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  🍓 Smart Home Dashboard — RPi Installer        ║"
echo "║                                                  ║"
echo "║  Zdroj:  $SCRIPT_DIR"
echo "║  Cíl:    $INSTALL_DIR"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── 1. Vytvoř cílový adresář ──────────────────────────
echo "📁 Vytvářím $INSTALL_DIR ..."
mkdir -p "$INSTALL_DIR"

# ── 2. Zkopíruj dashboard HTML ────────────────────────
HTML_SRC=""
for f in "$SCRIPT_DIR"/smart_home_rpi.html "$SCRIPT_DIR"/smart_home_dashboard*.html "$SCRIPT_DIR"/smart_home_tablet.html; do
  if [ -f "$f" ]; then
    HTML_SRC="$f"
    break
  fi
done

if [ -z "$HTML_SRC" ]; then
  echo "❌ Nenalezen žádný smart_home*.html v $SCRIPT_DIR"
  echo "   Stáhni smart_home_rpi.html do stejné složky jako tento skript."
  exit 1
fi

cp "$HTML_SRC" "$INSTALL_DIR/smart_home_rpi.html"
echo "✅ Dashboard: $(basename $HTML_SRC) → smart_home_rpi.html"

# ── 3. Vytvoř proxy server (přímo v instalátoru) ──────
cat > "$INSTALL_DIR/dashboard_server.py" << 'SERVEREOF'
import http.server, json, urllib.request, urllib.error, os, sys

PORT = 8080
HOMEY_HOST = "http://192.168.1.142"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/'):
            self._proxy('GET')
        else:
            super().do_GET()

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self._proxy('PUT')
        else:
            self.send_error(405)

    def do_POST(self):
        if self.path.startswith('/api/'):
            self._proxy('POST')
        else:
            self.send_error(405)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()

    def _proxy(self, method):
        try:
            url = HOMEY_HOST + self.path
            body = None
            if method in ('PUT', 'POST'):
                length = int(self.headers.get('Content-Length', 0))
                if length > 0:
                    body = self.rfile.read(length)
            req = urllib.request.Request(url, data=body, method=method)
            auth = self.headers.get('Authorization', '')
            if auth:
                req.add_header('Authorization', auth)
            if body:
                req.add_header('Content-Type', 'application/json')
            resp = urllib.request.urlopen(req, timeout=10)
            data = resp.read()
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

    def log_message(self, format, *args):
        msg = format % args
        if '/api/' in msg:
            print(f"  API {msg}")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Dashboard server on http://localhost:{PORT}")
    print(f"Proxy → {HOMEY_HOST}")
    server = http.server.HTTPServer(('', PORT), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
SERVEREOF
echo "✅ Proxy server vytvořen"

# ── 4. Vytvoř start skript ────────────────────────────
cat > "$INSTALL_DIR/start.sh" << STARTEOF
#!/bin/bash
cd "$INSTALL_DIR"

# Vypnout screensaver + power management
xset s off 2>/dev/null
xset -dpms 2>/dev/null
xset s noblank 2>/dev/null

# Skrýt kurzor (pokud nainstalován)
which unclutter >/dev/null 2>&1 && unclutter -idle 3 -root &

# Spustit proxy server
python3 dashboard_server.py &
sleep 2

# Chromium kiosk
chromium-browser \\
  --kiosk \\
  --noerrdialogs \\
  --disable-infobars \\
  --disable-translate \\
  --disable-session-crashed-bubble \\
  --incognito \\
  --disable-gpu-compositing \\
  --disable-smooth-scrolling \\
  http://localhost:$PORT/smart_home_rpi.html
STARTEOF
chmod +x "$INSTALL_DIR/start.sh"
echo "✅ Start skript vytvořen"

# ── 5. Nainstaluj unclutter (skrytí kurzoru) ──────────
echo ""
echo "📦 Instaluji unclutter (skrytí kurzoru)..."
sudo apt-get install -y unclutter 2>/dev/null || echo "⚠ unclutter se nepodařilo nainstalovat (nepovinné)"

# ── 6. Vypni screensaver ──────────────────────────────
echo ""
echo "🔧 Vypínám screensaver..."
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

# Pokud existuje lightdm config
if [ -f /etc/lightdm/lightdm.conf ]; then
  if ! grep -q "xserver-command=X -s 0 -dpms" /etc/lightdm/lightdm.conf; then
    sudo sed -i '/^\[Seat:\*\]/a xserver-command=X -s 0 -dpms' /etc/lightdm/lightdm.conf 2>/dev/null || true
    echo "✅ lightdm screensaver vypnut"
  fi
fi

# ── 7. Nastav autostart ──────────────────────────────
echo ""
echo "🚀 Nastavuji autostart..."
AUTOSTART_DIR="$HOME/.config/lxsession/LXDE-pi"
mkdir -p "$AUTOSTART_DIR"
AUTOSTART_FILE="$AUTOSTART_DIR/autostart"

# Vytvoř autostart pokud neexistuje
if [ ! -f "$AUTOSTART_FILE" ]; then
  cat > "$AUTOSTART_FILE" << AUTOEOF
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
AUTOEOF
fi

# Přidej dashboard pokud tam ještě není
if ! grep -q "start.sh" "$AUTOSTART_FILE" 2>/dev/null; then
  echo "@$INSTALL_DIR/start.sh" >> "$AUTOSTART_FILE"
  echo "✅ Autostart přidán do $AUTOSTART_FILE"
else
  echo "✅ Autostart už existuje"
fi

# ── 8. Hotovo ─────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ INSTALACE DOKONČENA                          ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║                                                  ║"
echo "║  Soubory:                                        ║"
echo "║    $INSTALL_DIR/smart_home_rpi.html"
echo "║    $INSTALL_DIR/dashboard_server.py"
echo "║    $INSTALL_DIR/start.sh"
echo "║                                                  ║"
echo "║  Spuštění:                                       ║"
echo "║    $INSTALL_DIR/start.sh"
echo "║                                                  ║"
echo "║  Po restartu RPi se dashboard spustí             ║"
echo "║  automaticky v kiosk mode.                       ║"
echo "║                                                  ║"
echo "║  ⚠ RPi musí být na WiFi 'smhome'                ║"
echo "║    (stejná síť jako Homey 192.168.1.142)         ║"
echo "║                                                  ║"
echo "║  Chceš spustit teď? (y/n)                        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
read -p "Spustit dashboard? [y/N]: " answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
  exec "$INSTALL_DIR/start.sh"
fi
