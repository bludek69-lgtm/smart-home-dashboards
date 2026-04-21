"""
Phase 42 (2026-04-21) — LOG SNAPSHOTS g4 → g2 (fit into right column)

AI page má column-count:2 layout. LOG SNAPSHOTS mají tile-grid.g4 (4 sloupce)
což v pravém column layoutu (~48% šířky obrazovky) přetéká za pravý bok.

Fix: přepnout na 2 sloupce (12 tiles = 6 řad × 2 sloupce) + max-width:100%.

Idempotentní marker PHASE42_LOG_SNAPSHOTS_G2.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE42_LOG_SNAPSHOTS_G2'


def patch_file(path):
    name = os.path.basename(path)
    if not os.path.exists(path):
        print(f'  X NOT FOUND: {name}')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if MARKER in html:
        print(f'  OK already patched: {name}')
        return True

    # Find the LOG SNAPSHOTS section boundary
    # Start: <div class="sect" ...>📦 LOG SNAPSHOTS</...>
    # End: <div class="sect" ...>🤖 GEMINI DIAGNOSTIKA
    start_pat = re.compile(r'<div class="sect"[^>]*>\s*<span class="help-sect-header">\s*<span>📦 LOG SNAPSHOTS</span>')
    end_pat = re.compile(r'<div class="sect"[^>]*>\s*<span class="help-sect-header">\s*<span>🤖 GEMINI DIAGNOSTIKA')

    m_start = start_pat.search(html)
    m_end = end_pat.search(html)
    if not m_start or not m_end:
        print(f'  X boundaries not found: {name}')
        return False

    block = html[m_start.start():m_end.start()]

    # Replace all `<div class="tile-grid g4" style="margin-bottom:6px;">` with 2-col variant
    new_block = re.sub(
        r'<div class="tile-grid g4" style="margin-bottom:6px;">',
        '<div class="tile-grid" style="grid-template-columns:repeat(2,1fr);gap:4px;margin-bottom:4px;max-width:100%;">',
        block
    )
    count = len(re.findall(r'grid-template-columns:repeat\(2,1fr\)', new_block))
    if count == 0:
        print(f'  X no g4 grids to convert: {name}')
        return False

    new_html = html[:m_start.start()] + new_block + html[m_end.start():]
    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK patched: {name} (grids converted: {count})')
    return True


def main():
    print('Phase 42: LOG SNAPSHOTS g4 → g2')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
