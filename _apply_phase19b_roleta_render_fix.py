"""Phase 19b — fix rendering mapping pro hysteresis row (byl wrong pattern v 19)."""
import os, re

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD_LINE = "    ['rcfg-evening',  'sh_cfg_lux_roleta_evening_close',' lux','int'],"
NEW_LINE = (
    "    ['rcfg-evening',  'sh_cfg_lux_roleta_evening_close',' lux','int'],\n"
    "    ['rcfg-hyst',     'sh_cfg_lux_roleta_hysteresis',  ' lux', 'int'],"
)

for p in FILES:
    if not os.path.exists(p):
        print(f'  ✗ missing: {p}'); continue
    with open(p, 'r', encoding='utf-8') as f:
        html = f.read()
    if 'rcfg-hyst' in html and "'sh_cfg_lux_roleta_hysteresis'" in html:
        print(f'  ✓ already: {os.path.basename(p)}')
        continue
    if OLD_LINE not in html:
        print(f'  ⚠ anchor not found: {os.path.basename(p)}')
        continue
    html = html.replace(OLD_LINE, NEW_LINE, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(p)}')
print('Done.')
