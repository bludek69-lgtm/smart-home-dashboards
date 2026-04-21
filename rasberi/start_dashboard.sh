#!/bin/bash
# ═══════════════════════════════════════════════════════
# Smart Home Dashboard — Raspberry Pi Auto-Start
# ═══════════════════════════════════════════════════════
#
# INSTALACE:
#   1. chmod +x start_dashboard.sh
#   2. Přidej do autostart:
#      nano ~/.config/lxsession/LXDE-pi/autostart
#      @/home/pi/dashboard/start_dashboard.sh
#
# NEBO jako systemd service:
#   sudo cp dashboard.service /etc/systemd/system/
#   sudo systemctl enable dashboard
#   sudo systemctl start dashboard

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8080
URL="http://localhost:$PORT/smart_home_rpi.html"

echo "╔══════════════════════════════════════╗"
echo "║  Smart Home Dashboard · RPi          ║"
echo "║  http://localhost:$PORT               ║"
echo "╚══════════════════════════════════════╝"

# Vypnout screensaver + power management
xset s off 2>/dev/null
xset -dpms 2>/dev/null
xset s noblank 2>/dev/null

# Skrýt kurzor
unclutter -idle 3 -root &

# Spustit proxy server (na pozadí)
cd "$DIR"
python3 dashboard_server.py &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Počkat až server naběhne
sleep 3

# Spustit Chromium v kiosk mode
chromium-browser \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --disable-translate \
  --disable-features=TranslateUI \
  --disable-session-crashed-bubble \
  --disable-restore-session-state \
  --incognito \
  --disable-gpu-compositing \
  --disable-smooth-scrolling \
  --disable-background-networking \
  --check-for-update-interval=31536000 \
  "$URL"

# Pokud Chromium skončí, zastav server
kill $SERVER_PID 2>/dev/null
