"""
PHASE 11 — Modální okna pro long content + statické stránky (no-scroll)

USER:
  1) "když se nevejde text na stránku tak vytvoř popup at je stránka statická"
  2) "nevidím Predict AI celý taky popup / modální okno"

ADDS:
  A) Generic InfoModal overlay (reusable)
  B) Klik na AI tile (Meta Brain, Predict, Coordinator) → modal s plnou hodnotou
  C) Klik na AI Tasks / AI Pending lists → modal s úplným obsahem
  D) CSS: stránky jsou statické (no-scroll), obsah který přeteče = do modalu

Idempotent. Marker: PHASE11_MODAL_POPUPS_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: Add generic InfoModal HTML + CSS before </body>
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_BODY = "</body>"

INJECT_MODAL = """<!-- PHASE11_MODAL_POPUPS_APPLIED — Generic InfoModal -->
<div id="infoModal" class="info-modal" onclick="if(event.target===this)closeInfoModal()">
  <div class="info-modal-body">
    <div class="info-modal-header">
      <span class="info-modal-icon" id="im-icon">ℹ</span>
      <span class="info-modal-title" id="im-title">—</span>
      <button class="info-modal-close" onclick="closeInfoModal()">✕</button>
    </div>
    <div class="info-modal-content" id="im-content">—</div>
  </div>
</div>
<style>
.info-modal{position:fixed;inset:0;background:rgba(0,0,0,.82);z-index:600;display:none;align-items:center;justify-content:center;padding:20px;}
.info-modal.show{display:flex;}
.info-modal-body{background:var(--bg1);border:1px solid var(--bda);border-radius:var(--r3);max-width:760px;width:100%;max-height:85vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.5);}
.info-modal-header{display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid var(--bd);flex-shrink:0;}
.info-modal-icon{font-size:22px;}
.info-modal-title{flex:1;font-size:15px;font-weight:600;color:var(--tx1);}
.info-modal-close{background:var(--bg3);border:1px solid var(--bd);color:var(--tx1);border-radius:8px;padding:6px 12px;cursor:pointer;font-size:14px;font-family:var(--sans);}
.info-modal-close:hover{background:var(--bg4);}
.info-modal-content{padding:16px 20px;overflow-y:auto;color:var(--tx2);font-size:13px;line-height:1.6;flex:1;scrollbar-width:thin;scrollbar-color:var(--bg4) transparent;}
.info-modal-content pre{font-family:var(--mono);font-size:11px;background:var(--bg2);border-radius:8px;padding:10px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;color:var(--tx1);}
.info-modal-content .im-kv{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:12px;}
.info-modal-content .im-kv .k{color:var(--tx3);font-family:var(--mono);}
.info-modal-content .im-kv .v{color:var(--tx1);}
/* PHASE11 — statické stránky: page-ai má fixed height, ne scroll */
#page-ai.active, #page-logy.active{overflow:hidden !important;}
</style>
<script>
function openInfoModal(title, content, opts) {
  const modal = document.getElementById('infoModal');
  if (!modal) return;
  const opt = opts || {};
  document.getElementById('im-icon').textContent = opt.icon || 'ℹ';
  document.getElementById('im-title').textContent = title || '—';
  const ct = document.getElementById('im-content');
  if (opt.html) ct.innerHTML = content;
  else if (opt.pre) ct.innerHTML = '<pre>' + String(content || '—').replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])) + '</pre>';
  else ct.textContent = String(content || '—');
  modal.classList.add('show');
}
function closeInfoModal() {
  const modal = document.getElementById('infoModal');
  if (modal) modal.classList.remove('show');
}
// Esc closes modal
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeInfoModal(); });

