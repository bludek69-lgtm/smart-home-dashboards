"""
PHASE 12a — Morning Tune clickable (desktop variants)
Desktop má jinou impl. než RPi, musí se patchnout separátně.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD = """    if (recommendation && recommendation.length > 5) {
      html += '<div style="padding:10px;background:rgba(176,133,255,.08);border:1px solid rgba(176,133,255,.3);border-radius:6px;">';
      html += '<div style="font-size:10px;color:var(--purple);font-weight:600;margin-bottom:4px;">🧠 GEMINI DOPORUČENÍ</div>';
      html += '<div style="font-size:12px;color:var(--tx1);line-height:1.5;">'+recommendation+'</div>';
      html += '</div>';
    } else {"""

NEW = """    if (recommendation && recommendation.length > 5) {
      // PHASE12A_EVENTLOG_TUNE_MODAL_APPLIED — klikatelné + truncate
      const trunc = recommendation.length > 250 ? recommendation.substring(0, 250).replace(/\\s+\\S*$/, '') + '…' : recommendation;
      const isTrunc = recommendation.length > 250;
      html += '<div onclick="openMorningTuneModal()" style="padding:10px;background:rgba(176,133,255,.08);border:1px solid rgba(176,133,255,.3);border-radius:6px;cursor:pointer;" title="Klikni pro celý text (' + recommendation.length + ' znaků)">';
      html += '<div style="font-size:10px;color:var(--purple);font-weight:600;margin-bottom:4px;">🧠 GEMINI DOPORUČENÍ' + (isTrunc ? ' · 📖 klik pro celý' : '') + '</div>';
      html += '<div style="font-size:12px;color:var(--tx1);line-height:1.5;">'+trunc+'</div>';
      html += '</div>';
    } else {"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    is_crlf = '\r\n' in c[:4096]
    o = OLD.replace('\n','\r\n') if is_crlf else OLD
    n = NEW.replace('\n','\r\n') if is_crlf else NEW
    if 'openMorningTuneModal()"' in c:
        print(f'  ⏭️  {os.path.basename(fp)} (už applied)')
        return
    if o in c:
        c2 = c.replace(o, n, 1)
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c2)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⚠️  {os.path.basename(fp)} anchor missing')


if __name__ == '__main__':
    for f in FILES:
        patch(f)
