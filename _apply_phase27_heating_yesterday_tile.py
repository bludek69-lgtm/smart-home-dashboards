"""
Phase 27 (2026-04-21) — Heating yesterday runtime tile

Přidá vedle "Runtime dnes" + "≈ kWh" další položku:
   · Včera: 4 h 30 min · 41 kWh

HTML: rozšíří master card runtime row
JS: načte sh_heating_runtime_yesterday_s a sh_cfg_heating_kotel_kw → update spanů

Idempotentní marker PHASE27_HEATING_YESTERDAY.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE27_HEATING_YESTERDAY'

# HTML: replace runtime row — add "Včera" cell after kWh
HTML_PATTERN = re.compile(
    r'(<div>Kotel:\s*<strong id="heat-boiler-state">—</strong></div>\s*\n\s*'
    r'<div>Runtime dnes:\s*<strong id="heat-runtime">0 min</strong></div>\s*\n\s*'
    r'<div>≈\s*<strong id="heat-kwh">0 kWh</strong></div>)\s*\n'
)
HTML_REPLACEMENT = (
    r'\1' + '\n'
    '        <div style="color:var(--tx3);">· Včera: <strong id="heat-runtime-yest" style="color:var(--tx2);">—</strong> <span style="opacity:.7;">·</span> <strong id="heat-kwh-yest" style="color:var(--tx2);">—</strong></div>\n'
)

# JS: add yesterday update after kWh line
JS_PATTERN = re.compile(
    r"(const kwhEl = document\.getElementById\('heat-kwh'\);\s*\n"
    r"\s*if \(kwhEl\) kwhEl\.textContent = kwh \+ ' kWh';)"
)
JS_REPLACEMENT = (
    r'\1' + '\n'
    "    // PHASE27: yesterday runtime + kwh\n"
    "    const rtYestSec = Number((ALL_VARS['sh_heating_runtime_yesterday_s'] || {}).value || 0);\n"
    "    const kwhYest = Math.round((rtYestSec / 3600) * kotelKw * 10) / 10;\n"
    "    const rtYestEl = document.getElementById('heat-runtime-yest');\n"
    "    if (rtYestEl) {\n"
    "      if (rtYestSec > 0) {\n"
    "        const hy = Math.floor(rtYestSec / 3600);\n"
    "        const my = Math.floor((rtYestSec % 3600) / 60);\n"
    "        rtYestEl.textContent = (hy > 0 ? hy + ' h ' : '') + my + ' min';\n"
    "      } else {\n"
    "        rtYestEl.textContent = '—';\n"
    "      }\n"
    "    }\n"
    "    const kwhYestEl = document.getElementById('heat-kwh-yest');\n"
    "    if (kwhYestEl) kwhYestEl.textContent = rtYestSec > 0 ? (kwhYest + ' kWh') : '—';\n"
)


def patch_file(path):
    name = os.path.basename(path)
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {name}')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if MARKER in html:
        print(f'  ✓ already patched: {name}')
        return True

    orig_len = len(html)
    new_html, n_html = HTML_PATTERN.subn(HTML_REPLACEMENT, html, count=1)
    new_html, n_js = JS_PATTERN.subn(JS_REPLACEMENT, new_html, count=1)

    if n_html == 0 or n_js == 0:
        print(f'  ✗ pattern miss: {name} (html={n_html}, js={n_js})')
        return False

    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  ✓ patched: {name} ({len(new_html)-orig_len:+d} bytes, html={n_html}, js={n_js})')
    return True


def main():
    print('Phase 27: Heating yesterday runtime tile')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
