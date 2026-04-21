"""
PHASE 3 — TV remote overlay (bedroom)
Idempotent. Marker: PHASE3_TV_REMOTE_APPLIED.

ADDS:
  1) Tile "📺 TV ovládání" v bedroom zone
  2) Full remote overlay:
     - Power, Mute
     - Volume slider + ±
     - Play/Pause/Stop/Next/Prev (via speaker_playing/speaker_next/speaker_prev)
     - Channel +/- (via var sh_tv_remote_cmd)
     - Arrows up/down/left/right + OK
     - Home, Back
     - Numeric 0-9
  3) CSS pro remote (d-pad, numpad)
  4) Pattern: native capability first → fallback na sh_tv_remote_cmd variable
     (user si pak v Homey udělá flow: QUANDO sh_tv_remote_cmd è cambiata → dispatch)

REQUIRES (Homey setup po deploy):
  - Vytvořit proměnnou `sh_tv_remote_cmd` (string, default 'idle')
  - Volitelně: flow "SH – TV Remote Dispatcher" který na změnu spustí příslušnou
    Android TV flow action (Canale su, Home, Back, Up/Down atd.)
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE3_TV_REMOTE_APPLIED'
TV_NAME = 'Televize v ložnici'

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 1: CSS for remote — inject before "/* ══ DEVICE DETAIL OVERLAY ══ */"
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_CSS = "/* ══ DEVICE DETAIL OVERLAY ══ */"

INJECT_CSS = """/* ══ PHASE3_TV_REMOTE_APPLIED — TV remote styles ══ */
.tvr-grid{display:grid;gap:6px;}
.tvr-btn{background:rgba(255,255,255,.08);border:1px solid var(--bd);border-radius:12px;padding:14px 8px;text-align:center;cursor:pointer;font-family:var(--sans);font-size:14px;font-weight:500;color:var(--tx1);user-select:none;min-height:48px;display:flex;align-items:center;justify-content:center;}
.tvr-btn:active{background:rgba(255,255,255,.18);transform:scale(.95);}
.tvr-btn.power{background:rgba(255,107,107,.18);border-color:rgba(255,107,107,.35);color:var(--red);}
.tvr-btn.primary{background:rgba(100,244,216,.18);border-color:rgba(100,244,216,.35);color:var(--cyan);}
.tvr-btn.ok{background:rgba(94,232,160,.2);border-color:rgba(94,232,160,.4);color:var(--green);font-weight:600;font-size:16px;}
.tvr-btn.arrow{font-size:22px;background:rgba(108,180,255,.1);border-color:rgba(108,180,255,.25);}
.tvr-btn.num{font-family:var(--mono);font-size:18px;font-weight:600;}
.tvr-btn.small{font-size:11px;padding:10px 6px;min-height:38px;}
.tvr-dpad{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;max-width:240px;margin:0 auto;}
.tvr-dpad .tvr-empty{}
.tvr-numpad{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;max-width:240px;margin:0 auto;}
.tvr-row{display:grid;gap:6px;}
.tvr-row-4{grid-template-columns:repeat(4,1fr);}
.tvr-row-3{grid-template-columns:repeat(3,1fr);}
.tvr-row-2{grid-template-columns:repeat(2,1fr);}

"""

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 2: TV tile in bedroom zone — BEFORE "// PHASE2 ... Zvlhčovač panel"
# (bedroom already has humidifier; insert TV tile right before)
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_TV_TILE = "  // PHASE2_HUM_VACUUM_FRIDGE_APPLIED — Zvlhčovač panel (bedroom)"

INJECT_TV_TILE = """  // PHASE3_TV_REMOTE_APPLIED — TV remote tile (bedroom)
  if (zone === 'bedroom') {
    html += '<div class="sect">TV · Ovládání</div><div class="dev-tiles">';
    html += '<div class="dev-tile" id="bed-tv-tile" onclick="openTvRemote()">' +
      '<div class="tile-icon">📺</div>' +
      '<div class="tile-name">TV remote</div>' +
      '<div class="tile-state off" id="bed-tv-state">—</div>' +
    '</div>';
    html += '</div>';
    setTimeout(refreshTvTile, 120);
  }

"""

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 3: JS helpers — before "let _tileData = [];"
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_JS = "let _tileData = [];"

INJECT_JS = """// ══ PHASE3_TV_REMOTE_APPLIED — TV remote helpers ═════════════════════════
const TV_DEVICE_NAME = 'Televize v ložnici';
const TV_CMD_VAR = 'sh_tv_remote_cmd';

