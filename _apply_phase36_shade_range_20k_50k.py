"""
Phase 36 (2026-04-21) — Shade range 20000-50000 lux + helpy

User požaduje rozsah shade thresholdu striktně 20000-50000 lux.
Update:
  - Validation min/max (L5915): min:1000 → min:20000, tip update
  - Config desc (L4405): popis updatnout
  - Roleta-cfg example text (L1585): "Doporučeno 15,000-25,000" → "Nastavitelné 20,000-50,000"
  - + sekundární zmínky v popisech

Idempotentní marker PHASE36_SHADE_RANGE_20_50K.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE36_SHADE_RANGE_20_50K'

SUBS = [
    # 1) Validation range
    (
        "sh_cfg_lux_roleta_shade:   { min:1000, max:50000, tip:'Doporučeno 5000–20000 lux. Hystereze 3000.' },",
        "sh_cfg_lux_roleta_shade:   { min:20000, max:50000, tip:'Nastavitelné 20000–50000 lux. Hystereze 3000.' },"
    ),
    # 2) Config desc (L4405)
    (
        "{ name: 'sh_cfg_lux_roleta_shade',        label: 'Roleta — stínění (silné slunce)', unit: 'lux',\n"
        "      desc: 'Nad touto hodnotou roleta sjede na částečnou pozici (stínění). Hystereze 3000 lux.' },",
        "{ name: 'sh_cfg_lux_roleta_shade',        label: 'Roleta — stínění (silné slunce)', unit: 'lux',\n"
        "      desc: 'Nad touto hodnotou roleta sjede na částečnou pozici (stínění). Rozsah 20000–50000 lux, hystereze 3000 lux.' },"
    ),
    # 3) Other desc variant (L4526)
    (
        "{ name: 'sh_cfg_lux_roleta_shade', label: 'Stínění (silné slunce)', unit: 'lux',",
        "{ name: 'sh_cfg_lux_roleta_shade', label: 'Stínění (silné slunce) · 20k–50k', unit: 'lux',"
    ),
    # 4) Another variant (L5851)
    (
        "{ name: 'sh_cfg_lux_roleta_shade',   label: 'Roleta — stínění (silné slunce)', unit: 'lux',",
        "{ name: 'sh_cfg_lux_roleta_shade',   label: 'Roleta — stínění (silné slunce) · 20k–50k', unit: 'lux',"
    ),
    # 5) Roleta-cfg page example text (already patched by Phase 25, update range)
    (
        "<strong>Reálná data z tvých senzorů</strong> (týden): max <strong>29,812 lux</strong> · top5 ≥ 18,000 · median top15 = 15,360. <span style=\"color:var(--cyan);\">📊 Doporučeno <strong>15,000–25,000</strong></span> + hysteresis 2000–3000. <br>Výš než 30,000 = shade se téměř nikdy nespustí (max reálný lux). Níž než 5000 = shade i při oblačnosti.",
        "<strong>Reálná data z tvých senzorů</strong> (týden): max <strong>29,812 lux</strong> · top5 ≥ 18,000 · median top15 = 15,360. <span style=\"color:var(--cyan);\">📊 Povolený rozsah <strong>20,000–50,000</strong></span> + hysteresis 2000–3000. <br>Nižší hodnoty zamítnuty (shade by se spustil i při oblačnosti). Výš než 35,000 = shade se spustí jen za extrémního slunce."
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
        print(f'  X no substitutions matched: {name}')
        return False

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name} (changes={changes}/{len(SUBS)})')
    return True


def main():
    print('Phase 36: Shade range 20000-50000 lux + helpy')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
