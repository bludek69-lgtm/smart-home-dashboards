"""
PHASE 13 — Config stránka: ukládání parametrů

BUG:
  #page-settings.active má `overflow: hidden !important` → Save button
  ("💾 Uložit všechny změny") je pod viewportem a nejde ke němu scrollovat.
  User změní input hodnotu, ale nemůže ji uložit.

FIX:
  A) overflow: hidden → overflow-y: auto (allow scroll on config page)
  B) BONUS: auto-save on blur/change — uloží hned bez klik na save button
     (lepší UX — user nemusí hledat save button)
  C) Save button → sticky bottom (vždy viditelný při scroll)
  D) Visual feedback: input dostane zelený border po úspěšném save

Idempotent. Marker: PHASE13_CONFIG_SAVE_FIX_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: Change overflow:hidden to overflow-y:auto on #page-settings
# ═══════════════════════════════════════════════════════════════════════════
OLD_CSS = "#page-settings.active{display:flex !important;flex-direction:column;overflow:hidden !important;}"
NEW_CSS = """#page-settings.active{display:flex !important;flex-direction:column;overflow-y:auto !important;overflow-x:hidden;scrollbar-width:thin;scrollbar-color:var(--bg4) transparent;}
/* PHASE13_CONFIG_SAVE_FIX_APPLIED — sticky save bar at bottom */
#page-settings .cfg-bottom{position:sticky;bottom:0;background:linear-gradient(180deg,transparent 0%,var(--bg1) 20%,var(--bg1) 100%);padding-top:10px;z-index:10;}
#page-settings .cfg-row input.cfg-saved{border-color:var(--green) !important;box-shadow:0 0 8px rgba(94,232,160,.25);transition:border-color .3s;}"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH B: Add onblur auto-save to cfg inputs
# ═══════════════════════════════════════════════════════════════════════════
OLD_INPUT = """        '<input type="' + iType + '" id="cfg_' + v.name + '" value="' + cur + '" step="' + step + '"' +
        ' oninput="validateCfgInput(\\'' + v.name + '\\',\\'cfg\\')"' +
        ' onchange="validateCfgInput(\\'' + v.name + '\\',\\'cfg\\')">' +"""

NEW_INPUT = """        '<input type="' + iType + '" id="cfg_' + v.name + '" value="' + cur + '" step="' + step + '"' +
        ' data-vartype="' + (v.type||'number') + '"' +
        ' oninput="validateCfgInput(\\'' + v.name + '\\',\\'cfg\\')"' +
        ' onchange="validateCfgInput(\\'' + v.name + '\\',\\'cfg\\')"' +
        ' onblur="autoSaveCfg(\\'' + v.name + '\\', this)">' +"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH C: Add autoSaveCfg JS helper
# ═══════════════════════════════════════════════════════════════════════════
JS_HELPER = """
// PHASE13_CONFIG_SAVE_FIX_APPLIED — auto-save on blur
async function autoSaveCfg(varName, inputEl) {
  try {
    if (!varName || !inputEl) return;
    if (!validateCfgInput(varName, 'cfg')) return;  // skip if invalid
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const curStored = av[varName] && av[varName].value;
    const varType = inputEl.getAttribute('data-vartype') || 'number';
    const newVal = varType === 'text' ? inputEl.value.trim() : Number(inputEl.value);
    if (String(newVal) === String(curStored == null ? '' : curStored)) return; // no change
    inputEl.classList.remove('cfg-saved');
    const ok = await writeVar(varName, newVal);
    if (ok) {
      inputEl.classList.add('cfg-saved');
      try { flash('✓ ' + varName + ' = ' + newVal); } catch(_){}
      setTimeout(() => inputEl.classList.remove('cfg-saved'), 2500);
    } else {
      try { flash('✗ Nepodařilo se uložit ' + varName); } catch(_){}
    }
  } catch(e) {
    try { flash('✗ ' + e.message); } catch(_){}
  }
}
"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    orig = c
    is_crlf = '\r\n' in c[:4096]
    marker = 'PHASE13_CONFIG_SAVE_FIX_APPLIED'
    changes = []

    def do(old, new, label):
        nonlocal c
        old2 = old.replace('\n','\r\n') if is_crlf else old
        new2 = new.replace('\n','\r\n') if is_crlf else new
        if old2 in c:
            c = c.replace(old2, new2, 1)
            changes.append('+ ' + label)
        elif marker in c and label.startswith('CSS'):
            changes.append('⏭ ' + label + ' (už applied)')
        else:
            changes.append('⏭ ' + label + ' (anchor missing)')

    do(OLD_CSS, NEW_CSS, 'CSS: overflow:auto + sticky save bar + saved border')
    do(OLD_INPUT, NEW_INPUT, 'Input onblur handler (autoSaveCfg)')

    if marker + ' — auto-save on blur' in c:
        changes.append('⏭ JS helper (už applied)')
    else:
        idx = c.rfind('</script>')
        if idx >= 0:
            inj = JS_HELPER.replace('\n','\r\n') if is_crlf else JS_HELPER
            c = c[:idx] + inj + c[idx:]
            changes.append('+ JS helper autoSaveCfg')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    for ch in changes:
        print(f'     {ch}')


if __name__ == '__main__':
    print('PHASE 13 — Config save fix (scroll + auto-save on blur)')
    print('='*60)
    for f in FILES:
        patch(f)
