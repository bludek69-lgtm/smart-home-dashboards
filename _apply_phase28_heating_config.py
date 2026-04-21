"""
Phase 28 (2026-04-21) — Heating configuration section in TOPENÍ page

Přidá sekci "⚙️ KONFIGURACE" mezi RYCHLÉ AKCE a TÝDENNÍ PROGRAM v TOPENÍ page.
Obsahuje 9 number inputů pro cfg proměnné (morning boost + AI vrstvy).

Inputs s validací (min/max), onchange → saveHeatingCfg() → writeVar.
Refresh načte hodnoty do inputů (pokud user nemá focus).

Cfg vars (9):
  morning: bath_boost_temp (23), bath_boost_min (60)
  AI:      wake_weekday_min (195), wake_weekend_min (315), prewake_window_min (30),
           prewake_bath_delta (2), prewake_toilet_delta (1),
           occupancy_age_max_s (600), occupancy_bonus (0.5)

Idempotentní marker PHASE28_HEATING_CONFIG.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE28_HEATING_CONFIG'

# HTML inject: after RYCHLÉ AKCE btn-row, before TÝDENNÍ PROGRAM
HTML_PATTERN = re.compile(
    r'(<div class="btn" style="border-color:var\(--red\);color:var\(--red\);" onclick="setHeatingMode\(\'off\'\)">⏸ Vše OFF</div>\s*\n'
    r'\s*<div class="btn" id="heat-ai-btn" onclick="toggleHeatingAi\(\)" title="[^"]*">🧠 AI: —</div>\s*\n'
    r'\s*</div>)\s*\n'
    r'(\s*<!-- SCHEDULE VIEWER -->)'
)

HTML_REPLACEMENT = (
    r'\1' + '\n'
    '\n'
    '    <!-- PHASE28: KONFIGURACE TOPENÍ -->\n'
    '    <div class="sect" style="color:var(--orange);margin-top:12px;">⚙️ KONFIGURACE</div>\n'
    '    <div class="card" style="padding:10px;display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;font-size:11px;font-family:var(--mono);">\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Cílová teplota koupelny při ranní rutině (override)">\n'
    '        <span style="color:var(--tx2);">🚿 Koupelna ráno °C</span>\n'
    '        <input type="number" step="0.5" min="18" max="28" id="cfg-h-bath-temp" onchange="saveHeatingCfg(\'sh_cfg_heating_morning_bath_boost_temp\',this.value,23)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Jak dlouho koupelna drží boost po ranní rutině (minuty)">\n'
    '        <span style="color:var(--tx2);">🚿 Koupelna boost min</span>\n'
    '        <input type="number" step="5" min="10" max="180" id="cfg-h-bath-min" onchange="saveHeatingCfg(\'sh_cfg_heating_morning_bath_boost_min\',this.value,60)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Čas alarmu PO-PÁ v minutách od půlnoci (195 = 3:15)">\n'
    '        <span style="color:var(--tx2);">⏰ Alarm PO-PÁ (min)</span>\n'
    '        <input type="number" step="15" min="0" max="1439" id="cfg-h-wake-wd" onchange="saveHeatingCfg(\'sh_cfg_heating_wake_weekday_min\',this.value,195)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Čas alarmu SO-NE v minutách od půlnoci (315 = 5:15)">\n'
    '        <span style="color:var(--tx2);">⏰ Alarm SO-NE (min)</span>\n'
    '        <input type="number" step="15" min="0" max="1439" id="cfg-h-wake-we" onchange="saveHeatingCfg(\'sh_cfg_heating_wake_weekend_min\',this.value,315)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Pre-heat okno před alarmem (minuty)">\n'
    '        <span style="color:var(--tx2);">🧠 Pre-heat okno min</span>\n'
    '        <input type="number" step="5" min="5" max="60" id="cfg-h-prewake-win" onchange="saveHeatingCfg(\'sh_cfg_heating_prewake_window_min\',this.value,30)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Pre-heat koupelna delta °C (AI přidá k target)">\n'
    '        <span style="color:var(--tx2);">🧠 Koupelna +°C</span>\n'
    '        <input type="number" step="0.5" min="0" max="5" id="cfg-h-prewake-bath" onchange="saveHeatingCfg(\'sh_cfg_heating_prewake_bath_delta\',this.value,2)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Pre-heat toaleta delta °C (AI přidá k target)">\n'
    '        <span style="color:var(--tx2);">🧠 Toaleta +°C</span>\n'
    '        <input type="number" step="0.5" min="0" max="5" id="cfg-h-prewake-toi" onchange="saveHeatingCfg(\'sh_cfg_heating_prewake_toilet_delta\',this.value,1)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;" title="Max stáří motion eventu pro occupancy bonus (sekundy)">\n'
    '        <span style="color:var(--tx2);">🧠 Motion max age s</span>\n'
    '        <input type="number" step="60" min="60" max="3600" id="cfg-h-occ-age" onchange="saveHeatingCfg(\'sh_cfg_heating_occupancy_age_max_s\',this.value,600)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <label style="display:flex;flex-direction:column;gap:2px;grid-column:span 2;" title="Occupancy bonus delta °C (AI přidá když je user v zóně)">\n'
    '        <span style="color:var(--tx2);">🧠 Occupancy +°C</span>\n'
    '        <input type="number" step="0.1" min="0" max="2" id="cfg-h-occ-bonus" onchange="saveHeatingCfg(\'sh_cfg_heating_occupancy_bonus\',this.value,0.5)" style="padding:4px;background:var(--bg3);border:1px solid var(--bd);color:var(--tx);border-radius:4px;font-family:var(--mono);">\n'
    '      </label>\n'
    '      <div style="grid-column:span 2;color:var(--tx3);font-size:9px;margin-top:4px;">Config platí po aktivaci 🧠 AI (Rychlé akce). Bez AI se používají jen morning boost cfg.</div>\n'
    '    </div>\n'
    '\n'
    r'\2'
)

# JS: saveHeatingCfg helper + config refresh hook — inject before toggleHeatingAi
JS_HELPER_PATTERN = re.compile(r'(async function toggleHeatingAi\(\) \{)')
JS_HELPER_REPLACEMENT = (
    'async function saveHeatingCfg(varName, val, fallback) {\n'
    '  try {\n'
    '    if (!varMapLoaded) await loadVarMap();\n'
    '    let num = Number(val);\n'
    '    if (!isFinite(num)) num = Number(fallback);\n'
    '    await writeVar(varName, num);\n'
    '    if (ALL_VARS[varName]) ALL_VARS[varName].value = num;\n'
    "    flash('✓ ' + varName.replace('sh_cfg_heating_','') + ' = ' + num);\n"
    "  } catch(e) { flash('✗ ' + e.message); }\n"
    '}\n'
    '\n'
    'const HEAT_CFG_FIELDS = [\n'
    "  ['cfg-h-bath-temp',    'sh_cfg_heating_morning_bath_boost_temp', 23],\n"
    "  ['cfg-h-bath-min',     'sh_cfg_heating_morning_bath_boost_min',  60],\n"
    "  ['cfg-h-wake-wd',      'sh_cfg_heating_wake_weekday_min',        195],\n"
    "  ['cfg-h-wake-we',      'sh_cfg_heating_wake_weekend_min',        315],\n"
    "  ['cfg-h-prewake-win',  'sh_cfg_heating_prewake_window_min',      30],\n"
    "  ['cfg-h-prewake-bath', 'sh_cfg_heating_prewake_bath_delta',      2],\n"
    "  ['cfg-h-prewake-toi',  'sh_cfg_heating_prewake_toilet_delta',    1],\n"
    "  ['cfg-h-occ-age',      'sh_cfg_heating_occupancy_age_max_s',     600],\n"
    "  ['cfg-h-occ-bonus',    'sh_cfg_heating_occupancy_bonus',         0.5]\n"
    '];\n'
    'function refreshHeatingCfgInputs() {\n'
    '  for (const [id, vn, fb] of HEAT_CFG_FIELDS) {\n'
    '    const el = document.getElementById(id);\n'
    '    if (!el || document.activeElement === el) continue;\n'
    '    const v = (ALL_VARS[vn] || {}).value;\n'
    "    el.value = (v === undefined || v === null || v === '') ? fb : Number(v);\n"
    '  }\n'
    '}\n'
    '\n'
    r'\1'
)

# Add refreshHeatingCfgInputs() call in refreshHeating after AI button update
JS_CALL_PATTERN = re.compile(
    r"(aiBtn\.style\.color = aiEnabled \? 'var\(--green\)' : 'var\(--tx3\)';\s*\n\s*\})"
)
JS_CALL_REPLACEMENT = (
    r'\1' + '\n'
    '    // PHASE28: refresh cfg inputs\n'
    '    try { refreshHeatingCfgInputs(); } catch(_) {}\n'
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

    orig_len = len(html)
    new_html, n_html = HTML_PATTERN.subn(HTML_REPLACEMENT, html, count=1)
    new_html, n_helper = JS_HELPER_PATTERN.subn(JS_HELPER_REPLACEMENT, new_html, count=1)
    new_html, n_call = JS_CALL_PATTERN.subn(JS_CALL_REPLACEMENT, new_html, count=1)

    if n_html == 0 or n_helper == 0 or n_call == 0:
        print(f'  X pattern miss: {name} (html={n_html}, helper={n_helper}, call={n_call})')
        return False

    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK patched: {name} ({len(new_html)-orig_len:+d} bytes, html={n_html}, helper={n_helper}, call={n_call})')
    return True


def main():
    print('Phase 28: Heating config section in TOPENI page')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
