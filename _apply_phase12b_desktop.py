"""Desktop varianta patche pro Gemini Diag card."""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD = """    <div class="sect" style="color:var(--purple);">🤖 GEMINI DIAGNOSTIKA</div>
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
    <div id="diagReportOverlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:500;overflow-y:auto;padding:58px 16px 16px;">
      <div style="background:var(--bg1);border:1px solid var(--purple);border-radius:var(--r2);padding:16px;max-width:600px;margin:10px auto;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
          <span style="font-weight:700;color:var(--purple);">🤖 Gemini Diagnostic Report</span>
          <div class="btn" onclick="document.getElementById('diagReportOverlay').style.display='none'">✕ Zavřít</div>
        </div>
        <pre id="diagReportText" style="font-family:var(--mono);font-size:11px;color:var(--tx1);white-space:pre-wrap;line-height:1.6;">—</pre>
        <div style="margin-top:10px;font-size:10px;color:var(--tx3);" id="diagReportTs">—</div>
      </div>
    </div>"""

NEW = """    <div class="sect" style="color:var(--purple);">🤖 GEMINI DIAGNOSTIKA</div>
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
        <div class="btn" style="flex:1;text-align:center;" onclick="openGeminiDiagFullReport()" title="Zobrazí celý snapshot v popupu">📋 Celý report</div>
      </div>
    </div>"""

for fp in FILES:
    if not os.path.exists(fp): continue
    with open(fp, 'r', encoding='utf-8', newline='') as f: c = f.read()
    is_crlf = '\r\n' in c[:4096]
    o = OLD.replace('\n','\r\n') if is_crlf else OLD
    n = NEW.replace('\n','\r\n') if is_crlf else NEW
    # Check specifically if CARD was patched (not just JS helpers)
    if 'openGeminiDiagFullReport()"' in c and 'onclick="openGeminiDiagModal' in c:
        print(f'  ⏭️  {os.path.basename(fp)} (card už applied)')
    elif o in c:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c.replace(o, n, 1))
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⚠️  {os.path.basename(fp)} anchor missing')
