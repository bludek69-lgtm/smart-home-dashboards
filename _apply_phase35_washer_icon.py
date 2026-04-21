"""
Phase 35 (2026-04-21) — Change washer icon 🧺 → 🫧

User feedback: 🧺 (košík na houby) nevypadá jako pračka.
🫧 (bubbles) je lepší vizuální metafora — čisté prádlo + mýdlová pěna.

Mění ikonu na 3 místech (PLUG_META, device icon detection, zone-detail tile).

Idempotentní marker PHASE35_WASHER_ICON_BUBBLES.
"""
import os, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE35_WASHER_ICON_BUBBLES'

SUBS = [
    # 1) PLUG_META (Phase 32)
    (
        "washer:{icon:'🧺',label:'Pračka'}",
        "washer:{icon:'🫧',label:'Pračka'}",
    ),
    # 2) Zone detail tile (Phase 33): _tileData icon + tile-icon in HTML
    (
        "_tileData.push({key:'washer', name:'Zasuvka pracka pradelna', icon:'🧺'",
        "_tileData.push({key:'washer', name:'Zasuvka pracka pradelna', icon:'🫧'",
    ),
    (
        "'<div class=\"tile-icon\">🧺</div>' +\n"
        "        '<div class=\"tile-name\">Pračka</div>'",
        "'<div class=\"tile-icon\">🫧</div>' +\n"
        "        '<div class=\"tile-name\">Pračka</div>'",
    ),
]


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

    changes = 0
    for old, new in SUBS:
        if old in html:
            html = html.replace(old, new, 1)
            changes += 1

    if changes == 0:
        print(f'  X no patterns found: {name}')
        return False

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name} (changes={changes}/{len(SUBS)})')
    return True


def main():
    print('Phase 35: Washer icon 🧺 → 🫧')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
