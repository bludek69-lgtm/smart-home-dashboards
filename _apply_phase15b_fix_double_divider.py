"""
Phase 15b — kosmetika: odstraní duplicitní <div class="divider"></div>
před PM2.5 alerts toggle (artifact z phase 15 insert).
Idempotentní — pokud už není double divider, nic nedělá.
"""
import os, re

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# Pattern: <div class="divider">  + whitespace + <div class="divider"> + whitespace + pm25 row
DOUBLE_DIV_PATTERN = re.compile(
    r'(<div class="divider"></div>\s*\n\s*)'   # první divider
    r'(<div class="divider"></div>\s*\n\s*)'   # druhý divider (duplicit)
    r'(<div class="tog-row">[^<]*<span class="card-icon">💨</span>)'
)

for path in FILES:
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {path}')
        continue
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    m = DOUBLE_DIV_PATTERN.search(html)
    if not m:
        print(f'  ✓ OK (no double divider): {os.path.basename(path)}')
        continue

    # Nahradit první + druhý divider jen jedním
    new_html = html[:m.start()] + m.group(1) + m.group(3) + html[m.end():]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  ✓ fixed: {os.path.basename(path)} (-{len(html)-len(new_html)} bytes)')

print('Done.')
