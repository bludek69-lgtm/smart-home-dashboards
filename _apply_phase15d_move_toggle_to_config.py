"""
Phase 15d (2026-04-21) — Přesunout PM2.5 alerts toggle z HOME/OVERRIDES do CONFIG page
Phase 15 ho omylem vložila do sekce PŘEPISY (OVERRIDES), která je na HOME page.
User správně řekl že to v CONFIG nenašel — není tam.

Fix:
1. REMOVE toggle row z HOME OVERRIDES sekce
2. INSERT nový card "ALERTY" do CONFIG page (po cfg-tile-grid, před hint)

Idempotentní — kontrola markeru `tog-pm25-alerts` v OVERRIDES (odstranit) a
nového wrapperu `cfg-alerts-card` (vložit jen pokud chybí).
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# Step 1: REMOVE toggle row z OVERRIDES (+ navazující divider)
# ═══════════════════════════════════════════════════════════════════════════
REMOVE_PATTERN = re.compile(
    r'\s*<div class="divider"></div>\s*\n\s*'
    r'<div class="tog-row"><span class="card-icon">💨</span>'
    r'<span class="tog-lbl"[^>]*title="sh_cfg_pm25_alerts_enabled[^"]*"[^>]*>PM2\.5 alerty</span>'
    r'<div class="toggle" id="tog-pm25-alerts" onclick="toggleVar\(\'sh_cfg_pm25_alerts_enabled\',this\)"></div></div>'
)

# ═══════════════════════════════════════════════════════════════════════════
# Step 2: INSERT nový card do CONFIG page (po cfg-tile-grid, před <p> hint)
# ═══════════════════════════════════════════════════════════════════════════
NEW_CONFIG_CARD = '''

    <!-- ALERTY master switches (v3.4/v2.11/v1.11 config) -->
    <div class="sect" style="color:var(--cyan);margin-top:12px;" id="cfg-alerts-card">
      <span class="help-sect-header">
        <span>ALERTY</span>
        <button class="help-btn" data-help-for="help-cfg-alerts" onclick="toggleHelp('help-cfg-alerts')">ℹ</button>
      </span>
    </div>
    <div id="help-cfg-alerts" class="help-panel">
      <h4>💨 Master přepínače alertů</h4>
      <ul>
        <li><strong>PM2.5 alerty</strong> — TTS hlášení, push notifikace i zmínka v briefingu. <code>OFF</code> = úplně ticho (čistička ale pořád běží).</li>
      </ul>
    </div>
    <div class="card">
      <div class="tog-row">
        <span class="card-icon">💨</span>
        <span class="tog-lbl" title="sh_cfg_pm25_alerts_enabled — PM2.5 TTS/push/briefing. Čistička běží pořád nezávisle.">PM2.5 alerty</span>
        <div class="toggle" id="tog-pm25-alerts" onclick="toggleVar('sh_cfg_pm25_alerts_enabled',this)"></div>
      </div>
    </div>
'''

# Anchor: RPi i desktop varianty — "Pokročilé" hint před ADVANCED link
# RPi: "💡 Pokročilé (Energie, Zásuvky, AI) → <strong>🔧 ADVANCED</strong>."
# Desktop: "💡 Pokročilé nastavení (Energie, Zásuvky, AI) najdeš na stránce <strong>🔧 ADVANCED</strong>."
INSERT_ANCHOR = re.compile(
    r'(\s*</div>\s*\n\s*)'                                          # end of cfg-tile-grid
    r'(<p style="font-size:10px;color:var\(--tx3\);margin:6px 0;[^>]*'
    r'>💡 Pokročilé[^<]*<strong>🔧 ADVANCED</strong>[^<]*</p>)'
)

MARKER_CFG = 'id="cfg-alerts-card"'

def patch_file(path):
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {path}')
        return False

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    orig_len = len(html)
    changed = False

    # Step 1: Remove old toggle row z OVERRIDES (idempotent — pokud už je pryč, OK)
    if 'id="tog-pm25-alerts"' in html and MARKER_CFG not in html:
        # Ještě tam je v OVERRIDES a v CONFIG chybí
        html, n = REMOVE_PATTERN.subn('', html, count=1)
        if n > 0:
            print(f'    - removed from OVERRIDES ({os.path.basename(path)})')
            changed = True
    elif MARKER_CFG in html and 'id="tog-pm25-alerts"' in html:
        # Obě jsou tam — zkontrolovat jestli duplicate v OVERRIDES
        # Pokud je v OVERRIDES, odstranit
        if REMOVE_PATTERN.search(html):
            html, n = REMOVE_PATTERN.subn('', html, count=1)
            if n > 0:
                print(f'    - removed duplicate from OVERRIDES ({os.path.basename(path)})')
                changed = True

    # Step 2: Insert do CONFIG pokud tam ještě není
    if MARKER_CFG not in html:
        m = INSERT_ANCHOR.search(html)
        if not m:
            print(f'  ✗ CONFIG anchor not found: {os.path.basename(path)}')
            return False
        html = html[:m.end(1)] + NEW_CONFIG_CARD + '\n    ' + m.group(2) + html[m.end():]
        print(f'    + inserted into CONFIG page ({os.path.basename(path)})')
        changed = True

    if not changed:
        print(f'  ✓ already correct: {os.path.basename(path)}')
        return True

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    delta = len(html) - orig_len
    print(f'  ✓ patched: {os.path.basename(path)} ({delta:+d} bytes)')
    return True

def main():
    print('Phase 15d: Move PM2.5 toggle from OVERRIDES → CONFIG page')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1

if __name__ == '__main__':
    sys.exit(main())