async function _findTvDevice() {
  if (typeof varMapLoaded !== 'undefined' && !varMapLoaded) await loadVarMap();
  if (ALL_DEVICES && ALL_DEVICES[TV_DEVICE_NAME]) return { name: TV_DEVICE_NAME, ...ALL_DEVICES[TV_DEVICE_NAME] };
  // trim/lower match
  if (ALL_DEVICES) {
    const norm = TV_DEVICE_NAME.toLowerCase().replace(/[^a-z0-9]/g,'');
    for (const [k, v] of Object.entries(ALL_DEVICES)) {
      if (k.toLowerCase().replace(/[^a-z0-9]/g,'') === norm) return { name: k, ...v };
    }
    // substring 'televize' or 'loznic'
    for (const [k, v] of Object.entries(ALL_DEVICES)) {
      const kl = k.toLowerCase();
      if (kl.includes('televize') && (kl.includes('lozni') || kl.includes('ložni'))) return { name: k, ...v };
    }
  }
  try {
    const all = await apiGet('/api/manager/devices/device/');
    for (const [id, d] of Object.entries(all || {})) {
      const n = String(d.name || '');
      if (n.toLowerCase().includes('televize') && n.toLowerCase().includes('ložni')) {
        if (ALL_DEVICES) ALL_DEVICES[n] = { id, caps: d.capabilities || [] };
        return { name: n, id, caps: d.capabilities || [] };
      }
    }
  } catch(_){}
  return null;
}

let _tvDetailCache = null;
async function _tvGetDetail(force) {
  if (!force && _tvDetailCache && (Date.now() - _tvDetailCache.ts < 3000)) return _tvDetailCache.data;
  const d = await _findTvDevice();
  if (!d) return null;
  try {
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    _tvDetailCache = { ts: Date.now(), data: { id: d.id, detail } };
    return _tvDetailCache.data;
  } catch(e) { return null; }
}

async function refreshTvTile() {
  const el = document.getElementById('bed-tv-state');
  if (!el) return;
  try {
    const data = await _tvGetDetail(false);
    if (!data) { el.textContent = 'device?'; return; }
    const co = data.detail.capabilitiesObj || {};
    const on = co.onoff ? co.onoff.value : null;
    const vol = co.volume_set ? Math.round((co.volume_set.value || 0) * 100) : null;
    const muted = co.volume_mute ? !!co.volume_mute.value : false;
    let txt = on ? 'ON' : 'OFF';
    if (on && vol !== null) txt += ' · ' + vol + '%';
    if (muted) txt += ' 🔇';
    el.textContent = txt;
    el.className = 'tile-state ' + (on ? 'on' : 'off');
  } catch(_) { el.textContent = 'err'; }
}

// ── Remote action dispatchers ────────────────────────────────────────────
async function _tvSetCap(cap, val) {
  const d = await _findTvDevice();
  if (!d) { try { flash('⚠ TV nenalezena'); } catch(_){}; return false; }
  try {
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/' + cap, { value: val });
    return true;
  } catch(e) {
    try { flash('✗ ' + cap + ': ' + e.message); } catch(_){}
    return false;
  }
}

async function _tvHasCap(cap) {
  const d = await _findTvDevice();
  if (!d) return false;
  return Array.isArray(d.caps) && d.caps.includes(cap);
}

// Write to sh_tv_remote_cmd variable (fallback for non-capability actions)
// Homey flow on user side: QUANDO sh_tv_remote_cmd è cambiata → dispatch
async function _tvSendCmd(cmd) {
  try {
    if (!varMapLoaded) await loadVarMap();
    const v = ALL_VARS && ALL_VARS[TV_CMD_VAR];
    if (!v) {
      try { flash('⚠ Proměnná ' + TV_CMD_VAR + ' chybí. Vytvoř ji v Homey (string).'); } catch(_){}
      return false;
    }
    // Reset to idle first (so same cmd can fire repeatedly)
    await writeVar(TV_CMD_VAR, 'idle');
    await writeVar(TV_CMD_VAR, cmd);
    try { flash('📺 ' + cmd); } catch(_){}
    return true;
  } catch(e) {
    try { flash('✗ ' + e.message); } catch(_){}
    return false;
  }
}

