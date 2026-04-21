"""
FIX — odstranit duplicitní ZONE_CFG entry pro sh_air_purifier_guard_enabled
po omylem spuštěném druhém běhu phase6 patche.

Také opraví phase6 patch script (dodatečně) aby byl idempotentní.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

DUPLICATE_BLOCK = """    { name: 'sh_air_purifier_guard_enabled',  label: 'Čistička — auto režim (PM2.5)', unit: '', type: 'text',
      desc: 'yes = sh_air_purifier_router_v1 řídí čističku automaticky dle PM2.5. no = čistička běží manuálně. Viz 🌬 tile v Kuchyni.' },
    { name: 'sh_air_purifier_guard_enabled',  label: 'Čistička — auto režim (PM2.5)', unit: '', type: 'text',
      desc: 'yes = sh_air_purifier_router_v1 řídí čističku automaticky dle PM2.5. no = čistička běží manuálně. Viz 🌬 tile v Kuchyni.' },"""

SINGLE_BLOCK = """    { name: 'sh_air_purifier_guard_enabled',  label: 'Čistička — auto režim (PM2.5)', unit: '', type: 'text',
      desc: 'yes = sh_air_purifier_router_v1 řídí čističku automaticky dle PM2.5. no = čistička běží manuálně. Viz 🌬 tile v Kuchyni.' },"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}"); return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    is_crlf = '\r\n' in content[:4096]
    dup = DUPLICATE_BLOCK.replace('\n', '\r\n') if is_crlf else DUPLICATE_BLOCK
    single = SINGLE_BLOCK.replace('\n', '\r\n') if is_crlf else SINGLE_BLOCK

    if dup in content:
        content = content.replace(dup, single, 1)
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ DEDUPLICATED: {os.path.basename(fp)}")
    else:
        # Check if already fixed (single occurrence)
        count = content.count("name: 'sh_air_purifier_guard_enabled'")
        print(f"  ⏭️  OK: {os.path.basename(fp)} ({count}× config entry)")


if __name__ == '__main__':
    print('FIX — remove duplicate purifier config')
    print('=' * 60)
    for f in FILES:
        patch(f)
    print('Hotovo.')
