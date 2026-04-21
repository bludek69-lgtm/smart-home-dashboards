#!/bin/bash
# Smart Home Dashboard — RPi installer
# Stáhni oba soubory do Downloads → spusť: bash install.sh

D="$HOME/dashboard"
mkdir -p "$D"

# Najdi HTML v Downloads
H=$(ls ~/Downloads/smart_home_rpi.html 2>/dev/null || ls ~/Downloads/smart_home*.html 2>/dev/null | head -1)
[ -z "$H" ] && echo "❌ Nenašel jsem smart_home_rpi.html v ~/Downloads" && exit 1
cp "$H" "$D/index.html"
echo "✅ Dashboard zkopírován"

# Proxy server
cat > "$D/server.py" << 'S'
import http.server,json,urllib.request,urllib.error,os
PORT=8080;HOMEY="http://192.168.1.142"
class P(http.server.SimpleHTTPRequestHandler):
 def do_GET(self):
  if self.path.startswith('/api/'):self._p('GET')
  else:super().do_GET()
 def do_PUT(self):self._p('PUT')
 def do_POST(self):self._p('POST')
 def do_OPTIONS(self):
  self.send_response(204)
  for h,v in[('Access-Control-Allow-Origin','*'),('Access-Control-Allow-Methods','GET,PUT,POST,OPTIONS'),('Access-Control-Allow-Headers','Authorization,Content-Type')]:self.send_header(h,v)
  self.end_headers()
 def _p(self,m):
  try:
   b=None
   if m in('PUT','POST'):
    l=int(self.headers.get('Content-Length',0))
    if l>0:b=self.rfile.read(l)
   r=urllib.request.Request(HOMEY+self.path,data=b,method=m)
   a=self.headers.get('Authorization','')
   if a:r.add_header('Authorization',a)
   if b:r.add_header('Content-Type','application/json')
   resp=urllib.request.urlopen(r,timeout=10)
   d=resp.read()
   self.send_response(resp.status);self.send_header('Content-Type','application/json');self.send_header('Access-Control-Allow-Origin','*');self.end_headers();self.wfile.write(d)
  except Exception as e:
   self.send_response(502);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps({"error":str(e)}).encode())
 def log_message(self,f,*a):
  if '/api/' in (f%a):print(f"  API {f%a}")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Dashboard http://localhost:{PORT} → {HOMEY}")
http.server.HTTPServer(('',PORT),P).serve_forever()
S
echo "✅ Server vytvořen"

# Start skript
cat > "$D/start.sh" << E
#!/bin/bash
cd $D
xset s off -dpms s noblank 2>/dev/null
which unclutter >/dev/null && unclutter -idle 3 -root &
python3 server.py &
sleep 2
chromium-browser --kiosk --noerrdialogs --disable-infobars --incognito --disable-gpu-compositing http://localhost:8080/index.html
E
chmod +x "$D/start.sh"
echo "✅ Start skript vytvořen"

# Autostart
AS="$HOME/.config/lxsession/LXDE-pi/autostart"
mkdir -p "$(dirname $AS)"
grep -q "dashboard/start.sh" "$AS" 2>/dev/null || echo "@$D/start.sh" >> "$AS"
echo "✅ Autostart nastaven"

# Screensaver off
xset s off 2>/dev/null; xset -dpms 2>/dev/null
sudo apt-get install -y unclutter 2>/dev/null

echo ""
echo "✅ HOTOVO! Spusť: $D/start.sh"
echo "   Po restartu RPi se spustí automaticky."
echo ""
read -p "Spustit teď? [y/N]: " a
[ "$a" = "y" ] && exec "$D/start.sh"
