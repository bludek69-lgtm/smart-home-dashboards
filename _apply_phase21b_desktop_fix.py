"""Phase 21b — fix sanity panel injection v desktop variantách (jiný comment marker)."""
import os, re

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

SANITY_PANEL = '''    <div id="roletaSanityPanel" style="margin-bottom:10px;font-size:11px;padding:8px 12px;border-radius:var(--r2);border:1px solid rgba(100,244,216,.2);background:rgba(100,244,216,.05);">
      <div style="font-weight:600;color:var(--cyan);margin-bottom:4px;">🔍 Kontrola konzistence (sanity check)</div>
      <div id="roletaSanityList" style="color:var(--tx2);line-height:1.5;">—</div>
    </div>

'''

OLD_DESKTOP = '    </div>\n\n    <!-- Config tile grid: 2 columns'
NEW_DESKTOP = '    </div>\n\n' + SANITY_PANEL + '    <!-- Config tile grid: 2 columns'

for p in FILES:
    if not os.path.exists(p):
        print(f'  ✗ missing: {p}'); continue
    with open(p, 'r', encoding='utf-8') as f:
        html = f.read()
    if 'id="roletaSanityPanel"' in html:
        print(f'  ✓ already: {os.path.basename(p)}')
        continue
    if OLD_DESKTOP not in html:
        print(f'  ⚠ anchor not found: {os.path.basename(p)}')
        continue
    html = html.replace(OLD_DESKTOP, NEW_DESKTOP, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ panel added: {os.path.basename(p)}')
print('Done.')
