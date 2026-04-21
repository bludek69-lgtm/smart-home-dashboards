"""
Phase 37 (2026-04-21) — Roleta simulator shade range fix

Simulátor v renderPredikceRolety (L2315+) má hardcoded old range 500-20000 s
fallback 3000. Uživatel má nyní legitimní shade=30000 který simulátor mylně
hlásí jako "mimo rozsah". Fix:
  - Default: 3000 → 20000
  - Sanity rozsah: 500-20000 → 20000-50000
  - Fallback: 3000 → 20000

Idempotentní marker PHASE37_SIM_SHADE_RANGE.
"""
import os, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE37_SIM_SHADE_RANGE'

SUBS = [
    (
        "shade: Number(_getVar('sh_cfg_lux_roleta_shade') || 3000),",
        "shade: Number(_getVar('sh_cfg_lux_roleta_shade') || 20000),"
    ),
    (
        "const safeShade = (cfg.shade < 500 || cfg.shade > 20000) ? 3000 : cfg.shade;  // FIX 2026-04-20: max 20000",
        "const safeShade = (cfg.shade < 20000 || cfg.shade > 50000) ? 20000 : cfg.shade;  // PHASE37: range 20k-50k"
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

    if changes != len(SUBS):
        print(f'  X incomplete: {name} (changes={changes}/{len(SUBS)})')
        return False

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name}')
    return True


def main():
    print('Phase 37: Roleta simulator shade range 20k-50k')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
