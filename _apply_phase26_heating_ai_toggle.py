"""
Phase 26 (2026-04-21) — Heating AI toggle (Fáze C)

Přidá do TOPENÍ page:
  - Tlačítko 🧠 AI: ON/OFF v RYCHLÉ AKCE row (po "Vše OFF")
  - toggleHeatingAi() JS funkce
  - refreshHeating() updatuje label (ON zeleně, OFF šedě)

Ovládá sh_cfg_heating_ai_enabled ('yes' / 'no').

Idempotentní marker PHASE26_HEATING_AI_TOGGLE.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE26_HEATING_AI_TOGGLE'

# 1) HTML: add AI button after "Vše OFF" button
HTML_PATTERN = re.compile(
    r'(<div class="btn" style="border-color:var\(--red\);color:var\(--red\);" onclick="setHeatingMode\(\'off\'\)">⏸ Vše OFF</div>)\s*\n(\s*</div>)'
)
HTML_REPLACEMENT = (
    r'\1' + '\n'
    '      <div class="btn" id="heat-ai-btn" onclick="toggleHeatingAi()" title="Fáze C AI vrstvy — preWakeBoost + weatherAdjust + occupancyBonus">🧠 AI: —</div>\n'
    r'\2'
)

# 2) JS: add toggleHeatingAi() + refresh hook — inject before setHeatingNightAll
JS_FN_PATTERN = re.compile(r'(async function setHeatingNightAll\(\) \{)')
JS_FN_REPLACEMENT = (
    'async function toggleHeatingAi() {\n'
    '  try {\n'
    '    if (!varMapLoaded) await loadVarMap();\n'
    "    const cur = String((ALL_VARS['sh_cfg_heating_ai_enabled'] || {}).value || 'no').toLowerCase();\n"
    "    const nu = cur === 'yes' ? 'no' : 'yes';\n"
    "    await writeVar('sh_cfg_heating_ai_enabled', nu);\n"
    "    if (ALL_VARS['sh_cfg_heating_ai_enabled']) ALL_VARS['sh_cfg_heating_ai_enabled'].value = nu;\n"
    "    flash('🧠 AI vrstvy: ' + nu.toUpperCase());\n"
    '    setTimeout(refreshHeating, 200);\n'
    "  } catch(e) { flash('✗ ' + e.message); }\n"
    '}\n'
    '\n'
    r'\1'
)

# 3) JS: update AI button label inside refreshHeating — inject after heat-kwh update
JS_LABEL_PATTERN = re.compile(
    r"(if \(kwhEl\) kwhEl\.textContent = kwh \+ ' kWh';)"
)
JS_LABEL_REPLACEMENT = (
    r'\1' + '\n'
    "    // PHASE26: AI button label\n"
    "    const aiEnabled = String((ALL_VARS['sh_cfg_heating_ai_enabled'] || {}).value || 'no').toLowerCase() === 'yes';\n"
    "    const aiBtn = document.getElementById('heat-ai-btn');\n"
    "    if (aiBtn) {\n"
    "      aiBtn.textContent = aiEnabled ? '🧠 AI: ON' : '🧠 AI: OFF';\n"
    "      aiBtn.style.borderColor = aiEnabled ? 'var(--green)' : 'var(--tx3)';\n"
    "      aiBtn.style.color = aiEnabled ? 'var(--green)' : 'var(--tx3)';\n"
    "    }\n"
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
    new_html, n_fn   = JS_FN_PATTERN.subn(JS_FN_REPLACEMENT, new_html, count=1)
    new_html, n_lbl  = JS_LABEL_PATTERN.subn(JS_LABEL_REPLACEMENT, new_html, count=1)

    if n_html == 0 or n_fn == 0 or n_lbl == 0:
        print(f'  X pattern miss: {name} (html={n_html}, fn={n_fn}, lbl={n_lbl})')
        return False

    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK patched: {name} ({len(new_html)-orig_len:+d} bytes, html={n_html}, fn={n_fn}, lbl={n_lbl})')
    return True


def main():
    print('Phase 26: Heating AI toggle (Faze C opt-in)')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
