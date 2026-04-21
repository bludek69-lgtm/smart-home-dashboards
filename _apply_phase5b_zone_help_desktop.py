"""
PHASE 5b — ZONE_HELP rozšíření pro DESKTOP varianty (1920x1080, 2880x1800)
Idempotent.

CONTEXT:
  Phase 5 patch updatoval ZONE_HELP jen na RPi (tam byly krátké texty).
  Desktop varianty mají vlastní, detailnější texty — vyžadují separate patching.

ADDS (per zone):
  pracovna: Xiaomi button + Pomodoro
  bedroom:  TV remote + Zvlhčovač
  bathroom: Giuseppe vysavač
  kitchen:  Lednice spotřeba graf
"""
import os
import re

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# Markery pro idempotenci (v komentáři uvnitř textů)
MARKERS = {
    'pracovna': '🎮 Xiaomi button',
    'bedroom':  '📺 TV remote',
    'bathroom': '🤖 Giuseppe',
    'kitchen':  '🧊 Lednice',
}

# Co přidat před closing `]` v items array daného zone
APPENDS = {
    'pracovna': (
        "      '<strong>🎮 Xiaomi button</strong> (Pc Setup) — 6 gest: 1× světlo · 2× PC · 3× kávovar · 4× scéna WORK · long = konec práce',\n"
        "      '<strong>🍅 Pomodoro</strong> — 25/5 min cykly, TTS do kuchyně, persistence v prohlížeči'\n"
    ),
    'bedroom': (
        "      '<strong>📺 TV remote</strong> — Power, Vol, Play, Channel, D-pad, Home/Back, numpad 0-9 (native capabilities)',\n"
        "      '<strong>💧 Zvlhčovač1</strong> — auto zap pod sh_cfg_humidity_low (default 30%), vyp nad sh_cfg_humidity_high (default 45%)'\n"
    ),
    'bathroom': (
        "      '<strong>🤖 Giuseppe</strong> — robotický vysavač (start/stop + battery)'\n"
    ),
    'kitchen': (
        "      '<strong>🧊 Lednice</strong> — live power (W) + sparkline graf (120 vzorků, ~10 min historie)'\n"
    ),
}


def patch_zone(content, zone, marker, append_text, is_crlf):
    """Najde ZONE_HELP[zone] → items: [...] a přidá před poslední ']' nové položky."""
    if marker in content:
        return content, f"⏭ {zone} (už applied, obsahuje '{marker}')"

    # Pattern: matchuje `<zone>: {` ... `items: [` ... `]` (non-greedy)
    # Append před closing `]` uvnitř items array
    nl = '\r\n' if is_crlf else '\n'
    append = append_text.replace('\n', nl) if is_crlf else append_text

    # Find the zone block
    zone_start_pat = rf'  {zone}: \{{'
    m = re.search(zone_start_pat, content)
    if not m:
        return content, f"❌ {zone} (ZONE_HELP[{zone}] nenalezen)"
    start = m.start()

    # From `<zone>: {` find next "items: [" then closing "]"
    items_start = content.find('items: [', start)
    if items_start == -1:
        return content, f"❌ {zone} (items array nenalezen)"
    items_end = content.find(']', items_start)
    if items_end == -1:
        return content, f"❌ {zone} (items closing ] nenalezen)"

    # Ověř že jsme ve správném zone (closing ] by měl být před `flow:`)
    flow_pos = content.find('flow:', items_start)
    if flow_pos != -1 and flow_pos < items_end:
        return content, f"❌ {zone} (items ] překrývá flow:, zone block je rozbitý?)"

    # Zjisti, zda poslední item má na konci čárku
    # Text před `]` může být `'...strong>'` nebo `'...strong>',`
    # Najdi poslední ne-whitespace znak před items_end
    before = content[items_start + len('items: ['):items_end]
    stripped = before.rstrip()
    needs_comma = bool(stripped) and not stripped.endswith(',')

    prefix = ',' + nl if needs_comma else nl
    new_block = prefix + append

    new_content = content[:items_end] + new_block + content[items_end:]
    return new_content, f"+ {zone}"


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP (not found): {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    orig = content
    is_crlf = '\r\n' in content[:4096]
    changes = []

    for zone, marker in MARKERS.items():
        content, msg = patch_zone(content, zone, marker, APPENDS[zone], is_crlf)
        changes.append(msg)

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 5b — ZONE_HELP desktop varianty')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