// AI tile handlers — click opens modal with full variable value
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
}
</script>
"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH B: Make Meta Brain, Predict, Coordinator tiles clickable
# ═══════════════════════════════════════════════════════════════════════════
OLD_AI_TILES = """    <div class="sect" style="color:var(--purple);">AI MODULY</div>
    <div class="tile-grid g3">
      <div class="tile"><div class="t-top"><span class="t-icon">🧠</span><div class="t-info"><span class="t-lbl">Meta Brain</span><span class="t-cat">AI</span></div></div><span class="t-val" id="ai-meta" style="color:var(--purple);">—</span></div>
      <div class="tile"><div class="t-top"><span class="t-icon">🔮</span><div class="t-info"><span class="t-lbl">Predict</span><span class="t-cat">AI</span></div></div><span class="t-val" id="ai-predict" style="color:var(--purple);">—</span></div>
      <div class="tile"><div class="t-top"><span class="t-icon">🤝</span><div class="t-info"><span class="t-lbl">Coordinator</span><span class="t-cat">AI</span></div></div><span class="t-val" id="ai-coord" style="color:var(--purple);">—</span></div>
    </div>"""

NEW_AI_TILES = """    <div class="sect" style="color:var(--purple);">AI MODULY</div>
    <div class="tile-grid g3">
      <div class="tile" onclick="openAiTileModal('sh_meta_last_decision','🧠 Meta Brain — poslední rozhodnutí','🧠')" title="Klikni pro celý obsah rozhodnutí Meta Brain"><div class="t-top"><span class="t-icon">🧠</span><div class="t-info"><span class="t-lbl">Meta Brain</span><span class="t-cat">AI · klik</span></div></div><span class="t-val" id="ai-meta" style="color:var(--purple);">—</span></div>
      <div class="tile" onclick="openAiTileModal('sh_predict_last_action','🔮 Predict AI — poslední návrh','🔮')" title="Klikni pro celý obsah predikce"><div class="t-top"><span class="t-icon">🔮</span><div class="t-info"><span class="t-lbl">Predict</span><span class="t-cat">AI · klik</span></div></div><span class="t-val" id="ai-predict" style="color:var(--purple);">—</span></div>
      <div class="tile" onclick="openAiTileModal('sh_ai_coord_last_action','🤝 Coordinator AI — poslední akce','🤝')" title="Klikni pro celý obsah koordinace"><div class="t-top"><span class="t-icon">🤝</span><div class="t-info"><span class="t-lbl">Coordinator</span><span class="t-cat">AI · klik</span></div></div><span class="t-val" id="ai-coord" style="color:var(--purple);">—</span></div>
    </div>"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH C: Add "Zobrazit celý" button to AI Tasks + Pending cards (RPi version)
# ═══════════════════════════════════════════════════════════════════════════
OLD_AITASKS_RPI = """      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI TASKS</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">📋</span><span class="card-lbl">Otevřené</span><div class="btn cyan" onclick="loadAITasks()" style="padding:3px 8px;font-size:10px;">⟳</div></div>
          <div id="aiTasksList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:140px;overflow-y:auto;scrollbar-width:thin;">Klikni ⟳</div>
        </div>
      </div>
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI PENDING</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">⏳</span><span class="card-lbl">Čekající (48h)</span></div>
          <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:140px;overflow-y:auto;scrollbar-width:thin;">—</div>
        </div>
      </div>"""

NEW_AITASKS_RPI = """      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI TASKS</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row">
            <span class="card-icon">📋</span><span class="card-lbl">Otevřené</span>
            <div class="btn" onclick="openAiTasksModal()" style="padding:3px 8px;font-size:10px;" title="Zobrazit celý obsah v popupu">⛶</div>
            <div class="btn cyan" onclick="loadAITasks()" style="padding:3px 8px;font-size:10px;">⟳</div>
          </div>
          <div id="aiTasksList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:90px;overflow:hidden;cursor:pointer;" onclick="openAiTasksModal()" title="Klikni pro celý obsah">Klikni ⟳</div>
        </div>
      </div>
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI PENDING</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row">
            <span class="card-icon">⏳</span><span class="card-lbl">Čekající (48h)</span>
            <div class="btn" onclick="openAiPendingModal()" style="padding:3px 8px;font-size:10px;" title="Zobrazit celý obsah v popupu">⛶</div>
          </div>
          <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:90px;overflow:hidden;cursor:pointer;" onclick="openAiPendingModal()" title="Klikni pro celý obsah">—</div>
        </div>
      </div>"""

# Desktop variant
OLD_AITASKS_DESKTOP = """      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI TASKS (GOOGLE SHEETS)</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">📋</span><span class="card-lbl">Otevřené úkoly</span><div class="btn cyan" onclick="loadAITasks()" style="padding:3px 8px;font-size:10px;">⟳ Načíst</div></div>
          <div id="aiTasksList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:150px;overflow-y:auto;scrollbar-width:thin;">Klikni ⟳ pro načtení</div>
        </div>
      </div>
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI PENDING CHANGES</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">⏳</span><span class="card-lbl">Čekající změny (48h okno)</span></div>
          <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:150px;overflow-y:auto;scrollbar-width:thin;">—</div>
        </div>
      </div>"""

NEW_AITASKS_DESKTOP = """      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI TASKS (GOOGLE SHEETS)</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row">
            <span class="card-icon">📋</span><span class="card-lbl">Otevřené úkoly</span>
            <div class="btn" onclick="openAiTasksModal()" style="padding:3px 8px;font-size:10px;" title="Zobrazit celý v popupu">⛶</div>
            <div class="btn cyan" onclick="loadAITasks()" style="padding:3px 8px;font-size:10px;">⟳ Načíst</div>
          </div>
          <div id="aiTasksList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:110px;overflow:hidden;cursor:pointer;" onclick="openAiTasksModal()" title="Klikni pro celý obsah">Klikni ⟳ pro načtení</div>
        </div>
      </div>
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI PENDING CHANGES</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row">
            <span class="card-icon">⏳</span><span class="card-lbl">Čekající změny (48h okno)</span>
            <div class="btn" onclick="openAiPendingModal()" style="padding:3px 8px;font-size:10px;" title="Zobrazit celý v popupu">⛶</div>
          </div>
          <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:110px;overflow:hidden;cursor:pointer;" onclick="openAiPendingModal()" title="Klikni pro celý obsah">—</div>
        </div>
      </div>"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    orig = content
    changes = []
    is_crlf = '\r\n' in content[:4096]

    marker = 'PHASE11_MODAL_POPUPS_APPLIED'

    # A. Inject modal HTML + CSS + JS before </body>
    if marker in content:
        changes.append('⏭ Modal (už applied)')
    elif ANCHOR_BODY in content:
        inj = INJECT_MODAL.replace('\n', '\r\n') if is_crlf else INJECT_MODAL
        # insert before LAST </body>
        idx = content.rfind(ANCHOR_BODY)
        content = content[:idx] + inj + content[idx:]
        changes.append('+ Generic InfoModal (HTML + CSS + JS)')
    else:
        changes.append('❌ </body> not found')

    # B. AI tiles clickable
    def do(old, new, label):
        nonlocal content
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ ' + label)
        else:
            changes.append('⏭ ' + label + ' (anchor missing)')

    do(OLD_AI_TILES, NEW_AI_TILES, 'AI tiles clickable (Meta/Predict/Coordinator)')
    # AI Tasks/Pending — zkus obě varianty
    if OLD_AITASKS_RPI.replace('\n','\r\n' if is_crlf else '\n') in content or OLD_AITASKS_RPI in content:
        do(OLD_AITASKS_RPI, NEW_AITASKS_RPI, 'AI Tasks/Pending clickable (RPi)')
    else:
        do(OLD_AITASKS_DESKTOP, NEW_AITASKS_DESKTOP, 'AI Tasks/Pending clickable (Desktop)')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 11 — Modal popupy + statické stránky')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
