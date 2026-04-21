"""
PHASE 12b — Gemini Diagnostika → unified generic modal

CONTEXT:
  Existing "📋 Celý report" button volal `showDiagReport()` která NEEXISTUJE
  (dead code). Custom overlay `diagReportOverlay` není nikdy zobrazen.
  3 text rows (geminiDiagText, Fix, SystemInsight) nejsou clickable.

FIX:
  A) Kompletně nahradit custom overlay generic InfoModal
  B) Každý z 3 textových řádků clickable → modal s kompletní hodnotou
  C) "📋 Celý report" → openGeminiReport() (full Sheets API fetch)
  D) Remove dead code (showDiagReport stub + diagReportOverlay div)

Idempotent. Marker: PHASE12B_GEMINI_DIAG_MODAL_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: Replace card HTML — clickable rows + onclick on whole card
# ═══════════════════════════════════════════════════════════════════════════
OLD_CARD = """    <div class="sect" style="color:var(--purple);">🤖 GEMINI DIAGNOSTIKA</div>
    <div class="card" id="geminiDiagCard">
      <div class="card-row">
        <span class="card-icon" id="geminiDiagIcon">🔍</span>
        <span class="card-lbl" style="font-weight:600;" id="geminiDiagText">—</span>
        <span class="card-val" id="geminiDiagPrio" style="font-family:var(--mono);font-size:10px;">—</span>
      </div>
      <div class="divider"></div>
      <div class="card-row">
        <span class="card-icon">🔧</span>
        <span class="card-lbl card-sub" id="geminiDiagFix" style="font-size:11px;color:var(--tx2);">—</span>
      </div>
      <div class="divider"></div>
      <div class="card-row">
        <span class="card-icon">📊</span>
        <span class="card-lbl card-sub" id="systemInsightText" style="font-size:11px;color:var(--tx2);">—</span>
      </div>
      <div style="display:flex;gap:6px;margin-top:8px;">
        <div class="btn" style="flex:1;text-align:center;border-color:var(--purple);color:var(--purple);" onclick="runScript('sh_gemini_diagnostic_v1')">▶ Spustit analýzu</div>
        <div class="btn" style="flex:1;text-align:center;" onclick="showDiagReport()">📋 Celý report</div>
      </div>
    </div>
    <div id="diagReportOverlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:500;overflow-y:auto;padding:48px 12px 12px;">
      <div style="background:var(--bg1);border:1px solid var(--purple);border-radius:var(--r2);padding:16px;max-width:600px;margin:10px auto;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-weight:700;color:var(--purple);">🤖 Gemini Diagnostic Report</span>
          <div class="btn" onclick="document.getElementById('diagReportOverlay').style.display='none'">✕ Zavřít</div>
        </div>
        <pre id="diagReportText" style="font-family:var(--mono);font-size:11px;color:var(--tx1);white-space:pre-wrap;line-height:1.6;">—</pre>
        <div style="margin-top:10px;font-size:10px;color:var(--tx3);" id="diagReportTs">—</div>
      </div>
    </div>"""

NEW_CARD = """    <div class="sect" style="color:var(--purple);">🤖 GEMINI DIAGNOSTIKA</div>
    <!-- PHASE12B_GEMINI_DIAG_MODAL_APPLIED — clickable rows + generic modal -->
    <div class="card" id="geminiDiagCard">
      <div class="card-row" onclick="openGeminiDiagModal('text')" style="cursor:pointer;" title="Klikni pro celý popis problému">
        <span class="card-icon" id="geminiDiagIcon">🔍</span>
        <span class="card-lbl" style="font-weight:600;" id="geminiDiagText">—</span>
        <span class="card-val" id="geminiDiagPrio" style="font-family:var(--mono);font-size:10px;">—</span>
      </div>
      <div class="divider"></div>
      <div class="card-row" onclick="openGeminiDiagModal('fix')" style="cursor:pointer;" title="Klikni pro celý návrh řešení">
        <span class="card-icon">🔧</span>
        <span class="card-lbl card-sub" id="geminiDiagFix" style="font-size:11px;color:var(--tx2);">—</span>
      </div>
      <div class="divider"></div>
      <div class="card-row" onclick="openGeminiDiagModal('insight')" style="cursor:pointer;" title="Klikni pro celý system insight">
        <span class="card-icon">📊</span>
        <span class="card-lbl card-sub" id="systemInsightText" style="font-size:11px;color:var(--tx2);">—</span>
      </div>
      <div style="display:flex;gap:6px;margin-top:8px;">
        <div class="btn" style="flex:1;text-align:center;border-color:var(--purple);color:var(--purple);" onclick="runScript('sh_gemini_diagnostic_v1')" title="Spustí sh_gemini_diagnostic_v1 skript">▶ Spustit analýzu</div>
        <div class="btn" style="flex:1;text-align:center;" onclick="openGeminiDiagFullReport()" title="Zobrazí celý snapshot diagnostiky v popupu">📋 Celý report</div>
      </div>
    </div>"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH B: Add JS helpers — openGeminiDiagModal + openGeminiDiagFullReport