// High-level buttons
async function tvPower() { const on = await _tvCurrentOn(); await _tvSetCap('onoff', !on); setTimeout(refreshTvOverlay, 300); setTimeout(refreshTvTile, 500); }
async function tvMute() {
  if (await _tvHasCap('volume_mute')) {
    const data = await _tvGetDetail(true);
    const cur = data && data.detail.capabilitiesObj.volume_mute ? !!data.detail.capabilitiesObj.volume_mute.value : false;
    await _tvSetCap('volume_mute', !cur);
  } else { _tvSendCmd('mute'); }
  setTimeout(refreshTvOverlay, 300);
}
async function tvVolUp() {
  if (await _tvHasCap('volume_up')) await _tvSetCap('volume_up', true);
  else { _tvSendCmd('vol_up'); }
  setTimeout(refreshTvOverlay, 300);
}
async function tvVolDown() {
  if (await _tvHasCap('volume_down')) await _tvSetCap('volume_down', true);
  else { _tvSendCmd('vol_down'); }
  setTimeout(refreshTvOverlay, 300);
}
async function tvVolSet(pct) {
  if (await _tvHasCap('volume_set')) await _tvSetCap('volume_set', Number(pct)/100);
  else _tvSendCmd('vol_' + Math.round(pct));
}
async function tvPlayPause() {
  if (await _tvHasCap('speaker_playing')) {
    const data = await _tvGetDetail(true);
    const cur = data && data.detail.capabilitiesObj.speaker_playing ? !!data.detail.capabilitiesObj.speaker_playing.value : false;
    await _tvSetCap('speaker_playing', !cur);
  } else _tvSendCmd('play_pause');
}
async function tvStop() { _tvSendCmd('stop'); }
async function tvNext() {
  if (await _tvHasCap('speaker_next')) await _tvSetCap('speaker_next', true);
  else _tvSendCmd('next');
}
async function tvPrev() {
  if (await _tvHasCap('speaker_prev')) await _tvSetCap('speaker_prev', true);
  else _tvSendCmd('prev');
}
// Channel/nav — fallback to variable (user maps to Android TV flow actions)
function tvChUp() { _tvSendCmd('channel_up'); }
function tvChDown() { _tvSendCmd('channel_down'); }
function tvUp() { _tvSendCmd('up'); }
function tvDown() { _tvSendCmd('down'); }
function tvLeft() { _tvSendCmd('left'); }
function tvRight() { _tvSendCmd('right'); }
function tvOk() { _tvSendCmd('ok'); }
function tvHome() { _tvSendCmd('home'); }
function tvBack() { _tvSendCmd('back'); }
function tvDigit(n) { _tvSendCmd('digit_' + n); }

async function _tvCurrentOn() {
  const data = await _tvGetDetail(true);
  if (!data) return false;
  const co = data.detail.capabilitiesObj || {};
  return co.onoff ? !!co.onoff.value : false;
}

async function refreshTvOverlay() {
  const info = document.getElementById('tvr-info');
  const slider = document.getElementById('tvr-vol-slider');
  const volTxt = document.getElementById('tvr-vol-txt');
  if (!info) return;
  try {
    const data = await _tvGetDetail(true);
    if (!data) { info.textContent = 'TV nenalezena'; return; }
    const co = data.detail.capabilitiesObj || {};
    const on = co.onoff ? co.onoff.value : null;
    const vol = co.volume_set ? Math.round((co.volume_set.value || 0) * 100) : null;
    const muted = co.volume_mute ? !!co.volume_mute.value : false;
    const playing = co.speaker_playing ? !!co.speaker_playing.value : null;
    info.innerHTML = 'Power: <strong>' + (on ? 'ON' : 'OFF') + '</strong>' +
      (vol !== null ? ' · Vol: <strong>' + vol + '%</strong>' : '') +
      (muted ? ' · 🔇 mute' : '') +
      (playing !== null ? ' · ' + (playing ? '▶ playing' : '⏸ paused') : '');
    if (slider && vol !== null) { slider.value = vol; if (volTxt) volTxt.textContent = vol + '%'; }
  } catch(e) { info.textContent = 'err: ' + e.message; }
}

