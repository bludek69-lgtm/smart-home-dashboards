"""
PHASE 6c — Tlačítko vypnutí PM2.5 alertu v detailu čističky
Idempotent. Marker: PHASE6C_ALERT_MUTE_APPLIED.

REUSE FIRST:
  Proměnná `sh_context_alert_cooldowns` (JSON) už existuje — obsahuje klíče
  pm25/humidity/temp s unix timestamp do kdy je alert ztlumen.
  sh_kitchen_ai_v1 (a další) respektují tyto cooldowny.

  Dashboard jen nastaví pm25 cooldown na now + N minut.

ADDS:
  1) Helper `muteAlertPm25(minutes)` — parse-update-write sh_context_alert_cooldowns
  2) Helper `unmuteAlertPm25()` — reset pm25 cooldown
  3) Detail overlay panel "Alerty" v purifier bloku s tlačítky:
     - 🔕 Ztlumit 15 min
     - 🔕 Ztlumit 1 h
     - 🔔 Zrušit ztlumení
     + zobrazení aktuálního cooldown stavu (zbývá X min)
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: Add helpers after `async function togglePurifierDevice`
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_JS = """async function togglePurifierDevice(val) {"""

INJECT_JS_BEFORE = """// PHASE6C_ALERT_MUTE_APPLIED — PM2.5 alert mute helpers
async function muteAlertPm25(minutes) {
  try {
    if (!varMapLoaded) await loadVarMap();
    const raw = String((ALL_VARS && ALL_VARS['sh_context_alert_cooldowns'] && ALL_VARS['sh_context_alert_cooldowns'].value) || '{}');
    let cd = {};
    try { cd = JSON.parse(raw); } catch(_){}
    if (typeof cd !== 'object' || cd === null) cd = {};
    cd.pm25 = Math.floor(Date.now() / 1000) + Number(minutes) * 60;
    await writeVar('sh_context_alert_cooldowns', JSON.stringify(cd));
    try { flash('🔕 PM2.5 alert ztlumen na ' + minutes + ' min'); } catch(_){}
    setTimeout(refreshPurifierAlertStatus, 200);
  } catch(e) { try { flash('✗ ' + e.message); } catch(_){} }
}

async function unmuteAlertPm25() {
  try {
    if (!varMapLoaded) await loadVarMap();
    const raw = String((ALL_VARS && ALL_VARS['sh_context_alert_cooldowns'] && ALL_VARS['sh_context_alert_cooldowns'].value) || '{}');
    let cd = {};
    try { cd = JSON.parse(raw); } catch(_){}
    if (typeof cd !== 'object' || cd === null) cd = {};
    cd.pm25 = 0;
    await writeVar('sh_context_alert_cooldowns', JSON.stringify(cd));
    try { flash('🔔 PM2.5 alerty obnoveny'); } catch(_){}
    setTimeout(refreshPurifierAlertStatus, 200);
  } catch(e) { try { flash('✗ ' + e.message); } catch(_){} }
}

function refreshPurifierAlertStatus() {
  const el = document.getElementById('purifier-alert-status');
  if (!el) return;
  try {
    const raw = String((ALL_VARS && ALL_VARS['sh_context_alert_cooldowns'] && ALL_VARS['sh_context_alert_cooldowns'].value) || '{}');
    let cd = {};
    try { cd = JSON.parse(raw); } catch(_){}
    const untilTs = Number(cd.pm25) || 0;
    const nowTs = Math.floor(Date.now() / 1000);
    if (untilTs > nowTs) {
      const remainMin = Math.ceil((untilTs - nowTs) / 60);
      el.innerHTML = '🔕 <strong style="color:var(--orange);">Ztlumeno</strong> · zbývá ~' + remainMin + ' min';
    } else {
      el.innerHTML = '🔔 <strong style="color:var(--green);">Alerty aktivní</strong>';
    }
  } catch(e) { el.textContent = 'err: ' + e.message; }
}

"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: Extend openDeviceDetail purifier block — add "Alerty" card
# Anchor: existing purifier "Automatický režim (PM2.5)" block opening
# ═══════════════════════════════════════════════════════════════════════════
OLD_PURIFIER_DETAIL = """  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Čistička ovládání v detail
  if (d.key === 'purifier') {
    html += '<div class="dd-card">' +
      '<div class="dd-label">Stav čističky (live)</div>' +
      '<div id="purifier-stav" style="font-family:var(--mono);font-size:13px;line-height:1.6;">Načítám…</div>' +
      '<div class="divider"></div>' +
      '<div class="btn" onclick="refreshPurifier()" style="margin-top:6px;">↻ Obnovit</div>' +
    '</div>' +
    '<div class="dd-card">' +
      '<div class="dd-label">Automatický režim (PM2.5)</div>' +
      '<div class="tog-row" style="padding:4px 0;">' +
        '<span class="card-icon">🫁</span>' +
        '<span class="tog-lbl" title="sh_air_purifier_guard_enabled — při OFF čistička běží jen podle tlačítka ZAP/VYP">Hlídání PM2.5 (sh_air_purifier_router_v1)</span>' +
        '<div class="toggle" id="tog-purifier-kitchen" onclick="togglePurifierGuard(this)"></div>' +
      '</div>' +
      '<div style="font-size:10px;color:var(--tx3);margin-top:6px;line-height:1.5;">' +
        'ON = router řídí dle PM2.5. OFF = jen manuální ovládání.' +
      '</div>' +
    '</div>';
    setTimeout(function() {
      refreshPurifier();
      try {
        const v = String((ALL_VARS||{})['sh_air_purifier_guard_enabled']?.value || 'yes').trim().toLowerCase();
        const t = document.getElementById('tog-purifier-kitchen');
        if (t) t.classList.toggle('on', v === 'yes' || v === 'true' || v === 'on');
      } catch(_){}
    }, 80);
  }"""

NEW_PURIFIER_DETAIL = """  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Čistička ovládání v detail
  // PHASE6C_ALERT_MUTE_APPLIED — + panel Alerty s ztlumením PM2.5
  if (d.key === 'purifier') {
    html += '<div class="dd-card">' +
      '<div class="dd-label">Stav čističky (live)</div>' +
      '<div id="purifier-stav" style="font-family:var(--mono);font-size:13px;line-height:1.6;">Načítám…</div>' +
      '<div class="divider"></div>' +
      '<div class="btn" onclick="refreshPurifier()" style="margin-top:6px;">↻ Obnovit</div>' +
    '</div>' +
    '<div class="dd-card">' +
      '<div class="dd-label">Automatický režim (PM2.5)</div>' +
      '<div class="tog-row" style="padding:4px 0;">' +
        '<span class="card-icon">🫁</span>' +
        '<span class="tog-lbl" title="sh_air_purifier_guard_enabled — při OFF čistička běží jen podle tlačítka ZAP/VYP">Hlídání PM2.5 (sh_air_purifier_router_v1)</span>' +
        '<div class="toggle" id="tog-purifier-kitchen" onclick="togglePurifierGuard(this)"></div>' +
      '</div>' +
      '<div style="font-size:10px;color:var(--tx3);margin-top:6px;line-height:1.5;">' +
        'ON = router řídí dle PM2.5. OFF = jen manuální ovládání.' +
      '</div>' +
    '</div>' +
    '<div class="dd-card">' +
      '<div class="dd-label">Alerty PM2.5</div>' +
      '<div id="purifier-alert-status" style="font-family:var(--mono);font-size:13px;padding:6px 0;">—</div>' +
      '<div class="divider"></div>' +
      '<div class="btn-row">' +
        '<div class="btn" onclick="muteAlertPm25(15)">🔕 Ztlumit 15 min</div>' +
        '<div class="btn" onclick="muteAlertPm25(60)">🔕 Ztlumit 1 h</div>' +
        '<div class="btn" onclick="unmuteAlertPm25()">🔔 Obnovit</div>' +
      '</div>' +
      '<div style="font-size:10px;color:var(--tx3);margin-top:8px;line-height:1.5;">' +
        'Ztlumení zapíše <code>pm25</code> klíč do <code>sh_context_alert_cooldowns</code> (unix ts do kdy nealertovat). Respektuje sh_kitchen_ai_v1 a další.' +
      '</div>' +
    '</div>';
    setTimeout(function() {
      refreshPurifier();
      refreshPurifierAlertStatus();
      try {
        const v = String((ALL_VARS||{})['sh_air_purifier_guard_enabled']?.value || 'yes').trim().toLowerCase();
        const t = document.getElementById('tog-purifier-kitchen');
        if (t) t.classList.toggle('on', v === 'yes' || v === 'true' || v === 'on');
      } catch(_){}
    }, 80);
  }"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    orig = content
    changes = []
    is_crlf = '\r\n' in content[:4096]

    # 1. JS helpers (insert before togglePurifierDevice)
    if 'PHASE6C_ALERT_MUTE_APPLIED — PM2.5 alert mute' in content:
        changes.append('⏭ JS helpers (už applied)')
    else:
        anchor = ANCHOR_JS.replace('\n', '\r\n') if is_crlf else ANCHOR_JS
        inj = INJECT_JS_BEFORE.replace('\n', '\r\n') if is_crlf else INJECT_JS_BEFORE
        if anchor in content:
            content = content.replace(anchor, inj + anchor, 1)
            changes.append('+ JS helpers (muteAlertPm25, unmuteAlertPm25, refreshPurifierAlertStatus)')
        else:
            changes.append('❌ JS anchor nenalezen')

    # 2. Extend purifier detail block
    if 'PHASE6C_ALERT_MUTE_APPLIED — + panel Alerty' in content:
        changes.append('⏭ Detail purifier (už applied)')
    else:
        old2 = OLD_PURIFIER_DETAIL.replace('\n', '\r\n') if is_crlf else OLD_PURIFIER_DETAIL
        new2 = NEW_PURIFIER_DETAIL.replace('\n', '\r\n') if is_crlf else NEW_PURIFIER_DETAIL
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ Detail purifier panel Alerty')
        else:
            changes.append('❌ Detail anchor nenalezen')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 6c — Čistička + tlačítko vypnutí PM2.5 alertu')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
