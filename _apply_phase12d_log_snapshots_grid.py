"""
PHASE 12d — Log snapshots grid (11 diagnostic log buttons) na AI stránce

Přidá novou sekci "📦 LOG SNAPSHOTS" pod existující "MANUÁLNÍ AKCE",
s 11 tlačítky ke kompletním diagnostickým výstupům (všechny otevřou modal):

  🎓 AI Learning     → sh_ai_learn_last_report (DOPORUČENÍ: Luděk...)
  📅 Denní report    → sh_daily_report (Denní report pro Luďka)
  📆 Týdenní report  → sh_weekly_report (Týdenní report)
  🔬 Debug snapshot  → sh_debug_last_report (SMART HOME DEBUG SNAPSHOT)
  🧠 Last decision   → sh_last_decision
  🔄 Self-heal log   → sh_self_heal_last_action
  ⚠ Anomálie         → sh_anomaly_last
  🩹 AutoFix log     → sh_autofix_last
  🔍 Diag report     → sh_diag_last_report
  🌅 Gemini briefing → sh_gemini_daily_briefing
  📊 Learning stats  → sh_learning_summary

Idempotent. Marker: PHASE12D_LOG_SNAPSHOTS_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# Anchor: insert BEFORE Gemini Diagnostika section
ANCHOR_HTML = "    <div class=\"sect\" style=\"color:var(--purple);\">🤖 GEMINI DIAGNOSTIKA</div>"

INJECT_HTML = """    <!-- PHASE12D_LOG_SNAPSHOTS_APPLIED — 11 diagnostic log buttons -->
    <div class="sect" style="color:var(--purple);">📦 LOG SNAPSHOTS</div>
    <div class="tile-grid g4" style="margin-bottom:6px;">
      <div class="tile" onclick="openLogSnapshot('sh_ai_learn_last_report','🎓 AI Learning report','🎓')" title="sh_ai_learn_last_report — Gemini doporučení z posledního běhu" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🎓</span><div class="t-info"><span class="t-lbl">AI Learning</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_daily_report','📅 Denní report','📅')" title="sh_daily_report — denní Gemini shrnutí" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">📅</span><div class="t-info"><span class="t-lbl">Denní report</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_weekly_report','📆 Týdenní report','📆')" title="sh_weekly_report — týdenní souhrn" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">📆</span><div class="t-info"><span class="t-lbl">Týdenní</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_gemini_daily_briefing','🌅 Dnešní briefing','🌅')" title="sh_gemini_daily_briefing — dnešní ranní briefing" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🌅</span><div class="t-info"><span class="t-lbl">Briefing</span></div></div></div>
    </div>
    <div class="tile-grid g4" style="margin-bottom:6px;">
      <div class="tile" onclick="openLogSnapshot('sh_debug_last_report','🔬 Debug snapshot','🔬')" title="sh_debug_last_report — kompletní dump systému" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🔬</span><div class="t-info"><span class="t-lbl">Debug</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_diag_last_report','🔍 Diag report','🔍')" title="sh_diag_last_report — výstup sh_diagnostic_engine_v1" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🔍</span><div class="t-info"><span class="t-lbl">Diag</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_self_heal_last_action','🔄 Self-heal log','🔄')" title="sh_self_heal_last_action — poslední samooprava" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🔄</span><div class="t-info"><span class="t-lbl">Self-heal</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_autofix_last','🩹 AutoFix log','🩹')" title="sh_autofix_last — poslední automatická oprava" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🩹</span><div class="t-info"><span class="t-lbl">AutoFix</span></div></div></div>
    </div>
    <div class="tile-grid g4" style="margin-bottom:6px;">
      <div class="tile" onclick="openLogSnapshot('sh_anomaly_last','⚠ Poslední anomálie','⚠')" title="sh_anomaly_last — detekovaná neobvyklost" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">⚠</span><div class="t-info"><span class="t-lbl">Anomálie</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_last_decision','🧠 Last decision','🧠')" title="sh_last_decision — poslední rozhodnutí" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🧠</span><div class="t-info"><span class="t-lbl">Decision</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_learning_summary','📊 Learning stats','📊')" title="sh_learning_summary — AI learning metrics" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">📊</span><div class="t-info"><span class="t-lbl">Learning</span></div></div></div>
      <div class="tile" onclick="openLogSnapshot('sh_predict_last_action','🔮 Last prediction','🔮')" title="sh_predict_last_action — poslední predikce" style="min-height:50px;cursor:pointer;"><div class="t-top"><span class="t-icon">🔮</span><div class="t-info"><span class="t-lbl">Predict</span></div></div></div>
    </div>

    """

# JS helper — reuse openAiTileModal pattern but with timestamp lookup
JS_HELPER = """
// PHASE12D_LOG_SNAPSHOTS_APPLIED — generic log snapshot opener
async function openLogSnapshot(varName, title, icon) {
  try {
    if (typeof varMapLoaded !== 'undefined' && !varMapLoaded) {
      openInfoModal(title || 'Načítám…', 'Načítám proměnné z Homey...', { icon: icon || '📦' });
      if (typeof loadVarMap === 'function') await loadVarMap();
    }
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const entry = av && av[varName];
    const val = entry ? entry.value : null;
    if (val == null || String(val).trim() === '' || String(val) === 'idle') {
      openInfoModal(title, '(prázdné — proměnná nemá hodnotu)\\n\\nvar: ' + varName, { icon: icon || '📦', pre: true });
      return;
    }
    const raw = String(val);
    // Look for _ts companion variable for timestamp
    const tsKey = varName + '_ts';
    const tsVal = (av[tsKey] && av[tsKey].value) || '';
    let timeStr = '';
    if (tsVal) {
      const n = Number(tsVal);
      if (!isNaN(n) && n > 1600000000) {
        const d = new Date(n * 1000);
        timeStr = d.toLocaleString('cs-CZ', {timeZone:'Europe/Prague'});
      } else {
        timeStr = String(tsVal);
      }
    }
    // Try JSON pretty-print
    let content;
    let isPre = false;
    try {
      const parsed = JSON.parse(raw);
      content = JSON.stringify(parsed, null, 2);
      isPre = true;
    } catch(_) {
      content = raw;
      if (content.includes('\\n') || content.includes('\\t')) isPre = true;
    }
    const metaHtml = '<div style="font-size:11px;color:var(--tx3);padding-bottom:8px;margin-bottom:10px;border-bottom:1px solid var(--bd);font-family:var(--mono);">' +
      'var: <strong>' + varName + '</strong>' +
      (timeStr ? ' · čas: <strong>' + timeStr + '</strong>' : '') +
      ' · délka: ' + raw.length + ' znaků' +
    '</div>';
    const escaped = content.replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
    const mainHtml = isPre ? '<pre style="font-family:var(--mono);font-size:11px;background:var(--bg2);border-radius:8px;padding:12px;line-height:1.6;white-space:pre-wrap;word-break:break-word;margin:0;">' + escaped + '</pre>'
                           : '<div style="white-space:pre-wrap;word-break:break-word;line-height:1.7;">' + escaped + '</div>';
    openInfoModal(title, metaHtml + mainHtml, { icon: icon || '📦', html: true });
  } catch(e) {
    openInfoModal(title || 'Log snapshot', 'Chyba: ' + e.message, { icon: '⚠' });
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
    marker = 'PHASE12D_LOG_SNAPSHOTS_APPLIED'
    changes = []

    if marker + ' — 11 diagnostic log buttons' in c:
        changes.append('⏭ HTML grid (už applied)')
    elif ANCHOR_HTML in c:
        inj = INJECT_HTML.replace('\n','\r\n') if is_crlf else INJECT_HTML
        c = c.replace(ANCHOR_HTML, inj + ANCHOR_HTML, 1)
        changes.append('+ Log snapshots grid (11 tiles)')
    else:
        changes.append('❌ HTML anchor missing')

    if marker + ' — generic log snapshot opener' in c:
        changes.append('⏭ JS helper (už applied)')
    else:
        idx = c.rfind('</script>')
        if idx >= 0:
            inj = JS_HELPER.replace('\n','\r\n') if is_crlf else JS_HELPER
            c = c[:idx] + inj + c[idx:]
            changes.append('+ JS helper openLogSnapshot')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    for ch in changes:
        print(f'     {ch}')


if __name__ == '__main__':
    print('PHASE 12d — Log snapshots grid (11 tiles)')
    print('='*60)
    for f in FILES:
        patch(f)
