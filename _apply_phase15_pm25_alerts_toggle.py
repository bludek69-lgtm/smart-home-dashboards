"""
Phase 15 (2026-04-21) — PM2.5 alerts master toggle
Přidá toggle row "PM2.5 alerty" do Config sekce všech 3 dashboard variant.
Toggle píše/čte sh_cfg_pm25_alerts_enabled (yes/no).
Idempotentní: pokud už row existuje, nic nedělá.

User reason: čistička je UVNITŘ bytu, user občas kouří → PM2.5 pořád vysoké.
PM2.5 alerty (TTS + push + briefing zmínka) vypnuty. Toggle umožní kdykoliv
zapnout zpět.

Related: sh_gemini_brain_v1 v2.7, sh_context_alert_v1 v1.7, sh_kitchen_ai_v1 v1.11
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

TOGGLE_HTML = (
    '<div class="divider"></div>\n'
    '      <div class="tog-row"><span class="card-icon">💨</span>'
    '<span class="tog-lbl" title="sh_cfg_pm25_alerts_enabled — PM2.5 alerty a briefing hlášení. '
    'Čistička vzduchu běží pořád, nezávisle na tomto toggle.">PM2.5 alerty</span>'
    '<div class="toggle" id="tog-pm25-alerts" onclick="toggleVar(\'sh_cfg_pm25_alerts_enabled\',this)"></div></div>\n      '
)

# Vlož PŘED řádek s "Hlídání čističky" (souvisí spolu = vizuální blízkost)
ANCHOR_PATTERN = re.compile(
    r'(<div class="divider"></div>\s*\n\s*)'
    r'(<div class="tog-row">[^<]*<span class="card-icon">🫁</span>'
    r'<span class="tog-lbl"[^>]*title="sh_air_purifier_guard_enabled[^"]*"[^>]*>Hlídání čističky</span>)',
    re.DOTALL
)

# Idempotence: pokud už toggle existuje, skip
MARKER = 'id="tog-pm25-alerts"'

def patch_file(path):
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {path}')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    if MARKER in html:
        print(f'  ✓ already patched: {os.path.basename(path)}')
        return True

    m = ANCHOR_PATTERN.search(html)
    if not m:
        print(f'  ✗ anchor not found: {os.path.basename(path)}')
        return False

    # Vlož TOGGLE_HTML před divider+purifier row
    before = html[:m.start()]
    anchor_content = m.group(0)  # celý match (divider + purifier row)
    after = html[m.end():]

    # Struktura: [divider][purifier] → [divider][pm25_toggle][divider][purifier]
    # První divider zůstane před pm25, druhý nový divider je součástí TOGGLE_HTML
    # ale tady TOGGLE_HTML začíná s <div class="divider">, takže vloží:
    # [původní divider z anchor][purifier] → vložíme PŘED anchor obě věci
    # aby struktura byla: [divider před][pm25][divider v TOGGLE_HTML][původní divider z anchor][purifier]
    # Lépe: vložit TOGGLE_HTML mezi group(1) a group(2)

    new_html = before + m.group(1) + TOGGLE_HTML + m.group(2) + after

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f'  ✓ patched: {os.path.basename(path)} (+{len(new_html)-len(html)} bytes)')
    return True

def main():
    print('Phase 15: PM2.5 alerts toggle')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1

if __name__ == '__main__':
    sys.exit(main())