# Insert before </script>
# ═══════════════════════════════════════════════════════════════════════════
MODAL_HELPERS = """
// PHASE12B_GEMINI_DIAG_MODAL_APPLIED — Gemini Diag modal helpers
function openGeminiDiagModal(kind) {
  try {
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const get = k => (av[k] && av[k].value) || '(prázdné)';
    let title, varName, icon;
    if (kind === 'fix') {
      title = '🔧 Gemini Diagnostika — návrh řešení';
      varName = 'sh_gemini_diag_fix';
      icon = '🔧';
    } else if (kind === 'insight') {
      title = '📊 Gemini — System Insight';
      varName = 'sh_system_insight_text';
      icon = '📊';
    } else {
      title = '🔍 Gemini Diagnostika — problém';
      varName = 'sh_gemini_diag_text';
      icon = '🔍';
    }
    const raw = String(get(varName));
    const prio = String(get('sh_gemini_diag_priority') || '').toUpperCase();
    const state = String(get('sh_gemini_diag_state') || '');
    let metaHtml = '<div style="font-size:11px;color:var(--tx3);padding-bottom:8px;margin-bottom:8px;border-bottom:1px solid var(--bd);font-family:var(--mono);">';
    metaHtml += 'var: <strong>' + varName + '</strong>';
    if (kind === 'text') {
      metaHtml += ' · prio: <strong style="color:' + (prio === 'HIGH' ? 'var(--red)' : prio === 'MEDIUM' ? 'var(--orange)' : 'var(--green)') + ';">' + prio + '</strong>';
      metaHtml += ' · state: <strong>' + state + '</strong>';
    }
    metaHtml += '</div>';
    const escaped = raw.replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
    const mainHtml = '<div style="white-space:pre-wrap;word-break:break-word;line-height:1.6;">' + escaped + '</div>';
    openInfoModal(title, metaHtml + mainHtml, { icon: icon, html: true });
  } catch(e) {
    openInfoModal('Gemini Diag', 'Chyba: ' + e.message, { icon: '⚠' });
  }
}

function openGeminiDiagFullReport() {
  try {
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const get = k => (av[k] && av[k].value) || '—';
    const text = get('sh_gemini_diag_text');
    const fix = get('sh_gemini_diag_fix');
    const state = String(get('sh_gemini_diag_state'));
    const prio = String(get('sh_gemini_diag_priority'));
    const insight = get('sh_system_insight_text');
    const analysisTs = get('sh_diag_last_analysis_ts');
    const analysisRes = get('sh_diag_analysis_result');
    const diagLastReport = get('sh_diag_last_report');

    let html = '<div style="display:grid;grid-template-columns:auto 1fr;gap:8px 14px;font-size:12px;margin-bottom:14px;">';
    const statusColor = state === 'critical' ? 'var(--red)' : state === 'warn' ? 'var(--orange)' : 'var(--green)';
    html += '<div style="color:var(--tx3);font-family:var(--mono);">state</div><div style="color:' + statusColor + ';font-weight:600;">' + state + '</div>';
    html += '<div style="color:var(--tx3);font-family:var(--mono);">priority</div><div style="color:' + statusColor + ';">' + prio + '</div>';
    html += '<div style="color:var(--tx3);font-family:var(--mono);">last analysis</div><div style="font-family:var(--mono);font-size:11px;">' + analysisTs + '</div>';
    html += '</div>';

    const section = (icon, title, content) => {
      const esc = String(content).replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
      return '<div style="margin-bottom:14px;padding:10px 12px;background:rgba(255,255,255,.03);border-radius:8px;">' +
        '<div style="font-size:11px;color:var(--purple);font-weight:600;margin-bottom:6px;">' + icon + ' ' + title + '</div>' +
        '<div style="font-size:12px;line-height:1.6;white-space:pre-wrap;word-break:break-word;">' + esc + '</div>' +
      '</div>';
    };

    html += section('🔍', 'Problém', text);
    html += section('🔧', 'Navržené řešení', fix);
    html += section('📊', 'System Insight', insight);

    // Diagnostic analysis (JSON if available)
    if (analysisRes && analysisRes !== '—' && analysisRes.length > 5) {
      try {
        const parsed = JSON.parse(analysisRes);
        html += '<div style="margin-bottom:14px;padding:10px 12px;background:rgba(255,255,255,.03);border-radius:8px;">';
        html += '<div style="font-size:11px;color:var(--purple);font-weight:600;margin-bottom:6px;">🔬 Analysis result (sh_diag_analysis_result)</div>';
        html += '<pre style="font-family:var(--mono);font-size:10px;line-height:1.5;white-space:pre-wrap;word-break:break-word;margin:0;">' +
          JSON.stringify(parsed, null, 2).replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])) + '</pre>';
        html += '</div>';
      } catch(_) {
        html += section('🔬', 'Analysis (raw)', analysisRes);
      }
    }

    if (diagLastReport && diagLastReport !== '—' && diagLastReport.length > 5) {
      html += section('📋', 'Last diagnostic report (sh_diag_last_report)', diagLastReport);
    }

    openInfoModal('🤖 Gemini Diagnostic — kompletní report', html, { icon: '🤖', html: true });
  } catch(e) {
    openInfoModal('Gemini Diag', 'Chyba: ' + e.message, { icon: '⚠' });
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
    marker = 'PHASE12B_GEMINI_DIAG_MODAL_APPLIED'

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

    do(OLD_CARD, NEW_CARD, 'Gemini Diag card HTML (clickable rows + dead overlay removed)')

    # Inject JS helpers
    if marker + ' — Gemini Diag modal helpers' in c:
        changes.append('⏭ JS helpers (už applied)')
    else:
        idx = c.rfind('</script>')
        if idx >= 0:
            inj = MODAL_HELPERS.replace('\n','\r\n') if is_crlf else MODAL_HELPERS
            c = c[:idx] + inj + c[idx:]
            changes.append('+ JS helpers (openGeminiDiagModal + openGeminiDiagFullReport)')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    for ch in changes:
        print(f'     {ch}')


if __name__ == '__main__':
    print('PHASE 12b — Gemini Diagnostika modal')
    print('='*60)
    for f in FILES:
        patch(f)
