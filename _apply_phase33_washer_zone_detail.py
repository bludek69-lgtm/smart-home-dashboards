"""
Phase 33 (2026-04-21) — Washer tile in Prádelna zone detail

Zone detail page má vlastní renderer (nikoliv renderHomeDevices). Pro Prádelnu
se zóna renderuje v bloku `if (zone === 'pradelna') { ... plugs.boiler ... }`.
Phase 33 přidává analogický blok pro plugs.washer těsně za boiler tile — ve
stejné sect group, vedle boileru.

Idempotentní marker PHASE33_WASHER_ZONE_DETAIL.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE33_WASHER_ZONE_DETAIL'

# Find pradelna block end: "      html += '</div>';\n    }\n  }\n" (close of boiler section + if wrapper)
# Strategy: find "// Prádelna — boiler → tile\n  if (zone === 'pradelna')" block,
# then inject washer tile inside same if-block after the boiler tile close </div>.

# More robust: match the exact pattern at end of boiler tile append:
#   "      html += '</div>';\n    }\n  }\n"
# Inject washer tile generation BEFORE the "    }\n  }" closing.

# Easier: we know the exact code of boiler tile end. Find closing "}\n  }\n\n  // PHASE1_PRACOVNA" or similar.
# Use boundary: "if (zone === 'pradelna') {" ... until matching "}\n  }"
PRADELNA_START = "  // Prádelna — boiler → tile\n  if (zone === 'pradelna') {"
PRADELNA_END   = "      html += '</div>';\n    }\n  }\n"
# Replace the closing with: washer block + closing
PRADELNA_END_NEW = (
    "      html += '</div>';\n"
    "    }\n"
    "    // PHASE33: washer tile\n"
    "    const washer = plugs.washer;\n"
    "    if (washer) {\n"
    "      const wIsOn = !!washer.on;\n"
    "      const wPowerW = washer.power !== null && washer.power !== undefined ? Math.round(washer.power) : null;\n"
    "      const wActive = wPowerW !== null && wPowerW > 5;\n"
    "      html += '<div class=\"sect\">Pračka</div><div class=\"dev-tiles\">';\n"
    "      const tIdxW = _tileData.length;\n"
    "      _tileData.push({key:'washer', name:'Zasuvka pracka pradelna', icon:'🧺', type:'plug', on:wIsOn,\n"
    "        dim:null, hasDim:false, hasTemp:false, temp:null,\n"
    "        power:washer.power!==undefined?washer.power:null, plugTemp:null});\n"
    "      html += '<div class=\"dev-tile' + (wActive ? ' tile-on' : '') + '\" onclick=\"openDeviceDetail(_tileData[' + tIdxW + '])\" title=\"Pračka · klikni pro detail\">' +\n"
    "        '<div class=\"tile-icon\">🧺</div>' +\n"
    "        '<div class=\"tile-name\">Pračka</div>' +\n"
    "        '<div class=\"tile-state ' + (wActive ? 'on' : 'off') + '\">' + (wActive ? wPowerW+'W · perie' : (wIsOn ? 'standby' : 'OFF')) + '</div>' +\n"
    "        '</div>';\n"
    "      html += '</div>';\n"
    "    }\n"
    "  }\n"
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

    # Find pradelna block start
    start_idx = html.find(PRADELNA_START)
    if start_idx < 0:
        print(f'  X pradelna start NOT FOUND: {name}')
        return False

    # Within the pradelna block, find the closing pattern (first occurrence after start)
    search_from = start_idx
    end_idx = html.find(PRADELNA_END, search_from)
    if end_idx < 0:
        print(f'  X pradelna end NOT FOUND: {name}')
        return False

    before = html[:end_idx]
    after = html[end_idx + len(PRADELNA_END):]
    new_html = before + PRADELNA_END_NEW + after
    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK patched: {name} ({len(new_html)-len(html):+d} bytes)')
    return True


def main():
    print('Phase 33: Washer tile in Prádelna zone detail')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
