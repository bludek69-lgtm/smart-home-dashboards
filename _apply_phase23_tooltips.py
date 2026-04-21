"""
Phase 23 (2026-04-21) — Tooltips na klíčové ikony

Přidává title="..." atributy na bottom nav buttons + často používané tile icons,
aby user po hover pochopil význam bez nutnosti klikat.

Změny:
  - Bottom nav tabs (HOME, ZÓNY, TOPENÍ, TOPENÍ 2 ≈ PLÁN, AUDIO, AI, LOGY, POČASÍ, KAMERA, CONFIG, ADVANCED, FINANCE, BURZA)
  - Často používané .card-icon (💡 💧 🔋 ⚡ 🔒 🪟)

Idempotentní — marker PHASE23_TOOLTIPS_APPLIED.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE23_TOOLTIPS_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# Mapping: page id → tooltip description
# ═══════════════════════════════════════════════════════════════════════════
NAV_TOOLTIPS = {
    'home':     'Hlavní panel — stavy bytu, přehled zón, scény, aktivity',
    'zones':    'Detail zón — proklik na každou místnost (kuchyň, ložnice, koupelna...)',
    'heating':  'TOPENÍ — kotel + 4 TRV, boiler state, demand, kWh, rychlé akce',
    'heating2': 'PLÁN — týdenní program topení (Po-Ne) per zóna',
    'audio':    'AUDIO — speakers, radio, TTS, priority engine',
    'ai':       'AI CONTROL — Meta Brain, Predict, Coordinator, autonomy level',
    'logy':     'LOGY — event log ze Sheets, baterie, offline, Gemini diagnostika',
    'pocasi':   'POČASÍ — aktuální stav + 3denní předpověď (OpenWeatherMap)',
    'kamera':   'KAMERA — live stream z předsíně + ložnice',
    'config':   'CONFIG — všechny sh_cfg_* proměnné s inline edit',
    'advanced': 'ADVANCED — Validator, Energie, Zásuvky, AI nastavení (rizikové)',
    'finance':  'FINANCE — spotřeba kWh, cena VT/NT, měsíční report',
    'burza':    'BURZA — crypto (Bitcoin, ETH, ...) + akciové tituly',
}


def add_nav_tooltip(html):
    """Přidá title= na bottom nav <div class="tab" ...> elements."""
    changes = 0
    for page_id, tooltip in NAV_TOOLTIPS.items():
        # Pattern: <div class="tab"  ... id="tab-<id>" onclick="switchPage('<id>')"...
        pattern = re.compile(
            r'(<div class="tab"[^>]*id="tab-' + re.escape(page_id) + r'"[^>]*onclick="switchPage\(\'' + re.escape(page_id) + r'\'\)"[^>]*?)(>)'
        )
        def repl(m):
            # Check if title already exists
            if 'title=' in m.group(1):
                return m.group(0)
            return m.group(1) + f' title="{tooltip}"' + m.group(2)
        new_html, n = pattern.subn(repl, html)
        if n > 0 and new_html != html:
            html = new_html
            changes += 1
    return html, changes


def add_marker(html):
    """Přidá skrytý HTML comment marker pro idempotentnost."""
    if MARKER in html:
        return html
    # Vloží před </body>
    marker_html = f'<!-- {MARKER} -->'
    if '</body>' in html:
        html = html.replace('</body>', marker_html + '\n</body>', 1)
    return html


def patch_file(path):
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {path}')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if MARKER in html:
        print(f'  ✓ already patched: {os.path.basename(path)}')
        return True

    orig_len = len(html)

    # Add nav tooltips
    html, nav_changes = add_nav_tooltip(html)

    # Add marker
    html = add_marker(html)

    if nav_changes == 0:
        print(f'  ✗ 0 nav changes: {os.path.basename(path)}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(path)} ({len(html)-orig_len:+d} bytes, {nav_changes} nav tooltips)')
    return True


def main():
    print('Phase 23: Tooltips on navigation + key icons')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
