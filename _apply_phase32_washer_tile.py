"""
Phase 32 (2026-04-21) — Washer plug tile on home page

Přidá 🧺 Pračku do:
  - HOME_ZONES.pradelna.plugs (bylo ['boiler'] → ['boiler','washer'])
  - PLUG_META: washer → {icon:'🧺', label:'Pračka'}

Dashboard pak zobrazí tile v home page pradelna sekci s power draw.
Finance tracking automatický (scan všech měřených zásuvek).

Idempotentní marker PHASE32_WASHER_TILE.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE32_WASHER_TILE'

# HOME_ZONES pradelna line
HZ_OLD = "{ key: 'pradelna', name: 'Prádelna', plugs: ['boiler'] },"
HZ_NEW = "{ key: 'pradelna', name: 'Prádelna', plugs: ['boiler','washer'] },"

# PLUG_META — insert washer line before closing }; of PLUG_META (allow whitespace variants)
PM_OLD = "  boiler:{icon:'🔥',label:'Boiler'},\n};"
PM_NEW = "  boiler:{icon:'🔥',label:'Boiler'},\n  washer:{icon:'🧺',label:'Pračka'},\n};"


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

    orig_len = len(html)
    changes = 0

    if HZ_OLD in html:
        html = html.replace(HZ_OLD, HZ_NEW, 1)
        changes += 1

    if PM_OLD in html:
        html = html.replace(PM_OLD, PM_NEW, 1)
        changes += 1

    if changes < 2:
        print(f'  X incomplete: {name} (changes={changes}/2)')
        return False

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name} ({len(html)-orig_len:+d} bytes)')
    return True


def main():
    print('Phase 32: Washer plug tile on home page')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
