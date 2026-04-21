"""
PHASE 12c — AI poznámky per zone → modal

CONTEXT:
  V zone detail je sekce "AI poznámky" s `sh_ai_zone_<name>` textem.
  Může být DLOUHÝ (Gemini generuje kontextové poznámky). Momentálně renderuje
  jako inline textContent — overflow řeší CSS.

FIX:
  - Truncate na ~200 znaků + "…"
  - Klik → modal s celým textem + také zobrazit `sh_ai_learn_last_report` pokud
    relevant pro zone

Idempotent. Marker: PHASE12C_AI_NOTES_MODAL_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD = """  // AI notes per zone
  html += '<div class="sect">AI poznámky</div>' +
    '<div class="card">' +
      '<div class="card-row"><span class="card-icon">🧠</span><span class="card-lbl card-sub" id="zd-ai-' + zone + '">Načítám…</span></div>' +
    '</div>';

  document.getElementById('zdContent').innerHTML = html;

  // Fill AI notes
  const aiNote = ALL_VARS['sh_ai_zone_' + zone]?.value || 'Žádné poznámky pro tuto zónu.';
  const aiNoteEl = document.getElementById('zd-ai-' + zone);
  if (aiNoteEl) aiNoteEl.textContent = aiNote;
}"""

NEW = """  // PHASE12C_AI_NOTES_MODAL_APPLIED — klik → modal s plnými poznámkami
  html += '<div class="sect">AI poznámky</div>' +
    '<div class="card" onclick="openZoneAiNotes(\\''+zone+'\\')" style="cursor:pointer;" title="Klikni pro celé poznámky + AI learning report">' +
      '<div class="card-row"><span class="card-icon">🧠</span><span class="card-lbl card-sub" id="zd-ai-' + zone + '">Načítám…</span><span class="card-val" style="font-size:9px;color:var(--tx3);">📖 klik</span></div>' +
    '</div>';

  document.getElementById('zdContent').innerHTML = html;

  // Fill AI notes (truncate pro inline preview)
  const aiNoteFull = ALL_VARS['sh_ai_zone_' + zone]?.value || 'Žádné poznámky pro tuto zónu.';
  const aiNoteEl = document.getElementById('zd-ai-' + zone);
  if (aiNoteEl) {
    const trunc = aiNoteFull.length > 150 ? aiNoteFull.substring(0, 150).replace(/\\s+\\S*$/, '') + '…' : aiNoteFull;
    aiNoteEl.textContent = trunc;
    aiNoteEl.title = 'Celkem ' + aiNoteFull.length + ' znaků · klikni pro celý text';
  }
}

// PHASE12C_AI_NOTES_MODAL_APPLIED — modal handler
function openZoneAiNotes(zone) {
  try {
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const zoneNames = {jidelna:'Jídelna',kitchen:'Kuchyně',bedroom:'Ložnice',bathroom:'Koupelna',pracovna:'Pracovna',pradelna:'Prádelna',predsin:'Předsíň',toilet:'Toaleta',spolecne:'Společné'};
    const zoneName = zoneNames[zone] || zone;
    const noteKey = 'sh_ai_zone_' + zone;
    const note = String((av[noteKey] && av[noteKey].value) || 'Žádné poznámky pro tuto zónu.');
    const learnReport = String((av['sh_ai_learn_last_report'] && av['sh_ai_learn_last_report'].value) || '');
    const learnTs = String((av['sh_ai_learn_last_ts'] && av['sh_ai_learn_last_ts'].value) || '');

    const esc = s => String(s).replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));

    let html = '<div style="font-size:11px;color:var(--tx3);padding-bottom:8px;margin-bottom:10px;border-bottom:1px solid var(--bd);font-family:var(--mono);">var: <strong>' + noteKey + '</strong> · zone: ' + zone + '</div>';
    html += '<div style="margin-bottom:14px;padding:12px;background:rgba(176,133,255,.08);border-radius:8px;">';
    html += '<div style="font-size:11px;color:var(--purple);font-weight:600;margin-bottom:6px;">🧠 Poznámky k zóně</div>';
    html += '<div style="white-space:pre-wrap;word-break:break-word;line-height:1.6;">' + esc(note) + '</div>';
    html += '</div>';

    if (learnReport && learnReport.length > 5) {
      html += '<div style="padding:12px;background:rgba(255,255,255,.03);border-radius:8px;">';
      html += '<div style="font-size:11px;color:var(--cyan);font-weight:600;margin-bottom:6px;">🎓 AI Learning report (globální)' + (learnTs ? ' · před ' + Math.floor((Date.now()/1000 - Number(learnTs))/60) + ' min' : '') + '</div>';
      html += '<div style="white-space:pre-wrap;word-break:break-word;line-height:1.5;font-size:11px;color:var(--tx2);">' + esc(learnReport) + '</div>';
      html += '</div>';
    }

    openInfoModal('🧠 AI poznámky — ' + zoneName, html, { icon: '🧠', html: true });
  } catch(e) {
    openInfoModal('AI poznámky', 'Chyba: ' + e.message, { icon: '⚠' });
  }
}
_AI_NOTES_TERMINATOR_"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    orig = c
    is_crlf = '\r\n' in c[:4096]
    marker = 'PHASE12C_AI_NOTES_MODAL_APPLIED'

    if marker in c:
        print(f'  ⏭️  {os.path.basename(fp)} (už applied)')
        return

    # Remove my terminator placeholder (just helps me visualize in the source)
    new = NEW.replace('_AI_NOTES_TERMINATOR_', '').rstrip() + '\n'

    o = OLD.replace('\n','\r\n') if is_crlf else OLD
    n = new.replace('\n','\r\n') if is_crlf else new

    if o in c:
        c2 = c.replace(o, n, 1)
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c2)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⚠️  {os.path.basename(fp)} anchor missing')


if __name__ == '__main__':
    print('PHASE 12c — AI poznámky per zone → modal')
    print('='*60)
    for f in FILES:
        patch(f)
