"""
Phase 19 (2026-04-21) — Roleta yo-yo fix: hystereze + jasné popisky

Řeší user problém: "roleta stínění jezdí nahoru dolu"
Root cause: scheduler používá stejný práh pro shade ↑ a návrat ↓ → jakmile lux
osciluje kolem 20000 (mráček), roleta se neustále přepíná.

Fix (3 vrstvy):
  1. Nová proměnná sh_cfg_lux_roleta_hysteresis (delta pro return-to-open)
     Router v3.9+ bude kontrolovat: pokud jsem v shade, vrátit jen když
     lux < shade_threshold - hysteresis (default 3000).
  2. Dashboard: nový řádek v roleta config "Hystereze (zabraňuje yo-yo)"
  3. Dashboard: lepší popisky — "STÁHNOUT KDYŽ" vs "VYTÁHNOUT KDYŽ"

Proměnná se vytvoří automaticky pokud chybí (graceful default v router).
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'rcfg-hyst'

# ═══════════════════════════════════════════════════════════════════════════
# 1. Nový config řádek (hystereze) — vložit před "večerní zavření"
# ═══════════════════════════════════════════════════════════════════════════
NEW_HYST_ROW = '''      <div class="roleta-cfg-row">
        <div class="roleta-cfg-head">
          <span class="roleta-cfg-name">🔁 Hystereze (proti yo-yo)</span>
          <span class="roleta-cfg-val" id="rcfg-hyst">—</span>
        </div>
        <div class="roleta-cfg-desc"><strong>Co to dělá:</strong> Zabraňuje že roleta osciluje když lux kolísá kolem shade threshold. Když je roleta ve shade módu, vrátí se do otevřené pozice až když lux klesne pod (shade_threshold − hysteresis).</div>
        <div class="roleta-cfg-example">Příklad: hysteresis = 3000, shade = 15000 → stáhne při 15000+, vrátí až při &lt;12000. Doporučeno: 20–30 % z shade hodnoty.</div>
      </div>
'''

# Insert před večerní zavření row
INSERT_ANCHOR = re.compile(
    r'(      <div class="roleta-cfg-row">\s*\n'
    r'        <div class="roleta-cfg-head">\s*\n'
    r'          <span class="roleta-cfg-name">🌆 Večerní zavření</span>)'
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. Lepší popisky pro "stínění při silném slunci"
# ═══════════════════════════════════════════════════════════════════════════
OLD_SHADE_LUX_DESC = (
    '          <span class="roleta-cfg-name">🥵 Stínění při silném slunci</span>\n'
    '          <span class="roleta-cfg-val" id="rcfg-shade-lux">—</span>\n'
    '        </div>\n'
    '        <div class="roleta-cfg-desc"><strong>Co to dělá:</strong> Nad touto hodnotou lux = přímé slunce → stínění.</div>\n'
    '        <div class="roleta-cfg-example">Příklad: 20000 lux. <span style="color:var(--red);">⚠️ Tvé 20177 je hodně — doporučeno 5000–15000.</span></div>'
)
NEW_SHADE_LUX_DESC = (
    '          <span class="roleta-cfg-name">🥵 STÁHNOUT KDYŽ (silné slunce)</span>\n'
    '          <span class="roleta-cfg-val" id="rcfg-shade-lux">—</span>\n'
    '        </div>\n'
    '        <div class="roleta-cfg-desc"><strong>Co to dělá:</strong> Když lux PŘEKROČÍ tuto hodnotu → roleta se <strong>stáhne</strong> do shade pozice (☀️ viz výše).</div>\n'
    '        <div class="roleta-cfg-example">Příklad: 8000 lux. <span style="color:var(--orange);">⚠️ Pokud je hodnota příliš nízká, roleta se bude často pohybovat. Doporučeno 5000–15000 + hysterezis 2000–3000.</span></div>'
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. Update JS rendering pro hysteresis value
# ═══════════════════════════════════════════════════════════════════════════
OLD_RENDER_MAP = "'rcfg-evening':         'sh_cfg_lux_roleta_evening_close',"
NEW_RENDER_MAP = (
    "'rcfg-evening':         'sh_cfg_lux_roleta_evening_close',\n"
    "    'rcfg-hyst':            'sh_cfg_lux_roleta_hysteresis',"
)


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
    changed = False

    # 1. Insert hysteresis row
    m = INSERT_ANCHOR.search(html)
    if m:
        html = html[:m.start()] + NEW_HYST_ROW + m.group(0) + html[m.end():]
        changed = True
    else:
        print(f'  ⚠ hysteresis anchor nenalezen: {os.path.basename(path)}')

    # 2. Update shade_lux description
    if OLD_SHADE_LUX_DESC in html:
        html = html.replace(OLD_SHADE_LUX_DESC, NEW_SHADE_LUX_DESC, 1)
        changed = True
    else:
        print(f'  ⚠ shade_lux desc nenalezen (možná upravené): {os.path.basename(path)}')

    # 3. Update JS rendering map (pokud existuje)
    if OLD_RENDER_MAP in html:
        html = html.replace(OLD_RENDER_MAP, NEW_RENDER_MAP, 1)
        changed = True
    else:
        print(f'  ⚠ render map anchor nenalezen (možná jiné skripty): {os.path.basename(path)}')

    if not changed:
        print(f'  ✗ no changes: {os.path.basename(path)}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(path)} ({len(html)-orig_len:+d} bytes)')
    return True


def main():
    print('Phase 19: Roleta hysteresis + clearer descriptions')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
