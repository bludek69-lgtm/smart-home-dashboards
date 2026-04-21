"""
Phase 31 (2026-04-21) — Finance TOP 5 → TOP 10

renderFinancePage() zobrazuje jen TOP 5 (m medailí: 🥇🥈🥉 + 4,5).
Rozšířit na TOP 10 (🥇🥈🥉 + 4-10).

Idempotentní marker PHASE31_FINANCE_TOP10.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE31_FINANCE_TOP10'

VARIANTS = [
    (
        "      const m = ['🥇','🥈','🥉','4','5'];\n      for (let i = 0; i < Math.min(sorted.length, 5); i++) {",
        "      const m = ['🥇','🥈','🥉','4','5','6','7','8','9','10'];\n      for (let i = 0; i < Math.min(sorted.length, 10); i++) {"
    ),
    (
        "      const m = ['🥇','🥈','🥉','4️⃣','5️⃣'];\n      for (let i = 0; i < Math.min(sorted.length, 5); i++) {",
        "      const m = ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟'];\n      for (let i = 0; i < Math.min(sorted.length, 10); i++) {"
    ),
    (
        "    const medals = ['🥇','🥈','🥉','4️⃣','5️⃣'];\n      for (let i = 0; i < Math.min(sorted.length, 5); i++) {",
        "    const medals = ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟'];\n      for (let i = 0; i < Math.min(sorted.length, 10); i++) {"
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
    new_html = html
    matched = False
    for OLD, NEW in VARIANTS:
        if OLD in new_html:
            new_html = new_html.replace(OLD, NEW, 1)
            matched = True
            break
    if not matched:
        print(f'  X pattern miss: {name}')
        return False
    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK patched: {name}')
    return True


def main():
    print('Phase 31: Finance TOP 5 -> TOP 10')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
