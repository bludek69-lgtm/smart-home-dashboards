"""
Phase 41 (2026-04-21) — PŘEPISY (OVERRIDES) compact layout

User: LOG SNAPSHOTS tiles vpravo nahoře stále vyčuhují ~2mm za viewport.
Řešení: zmenšit PŘEPISY sekci (7 tog-row) — kompaktnější padding/font,
odebrat dividery.

AI page má column-count:2 layout s fixed height:calc(100vh - 120px).
Zmenšením PŘEPISY se uvolní prostor pro pravý sloupec.

Idempotentní marker PHASE41_OVERRIDES_COMPACT.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE41_OVERRIDES_COMPACT'

# Wrap overrides card with compact style
# Find: '    <div class="card">\n      <div class="tog-row"><span class="card-icon">💡</span>'
OLD_OPEN = '    <div class="card">\n      <div class="tog-row"><span class="card-icon">💡</span><span class="tog-lbl"'
NEW_OPEN = '    <div class="card ov-compact" style="padding:4px 8px;font-size:11px;">\n      <div class="tog-row" style="padding:2px 0;"><span class="card-icon">💡</span><span class="tog-lbl"'


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

    if OLD_OPEN not in html:
        print(f'  X open pattern miss: {name}')
        return False

    # 1. Replace opening card div
    html = html.replace(OLD_OPEN, NEW_OPEN, 1)

    # 2. Remove all dividers INSIDE this specific card (7 divider patterns around tog-row for overrides)
    # Simpler: find 6 consecutive tog-rows with dividers between them and strip dividers.
    # Easiest: between '    <div class="card ov-compact"...' and next '    </div>\n\n    <div class="sect"'
    # Use regex to narrow block
    pattern = re.compile(
        r'(<div class="card ov-compact"[^>]*>)(.*?)(</div>\s*\n\s*<div class="sect")',
        re.DOTALL
    )
    m = pattern.search(html)
    if not m:
        print(f'  X block boundary not found: {name}')
        return False

    inner = m.group(2)
    # Add compact inline style to every tog-row (not just the first) + remove dividers
    inner_compact = re.sub(
        r'<div class="tog-row"(?![^>]*style="padding:2px)',
        '<div class="tog-row" style="padding:2px 0;"',
        inner
    )
    inner_compact = re.sub(r'<div class="divider"></div>\s*\n\s*', '', inner_compact)

    html = html[:m.start(2)] + inner_compact + html[m.end(2):]

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name}')
    return True


def main():
    print('Phase 41: PŘEPISY (OVERRIDES) compact')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
