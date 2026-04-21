"""Desktop varianty home tile onclick — regex-based (title text se liší)."""
import os
import re

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

TILES = [
    ('s-presence-tile', 'presence'),
    ('s-phase-tile', 'phase'),
    ('s-sleep-tile', 'sleep'),
    ('s-health-tile', 'health'),
    ('s-intent-tile', 'intent'),
    ('s-power-tile', 'power'),
    ('s-state-tile', 'house_state'),
    ('s-visitor-tile', 'visitor'),
]


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    orig = c
    added = 0
    skipped = 0

    for tile_id, kind in TILES:
        # Pattern: <div class="tile ht" id="s-X-tile" title="..."> (without onclick)
        # We only match tiles that DON'T already have onclick
        pat = re.compile(
            r'(<div class="tile ht" id="' + re.escape(tile_id) + r'" title=")([^"]*)(">)',
        )
        def repl(m):
            return (
                '<div class="tile ht" id="' + tile_id + '" '
                'onclick="openHomeTileModal(\'' + kind + '\')" '
                'title="' + m.group(2) + ' · klikni pro detail" '
                'style="cursor:pointer;">'
            )
        new_c, n = pat.subn(repl, c, count=1)
        if n > 0:
            c = new_c
            added += 1
        else:
            skipped += 1

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}: +{added} · skipped {skipped}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}: skipped {skipped}')


if __name__ == '__main__':
    for f in FILES:
        patch(f)
