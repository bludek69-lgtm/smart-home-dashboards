"""
Phase 39 (2026-04-21) — TOPENÍ page compact layout (no scroll)

User žádost: layout TOPENÍ page bez scrollu. Aktuálně KONFIGURACE a
TÝDENNÍ PROGRAM tlačí obsah pod fold. Řešení:
  1. KONFIGURACE → <details> collapse (default zavřené)
  2. TÝDENNÍ PROGRAM → <details> collapse (default zavřené)

User klikne na summary → rozbalí se obsah. Jinak jen hlavička jako
collapsible header.

Idempotentní marker PHASE39_HEATING_COMPACT.
"""
import os, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE39_HEATING_COMPACT'

# 1. KONFIGURACE — wrap sect + card do <details>
KONF_OLD = (
    '    <div class="sect" style="color:var(--orange);margin-top:12px;">⚙️ KONFIGURACE</div>\n'
    '    <div class="card" style="padding:10px;display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;font-size:11px;font-family:var(--mono);">'
)
KONF_NEW = (
    '    <details style="margin-top:12px;">\n'
    '      <summary class="sect" style="color:var(--orange);cursor:pointer;list-style:none;user-select:none;" title="Klikni pro rozbalení konfigurace topení">⚙️ KONFIGURACE <span style="font-size:10px;color:var(--tx3);">▸ klikni</span></summary>\n'
    '    <div class="card" style="padding:10px;display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;font-size:11px;font-family:var(--mono);margin-top:6px;">'
)

# Konec KONFIGURACE card — close details. Najdu marker na konci: "Config platí po aktivaci..."
KONF_END_OLD = (
    '      <div style="grid-column:span 2;color:var(--tx3);font-size:9px;margin-top:4px;">Config platí po aktivaci 🧠 AI (Rychlé akce). Bez AI se používají jen morning boost cfg.</div>\n'
    '    </div>'
)
KONF_END_NEW = (
    '      <div style="grid-column:span 2;color:var(--tx3);font-size:9px;margin-top:4px;">Config platí po aktivaci 🧠 AI (Rychlé akce). Bez AI se používají jen morning boost cfg.</div>\n'
    '    </div>\n'
    '    </details>'
)

# 2. TÝDENNÍ PROGRAM
SCHED_OLD = (
    '    <!-- SCHEDULE VIEWER -->\n'
    '    <div class="sect" style="color:var(--orange);margin-top:12px;">TÝDENNÍ PROGRAM (read-only MVP)</div>\n'
    '    <div class="card" style="padding:10px;font-family:var(--mono);font-size:11px;color:var(--tx2);">\n'
    '      <div>Editor přijde v Fázi B. Zatím úprava přes Homey Logic nebo CONFIG page (JSON).</div>\n'
    '      <div id="heat-schedule-preview" style="margin-top:8px;"></div>\n'
    '    </div>'
)
SCHED_NEW = (
    '    <!-- SCHEDULE VIEWER -->\n'
    '    <details style="margin-top:12px;">\n'
    '      <summary class="sect" style="color:var(--orange);cursor:pointer;list-style:none;user-select:none;" title="Klikni pro rozbalení týdenního programu">TÝDENNÍ PROGRAM <span style="font-size:10px;color:var(--tx3);">▸ klikni (read-only)</span></summary>\n'
    '    <div class="card" style="padding:10px;font-family:var(--mono);font-size:11px;color:var(--tx2);margin-top:6px;">\n'
    '      <div>Editor přijde v Fázi B. Zatím úprava přes Homey Logic nebo CONFIG page (JSON).</div>\n'
    '      <div id="heat-schedule-preview" style="margin-top:8px;"></div>\n'
    '    </div>\n'
    '    </details>'
)


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
    if KONF_OLD in html:
        html = html.replace(KONF_OLD, KONF_NEW, 1)
        changes += 1
    if KONF_END_OLD in html:
        html = html.replace(KONF_END_OLD, KONF_END_NEW, 1)
        changes += 1
    if SCHED_OLD in html:
        html = html.replace(SCHED_OLD, SCHED_NEW, 1)
        changes += 1

    if changes < 3:
        print(f'  X incomplete: {name} (changes={changes}/3)')
        return False

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name}')
    return True


def main():
    print('Phase 39: TOPENÍ page compact (collapse KONFIGURACE + PROGRAM)')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
