"""
PHASE 12a — Event Log rows + Morning Tune card → modal popup

CHANGES:
  A) Event Log rows — klik na řádek → modal s kompletní JSON detail eventu
     (všechna pole: timestamp, script, event, trigger, zone, params, result, error,
      phase, presence, sleep, scene, lux, temp, power_w, context)
  B) Morning Tune card — ořízni na 200 znaků s "…" + klik na celou kartu → modal
     s plným `sh_morning_tune_recommendation`

BONUS INSPIRATION (přidáno):
  - Error events highlighted červeně v modalu
  - Pretty timestamp format
  - "Otevřít event v dalším modalu" chain pro navigaci mezi events

Idempotent. Marker: PHASE12A_EVENTLOG_TUNE_MODAL_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: Event Log rows — store rows + onclick
# ═══════════════════════════════════════════════════════════════════════════
OLD_EVENTLOG = """    if (rows.length > 0) {
      document.getElementById('eventlog-recent').style.display = 'block';
      let rhtml = '';
      rows.slice(0, 20).forEach(function(r) {
        const ts = String(r.timestamp || '').substring(11, 19);
        const scr = String(r.script || '').replace('sh_','').replace('_v1','').replace('_v2','');
        const ev = r.event || '';
        const err = r.error || '';
        const color = err ? 'var(--red)' : 'var(--tx2)';
        rhtml += '<div style="display:flex;gap:6px;padding:2px 0;border-bottom:1px solid rgba(255,255,255,.05);color:' + color + ';">';
        rhtml += '<span style="color:var(--tx3);flex-shrink:0;">' + ts + '</span>';
        rhtml += '<span style="color:var(--cyan);flex-shrink:0;min-width:100px;">' + scr + '</span>';
        rhtml += '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + ev + '</span>';
        if (err) rhtml += '<span style="color:var(--red);flex-shrink:0;">⚠</span>';
        rhtml += '</div>';
      });
      el('el-rows').innerHTML = rhtml;
    }"""

NEW_EVENTLOG = """    // PHASE12A_EVENTLOG_TUNE_MODAL_APPLIED — clickable rows + store data
    if (rows.length > 0) {
      document.getElementById('eventlog-recent').style.display = 'block';
      window._eventLogRows = rows;  // store for modal lookup
      let rhtml = '';
      rows.slice(0, 20).forEach(function(r, idx) {
        const ts = String(r.timestamp || '').substring(11, 19);
        const scr = String(r.script || '').replace('sh_','').replace('_v1','').replace('_v2','');
        const ev = r.event || '';
        const err = r.error || '';
        const color = err ? 'var(--red)' : 'var(--tx2)';
        const tipRaw = scr + ' · ' + ev + (err ? ' · ' + err : '') + ' · klikni pro detail';
        const tip = tipRaw.replace(/"/g,'&quot;');
        rhtml += '<div style="display:flex;gap:6px;padding:2px 0;border-bottom:1px solid rgba(255,255,255,.05);color:' + color + ';cursor:pointer;" onclick="openEventLogRowModal(' + idx + ')" title="' + tip + '">';
        rhtml += '<span style="color:var(--tx3);flex-shrink:0;">' + ts + '</span>';
        rhtml += '<span style="color:var(--cyan);flex-shrink:0;min-width:100px;">' + scr + '</span>';
        rhtml += '<span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + ev + '</span>';
        if (err) rhtml += '<span style="color:var(--red);flex-shrink:0;">⚠</span>';
        rhtml += '</div>';
      });
      el('el-rows').innerHTML = rhtml;
    }"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH B: Morning Tune — clickable + truncate
# ═══════════════════════════════════════════════════════════════════════════
OLD_MORNING = """async function loadMorningTune() {
  const el = document.getElementById('morningTuneCard');
  if (!el) return;
  try {
    if (!varMapLoaded) await loadVarMap();
    const rec = String(_getVar('sh_morning_tune_recommendation')||'');
    const wa = Number(_getVar('sh_habit_wake_avg')||0);
    const sa = Number(_getVar('sh_habit_sleep_avg')||0);
    const ka = Number(_getVar('sh_habit_kitchen_avg')||0);
    const fmt = h => { if (!h) return '—'; const hr=Math.floor(h); const m=Math.round((h-hr)*60); return hr+':'+String(m).padStart(2,'0'); };
    let html = '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:10px;margin-bottom:6px;">';
    html += '<div>🌅 '+fmt(wa)+'</div><div>😴 '+fmt(sa)+'</div><div>☕ '+fmt(ka)+'</div></div>';
    if (rec && rec.length>5) {
      html += '<div style="padding:6px;background:rgba(176,133,255,.08);border:1px solid rgba(176,133,255,.3);border-radius:4px;font-size:10px;line-height:1.4;">'+rec+'</div>';
    } else {
      html += '<div style="color:var(--tx3);font-size:10px;text-align:center;padding:8px 0;">Klikni 🧠 Gemini</div>';
    }
    el.innerHTML = html;
  } catch(e) { el.innerHTML = '<div style="color:var(--red);">'+e.message+'</div>'; }
}"""

NEW_MORNING = """// PHASE12A_EVENTLOG_TUNE_MODAL_APPLIED — klik → modal s celým textem
async function loadMorningTune() {
  const el = document.getElementById('morningTuneCard');
  if (!el) return;
  try {
    if (!varMapLoaded) await loadVarMap();
    const rec = String(_getVar('sh_morning_tune_recommendation')||'');
    const wa = Number(_getVar('sh_habit_wake_avg')||0);
    const sa = Number(_getVar('sh_habit_sleep_avg')||0);
    const ka = Number(_getVar('sh_habit_kitchen_avg')||0);
    const fmt = h => { if (!h) return '—'; const hr=Math.floor(h); const m=Math.round((h-hr)*60); return hr+':'+String(m).padStart(2,'0'); };
    let html = '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:10px;margin-bottom:6px;">';
    html += '<div>🌅 '+fmt(wa)+'</div><div>😴 '+fmt(sa)+'</div><div>☕ '+fmt(ka)+'</div></div>';
    if (rec && rec.length>5) {
      const trunc = rec.length > 200 ? rec.substring(0, 200).replace(/\\s+\\S*$/, '') + '…' : rec;
      const isTrunc = rec.length > 200;
      html += '<div onclick="openMorningTuneModal()" style="padding:6px;background:rgba(176,133,255,.08);border:1px solid rgba(176,133,255,.3);border-radius:4px;font-size:10px;line-height:1.4;cursor:pointer;" title="Klikni pro celý text (' + rec.length + ' znaků)">';
      html += trunc;
      if (isTrunc) html += ' <span style="color:var(--purple);font-weight:600;">📖 celý…</span>';
      html += '</div>';
    } else {
      html += '<div style="color:var(--tx3);font-size:10px;text-align:center;padding:8px 0;">Klikni 🧠 Gemini</div>';
    }
    el.innerHTML = html;
  } catch(e) { el.innerHTML = '<div style="color:var(--red);">'+e.message+'</div>'; }
}"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH C: Add modal helpers (openEventLogRowModal + openMorningTuneModal)
# Insert before </script> in body
# ═══════════════════════════════════════════════════════════════════════════
MODAL_HELPERS = """
// PHASE12A_EVENTLOG_TUNE_MODAL_APPLIED — event log row + morning tune modal helpers
function openEventLogRowModal(idx) {
  const rows = window._eventLogRows || [];
  const r = rows[idx];
  if (!r) { openInfoModal('Event', 'Řádek nenalezen', {icon:'⚠'}); return; }
  // Format all fields nicely
  let html = '<div style="display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:12px;">';
  const fields = ['timestamp','script','event','trigger','zone','result','error','phase','presence','sleep','scene','lux','temp','power_w','context','params'];
  fields.forEach(function(k){
    if (r[k] !== undefined && r[k] !== null && r[k] !== '') {
      let v = r[k];
      if (typeof v === 'object') v = JSON.stringify(v, null, 2);
      const escaped = String(v).replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
      const color = (k === 'error') ? 'var(--red)' : (k === 'result' ? 'var(--green)' : 'var(--tx1)');
      const isJson = (k === 'params' || k === 'context') && String(v).length > 40;
      html += '<div style="color:var(--tx3);font-family:var(--mono);">' + k + '</div>';
      html += '<div style="color:' + color + ';' + (isJson ? 'font-family:var(--mono);font-size:11px;white-space:pre-wrap;word-break:break-word;' : 'word-break:break-word;') + '">' + escaped + '</div>';
    }
  });
  html += '</div>';
  // Navigation buttons (prev/next event)
  const nav = '<div style="display:flex;gap:8px;margin-top:14px;padding-top:10px;border-top:1px solid var(--bd);">' +
    (idx > 0 ? '<div class="btn" onclick="openEventLogRowModal(' + (idx-1) + ')" style="flex:1;text-align:center;">⬅ Předchozí</div>' : '<div style="flex:1;"></div>') +
    '<div style="flex-shrink:0;font-size:10px;color:var(--tx3);align-self:center;padding:0 8px;">' + (idx+1) + ' / ' + rows.length + '</div>' +
    (idx < rows.length - 1 ? '<div class="btn" onclick="openEventLogRowModal(' + (idx+1) + ')" style="flex:1;text-align:center;">Další ➡</div>' : '<div style="flex:1;"></div>') +
  '</div>';
  const icon = r.error ? '⚠' : '📋';
  const title = (r.script || 'Event') + ' · ' + (r.event || '—');
  openInfoModal(title, html + nav, { icon: icon, html: true });
}

function openMorningTuneModal() {
  try {
    const rec = String((typeof _getVar === 'function' ? _getVar('sh_morning_tune_recommendation') : '') || '');
    if (!rec || rec.length < 5) {
      openInfoModal('📊 Morning Tune', 'Žádné doporučení. Klikni 🧠 Gemini pro vygenerování.', {icon:'📊'});
      return;
    }
    openInfoModal('📊 Morning Tune — doporučení Gemini', rec, { icon: '📊', pre: true });
  } catch(e) {
    openInfoModal('📊 Morning Tune', 'Chyba: ' + e.message, {icon:'⚠'});
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
    changes = []
    marker = 'PHASE12A_EVENTLOG_TUNE_MODAL_APPLIED'

    def do(old, new, label):
        nonlocal c
        old2 = old.replace('\n','\r\n') if is_crlf else old
        new2 = new.replace('\n','\r\n') if is_crlf else new
        if old2 in c:
            c = c.replace(old2, new2, 1)
            changes.append('+ ' + label)
        elif marker in c:
            changes.append('⏭ ' + label + ' (už applied)')
        else:
            changes.append('⏭ ' + label + ' (anchor missing)')

    do(OLD_EVENTLOG, NEW_EVENTLOG, 'Event Log rows clickable')
    do(OLD_MORNING, NEW_MORNING, 'Morning Tune card clickable + truncate')

    # Inject helpers before </script></body>
    if marker + ' — event log row + morning tune modal' in c:
        changes.append('⏭ Modal helpers (už applied)')
    else:
        anchor = '</script>\n</body>'
        if is_crlf: anchor = '</script>\r\n</body>'
        if anchor in c:
            inj = MODAL_HELPERS.replace('\n','\r\n') if is_crlf else MODAL_HELPERS
            c = c.replace(anchor, inj + anchor, 1)
            changes.append('+ Modal helpers (openEventLogRowModal + openMorningTuneModal)')
        else:
            # Fallback: before last </script>
            idx = c.rfind('</script>')
            if idx >= 0:
                inj = MODAL_HELPERS.replace('\n','\r\n') if is_crlf else MODAL_HELPERS
                c = c[:idx] + inj + c[idx:]
                changes.append('+ Modal helpers (fallback placement)')
            else:
                changes.append('❌ </script> not found')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    for ch in changes:
        print(f'     {ch}')


if __name__ == '__main__':
    print('PHASE 12a — Event Log + Morning Tune modal')
    print('='*60)
    for f in FILES:
        patch(f)
