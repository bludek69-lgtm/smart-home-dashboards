"""
PHASE 1 — Pracovna tiles: Xiaomi button + Pomodoro timer
Idempotent. Applies to all 3 dashboard variants (rpi, 1920x1080, 2880x1800).

ADDS:
  1) Xiaomi button tile (battery % + last press ago) in pracovna zone
     - Reads /api/manager/devices/device/{id} for Xiaomi device (in Pc Setup zone)
     - Reads sh_button_pc_event variable for last press type
  2) Pomodoro timer tile (25/5 min, localStorage state, TTS notification)
     - Self-contained JS, no HomeyScript changes
     - Click opens overlay with Start/Pause/Reset

Marker: PHASE1_PRACOVNA_APPLIED in code prevents re-apply.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE1_PRACOVNA_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 1: HTML block inside renderZoneDetail(zone) — for pracovna zone
# Anchor: "  // Roleta (jídelna) → tile"  (right before jidelna roleta block)
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_HTML = "  // Roleta (jídelna) → tile"

INJECT_HTML = """  // PHASE1_PRACOVNA_APPLIED — Pc Setup tiles (Xiaomi button + Pomodoro)
  if (zone === 'pracovna') {
    html += '<div class="sect">Pc Setup</div><div class="dev-tiles">';
    // Xiaomi button tile
    html += '<div class="dev-tile" id="pc-xiaomi-tile" onclick="openXiaomiButtonHelp()">' +
      '<div class="tile-icon">🎮</div>' +
      '<div class="tile-name">Xiaomi button</div>' +
      '<div class="tile-state off" id="pc-xiaomi-state">—</div>' +
    '</div>';
    // Pomodoro tile
    html += '<div class="dev-tile" id="pc-pomo-tile" onclick="openPomodoro()">' +
      '<div class="tile-icon">🍅</div>' +
      '<div class="tile-name">Pomodoro</div>' +
      '<div class="tile-state off" id="pc-pomo-state">idle</div>' +
    '</div>';
    html += '</div>';
    setTimeout(refreshXiaomiButtonState, 100);
    setTimeout(refreshPomodoroTile, 50);
  }

"""

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 2: JS helpers before function renderZoneDetail(zone) {
# Anchor: "let _tileData = [];"
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_JS = "let _tileData = [];"

INJECT_JS = """// ══ PHASE1_PRACOVNA_APPLIED — Xiaomi button + Pomodoro helpers ═══════════
async function refreshXiaomiButtonState() {
  const el = document.getElementById('pc-xiaomi-state');
  if (!el) return;
  try {
    if (typeof varMapLoaded !== 'undefined' && !varMapLoaded) await loadVarMap();
    const d = ALL_DEVICES && ALL_DEVICES['Xiaomi'];
    let bat = '';
    if (d) {
      try {
        const detail = await apiGet('/api/manager/devices/device/' + d.id);
        const co = detail.capabilitiesObj || {};
        if (co.measure_battery && co.measure_battery.value != null) {
          bat = Math.round(Number(co.measure_battery.value)) + '%';
        } else if (co.alarm_battery && co.alarm_battery.value === true) {
          bat = 'LOW!';
        } else if (co.alarm_battery && co.alarm_battery.value === false) {
          bat = 'ok';
        }
      } catch(_) {}
    }
    const ev = String((ALL_VARS && ALL_VARS['sh_button_pc_event'] && ALL_VARS['sh_button_pc_event'].value) || 'idle');
    const evShort = ev && ev !== 'idle' ? ev.replace('_click','× klik').replace('long','long press') : '';
    el.textContent = (bat || '—') + (evShort ? ' · ' + evShort : '');
    el.className = 'tile-state ' + ((bat === 'LOW!' ) ? 'warn' : (bat ? 'on' : 'off'));
  } catch(e) {
    el.textContent = 'err';
  }
}

