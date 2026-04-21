"""
PHASE 12 — Modal expansion example (pro desktop varianty)
Aplikuje stejný refactor explainLastAction jako byl ručně udělán na RPi.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD_BUTTON = '''<div class="btn" style="border-color:var(--purple);background:var(--purpled);color:var(--purple);width:100%;" onclick="runScript('sh_explain_last_action_v1')">🧠 Vysvětli poslední rozhodnutí</div>'''

NEW_BUTTON = '''<div class="btn" style="border-color:var(--purple);background:var(--purpled);color:var(--purple);width:100%;" onclick="explainLastAction()" title="Vygeneruje vysvětlení přes Gemini a otevře popup">🧠 Vysvětli poslední rozhodnutí</div>'''

OLD_RESULT_DIV = '''<div id="ai-explain-result" style="display:none;margin-top:8px;padding:10px 12px;background:var(--purpled);border:1px solid rgba(160,112,240,.2);border-radius:var(--r2);font-size:12px;color:var(--purple);"></div>'''

NEW_RESULT_DIV = '''<!-- PHASE12_MODAL_EXPAND_APPLIED — inline div removed, výsledek do modalu -->'''

OLD_FN = """async function explainLastAction() {
  const btn = document.querySelector('[onclick="explainLastAction()"]');
  if (btn) { btn.textContent = '⏳ Ptám se Gemini…'; btn.style.opacity = '.6'; }
  try {
    await runScript('sh_explain_last_action_v1');
    // Zobraz výsledek po 4s (TTS pipeline potřebuje čas)
    setTimeout(async () => {
      await loadVarMap();
      const result = ALL_VARS['sh_last_explain_result']?.value || '—';
      const ts     = ALL_VARS['sh_last_explain_ts']?.value || '';
      const el = document.getElementById('ai-explain-result');
      if (el) {
        el.textContent = result;
        el.style.display = 'block';
      }
      if (btn) { btn.textContent = '🧠 Vysvětli poslední akci'; btn.style.opacity = '1'; }
    }, 4000);
  } catch(e) {
    if (btn) { btn.textContent = '🧠 Vysvětli poslední akci'; btn.style.opacity = '1'; }
  }
}"""

NEW_FN = """// PHASE12_MODAL_EXPAND_APPLIED — výsledek do modalu místo inline divu
async function explainLastAction() {
  try {
    openInfoModal('🧠 Vysvětlení poslední akce', '⏳ Ptám se Gemini…', { icon: '🧠' });
    await runScript('sh_explain_last_action_v1');
    setTimeout(async () => {
      try {
        await loadVarMap();
        const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
        const result = (av['sh_last_explain_result'] && av['sh_last_explain_result'].value) || '(žádný výsledek)';
        const ts = (av['sh_last_explain_ts'] && av['sh_last_explain_ts'].value) || '';
        const title = '🧠 Vysvětlení poslední akce' + (ts ? ' · ' + ts : '');
        openInfoModal(title, String(result), { icon: '🧠', pre: true });
      } catch(e) {
        openInfoModal('🧠 Vysvětlení', 'Chyba: ' + e.message, { icon: '⚠' });
      }
    }, 4000);
  } catch(e) {
    openInfoModal('🧠 Vysvětlení', 'Chyba: ' + e.message, { icon: '⚠' });
  }
}"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    is_crlf = '\r\n' in c[:4096]
    orig = c
    changes = []

    def do(old, new, label):
        nonlocal c
        old2 = old.replace('\n','\r\n') if is_crlf else old
        new2 = new.replace('\n','\r\n') if is_crlf else new
        if old2 in c:
            c = c.replace(old2, new2, 1)
            changes.append('+ ' + label)
        elif 'PHASE12_MODAL_EXPAND_APPLIED' in c:
            changes.append('⏭ ' + label + ' (už applied)')
        else:
            changes.append('⏭ ' + label + ' (anchor missing)')

    do(OLD_BUTTON, NEW_BUTTON, 'Button onclick → explainLastAction()')
    do(OLD_RESULT_DIV, NEW_RESULT_DIV, 'Remove inline result div')
    do(OLD_FN, NEW_FN, 'explainLastAction → openInfoModal')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    for ch in changes:
        print(f'     {ch}')


if __name__ == '__main__':
    print('PHASE 12 — Example modal expansion (desktop)')
    print('='*60)
    for f in FILES:
        patch(f)
