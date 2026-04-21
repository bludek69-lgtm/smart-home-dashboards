"""
PHASE 11 HOTFIX — modal JS fix pro desktop varianty
  - window.ALL_VARS → ALL_VARS (let-scoped, ne na window)
  - Auto-load pokud placeholder
  - JSON pretty-print s meta info
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD = """// AI tile handlers — click opens modal with full variable value
function openAiTileModal(varName, title, icon) {
  try {
    const val = (window.ALL_VARS && window.ALL_VARS[varName] && window.ALL_VARS[varName].value);
    const raw = String(val == null ? '—' : val);
    // Try JSON-pretty format
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
    openInfoModal(title, content, { icon: icon || '🧠', pre: isPre });
  } catch(e) { openInfoModal(title || 'Info', String(e), { icon: '⚠' }); }
}

function openAiTasksModal() {
  const el = document.getElementById('aiTasksList');
  if (!el) return;
  const content = el.innerText || el.textContent || '—';
  openInfoModal('📋 AI Tasks (kompletní)', content, { icon: '📋', pre: true });
}
function openAiPendingModal() {
  const el = document.getElementById('aiPendingList');
  if (!el) return;
  const content = el.innerText || el.textContent || '—';
  openInfoModal('⏳ AI Pending Changes (kompletní)', content, { icon: '⏳', pre: true });
}"""

NEW = """// AI tile handlers — click opens modal with full variable value
// FIX: ALL_VARS je let-scoped, ne na window → použij přímé jméno
async function openAiTileModal(varName, title, icon) {
  try {
    if (typeof varMapLoaded !== 'undefined' && !varMapLoaded) {
      openInfoModal(title || 'Načítám…', 'Načítám proměnné z Homey...', { icon: icon || '⏳' });
      if (typeof loadVarMap === 'function') await loadVarMap();
    }
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const entry = av && av[varName];
    const val = entry ? entry.value : null;
    const raw = (val == null || val === '') ? '(prázdné)' : String(val);
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
    const metaHtml = '<div style="font-size:10px;color:var(--tx3);padding-bottom:8px;margin-bottom:8px;border-bottom:1px solid var(--bd);font-family:var(--mono);">proměnná: <strong>' + varName + '</strong></div>';
    const mainHtml = isPre ? '<pre>' + content.replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])) + '</pre>'
                           : '<div style="white-space:pre-wrap;word-break:break-word;">' + content.replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])) + '</div>';
    openInfoModal(title, metaHtml + mainHtml, { icon: icon || '🧠', html: true });
  } catch(e) {
    openInfoModal(title || 'Info', 'Chyba: ' + e.message, { icon: '⚠' });
  }
}

async function openAiTasksModal() {
  try {
    const el = document.getElementById('aiTasksList');
    if (!el) { openInfoModal('📋 AI Tasks', 'Element nenalezen', {icon:'⚠'}); return; }
    const placeholder = /Klikni\\s+⟳/i;
    if (placeholder.test(el.textContent) && typeof loadAITasks === 'function') {
      openInfoModal('📋 AI Tasks (načítám…)', 'Stahuji data z Google Sheets…', {icon:'⏳'});
      await loadAITasks();
    }
    const content = el.innerText || el.textContent || '—';
    openInfoModal('📋 AI Tasks (kompletní)', content, { icon: '📋', pre: true });
  } catch(e) {
    openInfoModal('📋 AI Tasks', 'Chyba: ' + e.message, {icon:'⚠'});
  }
}
async function openAiPendingModal() {
  try {
    const el = document.getElementById('aiPendingList');
    if (!el) { openInfoModal('⏳ AI Pending', 'Element nenalezen', {icon:'⚠'}); return; }
    const content = el.innerText || el.textContent || '—';
    openInfoModal('⏳ AI Pending Changes (kompletní)', content, { icon: '⏳', pre: true });
  } catch(e) {
    openInfoModal('⏳ AI Pending', 'Chyba: ' + e.message, {icon:'⚠'});
  }
}"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    is_crlf = '\r\n' in c[:4096]
    o = OLD.replace('\n','\r\n') if is_crlf else OLD
    n = NEW.replace('\n','\r\n') if is_crlf else NEW
    if o in c:
        c2 = c.replace(o, n, 1)
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c2)
        print(f'  ✅ {os.path.basename(fp)}')
    elif 'typeof ALL_VARS' in c:
        print(f'  ⏭️  {os.path.basename(fp)} (už opraveno)')
    else:
        print(f'  ⚠️  {os.path.basename(fp)} (anchor missing)')


if __name__ == '__main__':
    for f in FILES:
        patch(f)