function openXiaomiButtonHelp() {
  try { if (!varMapLoaded) loadVarMap(); } catch(_){}
  const lastEvt = String((ALL_VARS && ALL_VARS['sh_button_pc_event'] && ALL_VARS['sh_button_pc_event'].value) || 'idle');
  const body = '<div class="dd-card">' +
    '<div class="dd-label">Poslední akce</div>' +
    '<div style="font-family:var(--mono);font-size:18px;padding:8px 0;">' + lastEvt + '</div>' +
  '</div>' +
  '<div class="dd-card">' +
    '<div class="dd-label">Gesta</div>' +
    '<table style="width:100%;font-size:13px;line-height:1.7;">' +
      '<tr><td style="color:var(--tx3);width:90px;">1× klik</td><td>Toggle pracovna světlo</td></tr>' +
      '<tr><td style="color:var(--tx3);">2× klik</td><td>Toggle PC zásuvka</td></tr>' +
      '<tr><td style="color:var(--tx3);">3× klik</td><td>Toggle kávovar + TTS</td></tr>' +
      '<tr><td style="color:var(--tx3);">4× klik</td><td>Scéna WORK</td></tr>' +
      '<tr><td style="color:var(--tx3);">Long press</td><td>Konec práce (OFF vše)</td></tr>' +
    '</table>' +
  '</div>' +
  '<div class="dd-card">' +
    '<div class="dd-label">Stav</div>' +
    '<div id="xiaomi-stav" style="font-family:var(--mono);font-size:14px;padding:8px 0;">Načítám…</div>' +
    '<div class="btn" onclick="refreshXiaomiButtonDetail()">↻ Obnovit</div>' +
  '</div>';
  document.getElementById('ddIcon').textContent = '🎮';
  document.getElementById('ddName').textContent = 'Xiaomi button · Pc Setup';
  document.getElementById('ddBody').innerHTML = body;
  document.getElementById('devDetailOverlay').classList.add('show');
  refreshXiaomiButtonDetail();
}

async function refreshXiaomiButtonDetail() {
  const el = document.getElementById('xiaomi-stav');
  if (!el) return;
  try {
    if (!varMapLoaded) await loadVarMap();
    const d = ALL_DEVICES && ALL_DEVICES['Xiaomi'];
    if (!d) { el.textContent = 'Zařízení "Xiaomi" není načtené v ALL_DEVICES.'; return; }
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const co = detail.capabilitiesObj || {};
    const bat = co.measure_battery && co.measure_battery.value != null ? Math.round(co.measure_battery.value) + '%' : '—';
    const alarm = co.alarm_battery ? (co.alarm_battery.value ? 'LOW' : 'ok') : '—';
    const avail = detail.available === false ? '❌ offline' : '✅ online';
    el.innerHTML =
      'Battery: <strong>' + bat + '</strong> · Alarm: <strong>' + alarm + '</strong><br>' +
      'Available: ' + avail + '<br>' +
      'ID: <span style="font-size:10px;color:var(--tx3);">' + d.id + '</span>';
  } catch(e) { el.textContent = 'Chyba: ' + e.message; }
}

// ── Pomodoro ─────────────────────────────────────────────────────────────
const POMO_WORK_MIN = 25;
const POMO_BREAK_MIN = 5;
let _pomoState = null;

function _pomoLoad() {
  try { _pomoState = JSON.parse(localStorage.getItem('pomo_state') || 'null'); } catch(_){}
  if (!_pomoState) _pomoState = { mode:'idle', startedAt:0, totalSec:POMO_WORK_MIN*60, remaining:POMO_WORK_MIN*60, paused:false, completed:0 };
}
function _pomoSave() { try { localStorage.setItem('pomo_state', JSON.stringify(_pomoState)); } catch(_){} }

