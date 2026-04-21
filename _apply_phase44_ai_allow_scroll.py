"""
Phase 44 (2026-04-21) — AI page allow vertical scroll

AI page má overflow:hidden !important — content pod fold (LOG SNAPSHOTS dolní
řady, GEMINI DIAGNOSTIKA) je nepřístupný. Řešení: přepnout na overflow-y:auto.

Idempotentní marker PHASE44_AI_ALLOW_SCROLL.
"""
import os, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE44_AI_ALLOW_SCROLL'

OLD = '#page-ai.active, #page-logy.active{overflow:hidden !important;}'
NEW = '#page-logy.active{overflow:hidden !important;}\n#page-ai.active{overflow-y:auto !important;overflow-x:hidden !important;scrollbar-width:thin;}'


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
    if OLD not in html:
        print(f'  X pattern miss: {name}')
        return False
    html = html.replace(OLD, NEW, 1)
    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name}')
    return True


def main():
    print('Phase 44: AI page allow vertical scroll')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
