"""
Phase 34 (2026-04-21) — Merge washer into pradelna room-card data

Pradelna room-card / zone-card zobrazuje indicators z `r.pradelna` (kterou
posílá bridge). Bridge má `rooms.pradelna = {light, boiler, motion}` ale washer
je v `plugs.washer`. Proto se washer ikona neobjeví v room-card indicators.

Fix (stejný vzor jako bedroom): volat mergePlugs(r.pradelna, ['washer']) při
updateRoomFloor + updateZoneCard.

Idempotentní marker PHASE34_PRADELNA_WASHER_MERGE.
"""
import os, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE34_PRADELNA_WASHER_MERGE'

# Two lines need to change — both must succeed (count=2)
OLD_FLOOR = "  updateRoomFloor('pradelna', r.pradelna);"
NEW_FLOOR = "  updateRoomFloor('pradelna', mergePlugs(r.pradelna, ['washer']));"

OLD_CARD = "  updateZoneCard('pradelna', r.pradelna);"
NEW_CARD = "  updateZoneCard('pradelna', mergePlugs(r.pradelna, ['washer']));"


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
    if OLD_FLOOR in html:
        html = html.replace(OLD_FLOOR, NEW_FLOOR, 1)
        changes += 1
    if OLD_CARD in html:
        html = html.replace(OLD_CARD, NEW_CARD, 1)
        changes += 1

    if changes < 2:
        print(f'  X incomplete: {name} (changes={changes}/2)')
        return False

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name} (changes={changes})')
    return True


def main():
    print('Phase 34: Merge washer into pradelna room-card data')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