function _pomoTick() {
  _pomoLoad();
  if (_pomoState.mode === 'idle' || _pomoState.paused) return;
  const elapsed = Math.floor((Date.now() - _pomoState.startedAt) / 1000);
  _pomoState.remaining = Math.max(0, _pomoState.totalSec - elapsed);
  if (_pomoState.remaining <= 0) {
    // Phase end — transition
    if (_pomoState.mode === 'work') {
      _pomoState.completed += 1;
      _pomoState.mode = 'break';
      _pomoState.totalSec = POMO_BREAK_MIN * 60;
      _pomoState.startedAt = Date.now();
      _pomoState.remaining = POMO_BREAK_MIN * 60;
      try { sendReq('sh_tts_speaker', 'kuchyn'); } catch(_){}
      try { sendReq('sh_tts_text', 'Pomodoro hotovo. Pauza pet minut.'); } catch(_){}
    } else {
      _pomoState.mode = 'work';
      _pomoState.totalSec = POMO_WORK_MIN * 60;
      _pomoState.startedAt = Date.now();
      _pomoState.remaining = POMO_WORK_MIN * 60;
      try { sendReq('sh_tts_speaker', 'kuchyn'); } catch(_){}
      try { sendReq('sh_tts_text', 'Pauza skoncila. Pokracujeme v praci.'); } catch(_){}
    }
    _pomoSave();
  }
  refreshPomodoroTile();
  _pomoBigUpdate();
}

function refreshPomodoroTile() {
  _pomoLoad();
  const el = document.getElementById('pc-pomo-state');
  if (!el) return;
  if (_pomoState.mode === 'idle') {
    el.textContent = 'idle';
    el.className = 'tile-state off';
    return;
  }
  const min = Math.floor(_pomoState.remaining / 60);
  const sec = _pomoState.remaining % 60;
  const t = String(min).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
  const icon = _pomoState.mode === 'work' ? '💼' : '☕';
  const pauseMark = _pomoState.paused ? '⏸ ' : '';
  el.textContent = pauseMark + icon + ' ' + t + ' · ' + _pomoState.completed + '×';
  el.className = 'tile-state on';
}

function pomoStart(mode) {
  _pomoLoad();
  _pomoState.mode = mode;
  _pomoState.totalSec = (mode === 'work' ? POMO_WORK_MIN : POMO_BREAK_MIN) * 60;
  _pomoState.remaining = _pomoState.totalSec;
  _pomoState.startedAt = Date.now();
  _pomoState.paused = false;
  _pomoSave();
  refreshPomodoroTile();
  _pomoBigUpdate();
}

function pomoPauseToggle() {
  _pomoLoad();
  if (_pomoState.mode === 'idle') return;
  if (_pomoState.paused) {
    _pomoState.startedAt = Date.now() - (_pomoState.totalSec - _pomoState.remaining) * 1000;
    _pomoState.paused = false;
  } else {
    _pomoState.paused = true;
  }
  _pomoSave();
  refreshPomodoroTile();
  _pomoBigUpdate();
}

function pomoReset() {
  _pomoState = { mode:'idle', startedAt:0, totalSec:POMO_WORK_MIN*60, remaining:POMO_WORK_MIN*60, paused:false, completed:0 };
  _pomoSave();
  refreshPomodoroTile();
  _pomoBigUpdate();
}