function openTvRemote() {
  const body =
    '<div class="dd-card">' +
      '<div class="dd-label">Stav</div>' +
      '<div id="tvr-info" style="font-family:var(--mono);font-size:13px;">Načítám…</div>' +
    '</div>' +
    // Power + Mute
    '<div class="dd-card">' +
      '<div class="tvr-row tvr-row-2">' +
        '<div class="tvr-btn power" onclick="tvPower()">⏻ POWER</div>' +
        '<div class="tvr-btn" onclick="tvMute()">🔇 MUTE</div>' +
      '</div>' +
    '</div>' +
    // Volume
    '<div class="dd-card">' +
      '<div class="dd-label">Hlasitost</div>' +
      '<div class="tvr-row tvr-row-3" style="margin-bottom:10px;">' +
        '<div class="tvr-btn" onclick="tvVolDown()">🔉 −</div>' +
        '<div class="tvr-btn" onclick="tvMute()">🔇</div>' +
        '<div class="tvr-btn" onclick="tvVolUp()">🔊 +</div>' +
      '</div>' +
      '<div class="dd-slider-row">' +
        '<input type="range" id="tvr-vol-slider" min="0" max="100" value="30"' +
          ' oninput="document.getElementById(\\'tvr-vol-txt\\').textContent=this.value+\\'%\\'"' +
          ' onchange="tvVolSet(this.value)">' +
        '<div class="dd-sl-val" id="tvr-vol-txt">30%</div>' +
      '</div>' +
    '</div>' +
    // Playback
    '<div class="dd-card">' +
      '<div class="dd-label">Přehrávání</div>' +
      '<div class="tvr-row tvr-row-4">' +
        '<div class="tvr-btn" onclick="tvPrev()">⏮</div>' +
        '<div class="tvr-btn primary" onclick="tvPlayPause()">▶/⏸</div>' +
        '<div class="tvr-btn" onclick="tvStop()">⏹</div>' +
        '<div class="tvr-btn" onclick="tvNext()">⏭</div>' +
      '</div>' +
    '</div>' +
    // Channel
    '<div class="dd-card">' +
      '<div class="dd-label">Kanál</div>' +
      '<div class="tvr-row tvr-row-2">' +
        '<div class="tvr-btn" onclick="tvChDown()">CH −</div>' +
        '<div class="tvr-btn" onclick="tvChUp()">CH +</div>' +
      '</div>' +
    '</div>' +
    // D-pad
    '<div class="dd-card">' +
      '<div class="dd-label">Navigace</div>' +
      '<div class="tvr-dpad">' +
        '<div class="tvr-empty"></div>' +
        '<div class="tvr-btn arrow" onclick="tvUp()">▲</div>' +
        '<div class="tvr-empty"></div>' +
        '<div class="tvr-btn arrow" onclick="tvLeft()">◀</div>' +
        '<div class="tvr-btn ok" onclick="tvOk()">OK</div>' +
        '<div class="tvr-btn arrow" onclick="tvRight()">▶</div>' +
        '<div class="tvr-empty"></div>' +
        '<div class="tvr-btn arrow" onclick="tvDown()">▼</div>' +
        '<div class="tvr-empty"></div>' +
      '</div>' +
      '<div class="tvr-row tvr-row-2" style="margin-top:10px;">' +
        '<div class="tvr-btn" onclick="tvHome()">🏠 HOME</div>' +
        '<div class="tvr-btn" onclick="tvBack()">↩ BACK</div>' +
      '</div>' +
    '</div>' +
    // Numpad
    '<div class="dd-card">' +
      '<div class="dd-label">Číselnice</div>' +
      '<div class="tvr-numpad">' +
        '<div class="tvr-btn num" onclick="tvDigit(1)">1</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(2)">2</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(3)">3</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(4)">4</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(5)">5</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(6)">6</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(7)">7</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(8)">8</div>' +
        '<div class="tvr-btn num" onclick="tvDigit(9)">9</div>' +
        '<div class="tvr-empty"></div>' +
        '<div class="tvr-btn num" onclick="tvDigit(0)">0</div>' +
        '<div class="tvr-empty"></div>' +
      '</div>' +
    '</div>' +
    '<div class="dd-card">' +
      '<div class="dd-label">Info</div>' +
      '<div style="font-size:11px;color:var(--tx3);line-height:1.6;">' +
        '<strong>Power/Vol/Play</strong> jdou přímo na TV capabilities.<br>' +
        '<strong>Channel/Arrows/Home/Back/Numpad</strong> píšou do <code>sh_tv_remote_cmd</code> — ' +
        'vytvoř v Homey flow dispatcher (QUANDO cmd cambiata → Android TV flow action).' +
      '</div>' +
    '</div>';
  document.getElementById('ddIcon').textContent = '📺';
  document.getElementById('ddName').textContent = 'TV remote · Ložnice';
  document.getElementById('ddBody').innerHTML = body;
  document.getElementById('devDetailOverlay').classList.add('show');
  refreshTvOverlay();
}
// ══ END PHASE3 ═══════════════════════════════════════════════════════════

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
    is_crlf = '\r\n' in content[:4096]

    def apply_before(anchor, inject, label):
        nonlocal content
        inject2 = inject.replace('\n', '\r\n') if is_crlf else inject
        if anchor in content:
            content = content.replace(anchor, inject2 + anchor, 1)
            changes.append(label)
        else:
            changes.append('❌ ' + label + ' (anchor missing)')

    apply_before(ANCHOR_CSS, INJECT_CSS, 'CSS (.tvr-*)')
    apply_before(ANCHOR_TV_TILE, INJECT_TV_TILE, 'TV tile in bedroom')
    apply_before(ANCHOR_JS, INJECT_JS, 'JS helpers (openTvRemote + dispatch)')

    failed = [c for c in changes if c.startswith('❌')]
    if content != orig and not failed:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
        for c in changes:
            print(f"     + {c}")
    else:
        print(f"  ⚠️  PROBLEM: {os.path.basename(fp)}")
        for c in changes:
            print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 3 — TV remote overlay (bedroom)')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
