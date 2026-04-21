"""
Phase 16b — doplnit bottom nav tab "TOPENÍ" (fix: phase 16 měl špatný selector)
Bottom nav používá <div class="tab"> ne <button class="nav-btn">.
Vložit mezi tab-zones a tab-audio.
Idempotentní.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

NEW_TAB = '<div class="tab"        id="tab-heating"  onclick="switchPage(\'heating\')"><span class="ti">🔥</span>TOPENÍ</div>\n  '

ANCHOR = re.compile(
    r'(<div class="tab"\s+id="tab-zones"[^<]*onclick="switchPage\(\'zones\'\)"[^>]*>[^<]*<span class="ti">[^<]*</span>ZÓNY</div>\s*\n\s*)'
)

MARKER = 'id="tab-heating"'

for path in FILES:
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {path}')
        continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    if MARKER in html:
        print(f'  ✓ already has tab: {os.path.basename(path)}')
        continue

    m = ANCHOR.search(html)
    if not m:
        print(f'  ✗ tab-zones anchor not found: {os.path.basename(path)}')
        continue

    new_html = html[:m.end(1)] + NEW_TAB + html[m.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  ✓ added tab: {os.path.basename(path)} ({len(new_html)-len(html):+d} bytes)')

print('Done.')