function openPomodoro() {
  _pomoLoad();
  const body = '<div class="dd-card">' +
    '<div class="dd-label">Pomodoro timer · 25/5 min</div>' +
    '<div style="text-align:center;padding:24px 0;font-family:var(--mono);font-size:56px;font-weight:600;color:var(--green);" id="pomo-big">25:00</div>' +
    '<div style="text-align:center;color:var(--tx2);font-size:13px;padding-bottom:8px;" id="pomo-info">připraveno</div>' +
    '<div class="dd-onoff">' +
      '<div class="dd-btn dd-btn-on" onclick="pomoStart(\\'work\\');_pomoBigUpdate();">💼 Práce 25</div>' +
      '<div class="dd-btn" onclick="pomoStart(\\'break\\');_pomoBigUpdate();">☕ Pauza 5</div>' +
    '</div>' +
  '</div>' +
  '<div class="dd-card">' +
    '<div class="dd-onoff">' +
      '<div class="dd-btn" onclick="pomoPauseToggle();_pomoBigUpdate();">⏸ Pause/Resume</div>' +
      '<div class="dd-btn dd-btn-off" onclick="pomoReset();_pomoBigUpdate();">↺ Reset</div>' +
    '</div>' +
  '</div>' +
  '<div class="dd-card">' +
    '<div class="dd-label">Info</div>' +
    '<div style="font-size:12px;color:var(--tx2);line-height:1.6;">' +
      'Po skončení fáze zaznije TTS v kuchyni. Stav se ukládá do prohlížeče.<br>' +
      'Timer běží i při přepnutí stránky — drží se přes localStorage.' +
    '</div>' +
  '</div>';
  document.getElementById('ddIcon').textContent = '🍅';
  document.getElementById('ddName').textContent = 'Pomodoro · Pc Setup';
  document.getElementById('ddBody').innerHTML = body;
  document.getElementById('devDetailOverlay').classList.add('show');
  _pomoBigUpdate();
}

function _pomoBigUpdate() {
  _pomoLoad();
  const big = document.getElementById('pomo-big');
  const info = document.getElementById('pomo-info');
  if (!big) return;
  const min = Math.floor(_pomoState.remaining / 60);
  const sec = _pomoState.remaining % 60;
  big.textContent = String(min).padStart(2,'0') + ':' + String(sec).padStart(2,'0');
  if (info) {
    let lbl;
    if (_pomoState.mode === 'idle') lbl = 'připraveno';
    else if (_pomoState.mode === 'work') lbl = _pomoState.paused ? '⏸ práce (pauza)' : '💼 práce';
    else lbl = _pomoState.paused ? '⏸ break (pauza)' : '☕ break';
    info.textContent = lbl + ' · dokončeno cyklů: ' + _pomoState.completed;
  }
  big.style.color = _pomoState.mode === 'work' ? 'var(--green)' : (_pomoState.mode === 'break' ? 'var(--cyan)' : 'var(--tx2)');
}

// Global tick — 1 Hz
setInterval(_pomoTick, 1000);
// ══ END PHASE1 ═══════════════════════════════════════════════════════════

"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP (not found): {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    if MARKER in content:
        print(f"  ⏭️  ALREADY PATCHED: {os.path.basename(fp)}")
        return
    orig = content
    changes = []

    # Detect CRLF vs LF
    is_crlf = '\r\n' in content[:4096]
    nl = '\r\n' if is_crlf else '\n'

    anchor_html = ANCHOR_HTML if not is_crlf else ANCHOR_HTML  # no newlines in anchor itself
    inject_html = INJECT_HTML if not is_crlf else INJECT_HTML.replace('\n', '\r\n')

    if anchor_html in content:
        content = content.replace(anchor_html, inject_html + anchor_html, 1)
        changes.append('HTML block (Xiaomi + Pomodoro tiles in pracovna)')
    else:
        changes.append('❌ HTML anchor not found')

    anchor_js = ANCHOR_JS
    inject_js = INJECT_JS if not is_crlf else INJECT_JS.replace('\n', '\r\n')

    if anchor_js in content:
        content = content.replace(anchor_js, inject_js + anchor_js, 1)
        changes.append('JS helpers (openXiaomiButtonHelp, openPomodoro, timer)')
    else:
        changes.append('❌ JS anchor not found')

    if content != orig and not any(c.startswith('❌') for c in changes):
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
        for c in changes:
            print(f"     + {c}")
    else:
        print(f"  ⚠️  NO CHANGES (or anchor missing): {os.path.basename(fp)}")
        for c in changes:
            print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 1 — Pracovna tiles (Xiaomi button + Pomodoro)')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
