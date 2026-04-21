"""
Phase 15c (2026-04-21) — PM2.5 permanent toggle v Air Purifier detail
Přidá 4. tlačítko "🚫 Vypnout úplně" do ALERTY PM2.5 sekce v zone detail.
Vedle existujících: Ztlumit 15min / Ztlumit 1h / Obnovit.

Funguje jako TOGGLE — podle aktuálního stavu sh_cfg_pm25_alerts_enabled:
  - 'yes' (alerts ON)  → tlačítko ukazuje "🚫 Vypnout úplně"
  - 'no'  (alerts OFF) → tlačítko ukazuje "✅ Zapnout alerty"

Status badge taky aktualizován:
  - 🚫 Alerty VYPNUTY permanentně  (priorita 1, pokud config=no)
  - 🔕 Ztlumeno · zbývá X min        (priorita 2, pokud cooldown aktivní)
  - 🔔 Alerty aktivní                (priorita 3, default)

Idempotentní — check markeru togglePm25AlertsPermanent.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'togglePm25AlertsPermanent'

# ═══════════════════════════════════════════════════════════════════════════
# 1. Insert nového tlačítka mezi "Ztlumit 1 h" a "Obnovit"
# ═══════════════════════════════════════════════════════════════════════════
NEW_BUTTON_HTML = (
    "'<div class=\"btn\" id=\"btn-pm25-permanent\" onclick=\"togglePm25AlertsPermanent()\">🚫 Vypnout úplně</div>' +\n"
    "        "
)

BUTTON_ANCHOR = re.compile(
    r"('<div class=\"btn\" onclick=\"muteAlertPm25\(60\)\">🔕 Ztlumit 1 h</div>' \+\n\s+)"
    r"('<div class=\"btn\" onclick=\"unmuteAlertPm25\(\)\">🔔 Obnovit</div>')"
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. Nová JS funkce togglePm25AlertsPermanent + upravený refreshPurifierAlertStatus
# ═══════════════════════════════════════════════════════════════════════════
NEW_JS_FN = '''

async function togglePm25AlertsPermanent() {
  try {
    if (!varMapLoaded) await loadVarMap();
    const cur = String(
      (ALL_VARS && ALL_VARS['sh_cfg_pm25_alerts_enabled'] && ALL_VARS['sh_cfg_pm25_alerts_enabled'].value) || 'no'
    ).toLowerCase();
    const newVal = (cur === 'yes') ? 'no' : 'yes';
    await writeVar('sh_cfg_pm25_alerts_enabled', newVal);
    // Sync local cache
    try {
      if (ALL_VARS && ALL_VARS['sh_cfg_pm25_alerts_enabled']) {
        ALL_VARS['sh_cfg_pm25_alerts_enabled'].value = newVal;
      }
    } catch(_) {}
    try {
      flash(newVal === 'no' ? '🚫 PM2.5 alerty vypnuty trvale' : '✅ PM2.5 alerty zapnuty');
    } catch(_) {}
    setTimeout(refreshPurifierAlertStatus, 200);
    // Sync Config page toggle pokud existuje
    try {
      const togCfg = document.getElementById('tog-pm25-alerts');
      if (togCfg) togCfg.classList.toggle('on', newVal === 'yes');
    } catch(_) {}
  } catch(e) { try { flash('✗ ' + e.message); } catch(_){} }
}
'''

# Insert nové funkce za funkci unmuteAlertPm25 (před refreshPurifierAlertStatus)
FN_ANCHOR = re.compile(
    r'(async function unmuteAlertPm25\(\) \{[\s\S]*?\n\}\s*\n)'
    r'(\nfunction refreshPurifierAlertStatus\(\))'
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. Rewrite refreshPurifierAlertStatus — permanent check má prioritu 1
# ═══════════════════════════════════════════════════════════════════════════
NEW_REFRESH_FN = '''function refreshPurifierAlertStatus() {
  const el = document.getElementById('purifier-alert-status');
  if (!el) return;
  try {
    // Priorita 1: permanent disable master switch
    const permEnabled = String(
      (ALL_VARS && ALL_VARS['sh_cfg_pm25_alerts_enabled'] && ALL_VARS['sh_cfg_pm25_alerts_enabled'].value) || 'no'
    ).trim().toLowerCase();
    const permOff = (permEnabled !== 'yes');

    // Update toggle button label
    const permBtn = document.getElementById('btn-pm25-permanent');
    if (permBtn) {
      if (permOff) {
        permBtn.innerHTML = '✅ Zapnout alerty';
        permBtn.style.background = 'rgba(46,204,113,0.15)';
        permBtn.style.borderColor = 'rgba(46,204,113,0.4)';
      } else {
        permBtn.innerHTML = '🚫 Vypnout úplně';
        permBtn.style.background = '';
        permBtn.style.borderColor = '';
      }
    }

    if (permOff) {
      el.innerHTML = '🚫 <strong style="color:var(--red);">Alerty VYPNUTY permanentně</strong>' +
        '<div style="font-size:10px;color:var(--tx3);margin-top:3px;">sh_cfg_pm25_alerts_enabled=no · čistička dál běží podle PM2.5</div>';
      return;
    }

    // Priorita 2: cooldown (time-limited mute)
    const raw = String((ALL_VARS && ALL_VARS['sh_context_alert_cooldowns'] && ALL_VARS['sh_context_alert_cooldowns'].value) || '{}');
    let cd = {};
    try { cd = JSON.parse(raw); } catch(_){}
    const untilTs = Number(cd.pm25) || 0;
    const nowTs = Math.floor(Date.now() / 1000);
    if (untilTs > nowTs) {
      const remainMin = Math.ceil((untilTs - nowTs) / 60);
      el.innerHTML = '🔕 <strong style="color:var(--orange);">Ztlumeno</strong> · zbývá ~' + remainMin + ' min';
    } else {
      // Priorita 3: default — alerts active
      el.innerHTML = '🔔 <strong style="color:var(--green);">Alerty aktivní</strong>';
    }
  } catch(e) { el.textContent = 'err: ' + e.message; }
}'''

OLD_REFRESH_FN_PATTERN = re.compile(
    r'function refreshPurifierAlertStatus\(\) \{\s*\n'
    r'  const el = document\.getElementById\(\'purifier-alert-status\'\);\s*\n'
    r'  if \(!el\) return;\s*\n'
    r'  try \{\s*\n'
    r'    const raw = String\(\(ALL_VARS && ALL_VARS\[\'sh_context_alert_cooldowns\'\][\s\S]*?'
    r'\}\s*\n\s*\} catch\(e\) \{ el\.textContent = \'err: \' \+ e\.message; \}\s*\n\}'
)

def patch_file(path):
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {path}')
        return False

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    if MARKER in html:
        print(f'  ✓ already patched: {os.path.basename(path)}')
        return True

    orig_len = len(html)
    changed = False

    # 1. Insert button
    m = BUTTON_ANCHOR.search(html)
    if m:
        html = html[:m.end(1)] + NEW_BUTTON_HTML + m.group(2) + html[m.end():]
        changed = True
    else:
        print(f'  ✗ button anchor not found: {os.path.basename(path)}')
        return False

    # 2. Insert JS function
    m2 = FN_ANCHOR.search(html)
    if m2:
        html = html[:m2.end(1)] + NEW_JS_FN + m2.group(2) + html[m2.end():]
        changed = True
    else:
        print(f'  ✗ fn anchor not found: {os.path.basename(path)}')
        return False

    # 3. Rewrite refreshPurifierAlertStatus (whole function)
    m3 = OLD_REFRESH_FN_PATTERN.search(html)
    if m3:
        html = html[:m3.start()] + NEW_REFRESH_FN + html[m3.end():]
        changed = True
    else:
        print(f'  ✗ refresh fn pattern not found: {os.path.basename(path)}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    delta = len(html) - orig_len
    print(f'  ✓ patched: {os.path.basename(path)} ({delta:+d} bytes)')
    return True

def main():
    print('Phase 15c: PM2.5 permanent toggle in Air Purifier detail')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1

if __name__ == '__main__':
    sys.exit(main())
