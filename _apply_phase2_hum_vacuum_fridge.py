"""
PHASE 2 — Humidifier (bedroom) + Giuseppe vacuum (bathroom) + Fridge sparkline (kitchen)
Idempotent. Marker: PHASE2_HUM_VACUUM_FRIDGE_APPLIED.

ADDS:
  1) Zvlhčovač panel v ložnici (on/off + aktuální vlhkost + config thresholds)
  2) Giuseppe vysavač tile v koupelně (start/stop + battery)
  3) Lednice sparkline graf v kuchyni (60 samples, local storage)
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE2_HUM_VACUUM_FRIDGE_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 1: Kitchen Lednice sparkline — BEFORE "// Speaker (bathroom) → tile"
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_FRIDGE = "  // Speaker (bathroom) → tile"

INJECT_FRIDGE = """  // PHASE2_HUM_VACUUM_FRIDGE_APPLIED — Lednice power sparkline (kitchen)
  if (zone === 'kitchen') {
    const fridge = DATA && DATA.plugs && DATA.plugs.fridge;
    if (fridge && fridge.power != null) {
      const curW = Math.round(Number(fridge.power));
      const tempC = fridge.temp != null ? Math.round(Number(fridge.temp)) : null;
      html += '<div class="sect">Lednice — spotřeba</div><div class="card">';
      html += '<div class="card-row">' +
        '<span class="card-icon">🧊</span>' +
        '<span class="card-lbl">Aktuální: <strong>' + curW + ' W</strong>' +
        (tempC !== null ? ' · ' + tempC + '°C' : '') + '</span>' +
      '</div>';
      html += '<canvas id="fridge-spark" width="600" height="70" style="width:100%;height:70px;display:block;margin-top:8px;border-radius:8px;background:rgba(255,255,255,.03);"></canvas>';
      html += '<div style="display:flex;justify-content:space-between;font-size:10px;color:var(--tx3);font-family:var(--mono);margin-top:4px;">' +
        '<span id="fridge-spark-min">min —</span>' +
        '<span id="fridge-spark-avg">avg —</span>' +
        '<span id="fridge-spark-max">max —</span>' +
        '<span id="fridge-spark-samples">0 vzorků</span>' +
      '</div>';
      html += '</div>';
      setTimeout(function(){ _drawFridgeSpark(curW); }, 60);
    }
  }

"""

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 2: Bathroom Giuseppe vacuum — BEFORE "// Ložnice — zásuvky → tiles"
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_VACUUM = "  // Ložnice — zásuvky → tiles"

INJECT_VACUUM = """  // PHASE2_HUM_VACUUM_FRIDGE_APPLIED — Giuseppe vysavač (bathroom)
  if (zone === 'bathroom') {
    html += '<div class="sect">Giuseppe · vysavač</div><div class="card">';
    html += '<div class="card-row">' +
      '<span class="card-icon">🤖</span>' +
      '<span class="card-lbl" id="giuseppe-stav">Načítám…</span>' +
    '</div>';
    html += '<div class="divider"></div>' +
      '<div class="btn-row">' +
        '<div class="btn" onclick="giuseppeStart()">▶ Start úklid</div>' +
        '<div class="btn danger" onclick="giuseppeStop()">⏹ Stop</div>' +
        '<div class="btn" onclick="refreshGiuseppe()">↻ Obnovit</div>' +
      '</div>';
    html += '</div>';
    setTimeout(refreshGiuseppe, 80);
  }

"""

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 3: Bedroom Humidifier panel — BEFORE "// Speaker (bedroom — ZRUŠEN...)"
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_HUM = "  // Speaker (bedroom — ZRUŠEN, vše přes Kuchyň)"

INJECT_HUM = """  // PHASE2_HUM_VACUUM_FRIDGE_APPLIED — Zvlhčovač panel (bedroom)
  if (zone === 'bedroom') {
    const hum = DATA && DATA.plugs && DATA.plugs.humidifier;
    const roomHum = roomData && roomData.humidity != null ? roomData.humidity : null;
    const humLow = Number((ALL_VARS && ALL_VARS['sh_cfg_humidity_low'] && ALL_VARS['sh_cfg_humidity_low'].value) || 30);
    const humHigh = Number((ALL_VARS && ALL_VARS['sh_cfg_humidity_high'] && ALL_VARS['sh_cfg_humidity_high'].value) || 45);
    html += '<div class="sect">Zvlhčovač</div><div class="card">';
    html += '<div class="card-row">' +
      '<span class="card-icon">💧</span>' +
      '<span class="card-lbl">' +
        (hum ? 'Stav: <strong>' + (hum.on ? 'ON' : 'OFF') + '</strong>' +
          (hum.power != null ? ' · ' + Math.round(hum.power) + 'W' : '') : 'Zvlhčovač1 (data nedostupná)') +
        (roomHum !== null ? '<br><span style="font-size:11px;color:var(--tx2);">Vlhkost ložnice: <strong>' + roomHum + '%</strong></span>' : '') +
      '</span>' +
    '</div>';
    html += '<div class="divider"></div>' +
      '<div class="btn-row">' +
        '<div class="btn" onclick="setDeviceCap(\\'Zvlhčovač1\\',\\'onoff\\',true)">▶ Zapnout</div>' +
        '<div class="btn danger" onclick="setDeviceCap(\\'Zvlhčovač1\\',\\'onoff\\',false)">⏹ Vypnout</div>' +
      '</div>';
    html += '<div class="divider"></div>' +
      '<div style="font-size:11px;color:var(--tx3);line-height:1.6;">' +
        'Auto-režim (flow): zapne pod <strong>' + humLow + '%</strong>, vypne nad <strong>' + humHigh + '%</strong>.' +
      '</div>';
    html += '</div>';
  }

"""

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 4: JS helpers — before "function renderZoneDetail(zone) {"
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_JS = "let _tileData = [];"

INJECT_JS = """// ══ PHASE2_HUM_VACUUM_FRIDGE_APPLIED — helpers ═══════════════════════════

// ── Lednice sparkline ────────────────────────────────────────────────────
function _drawFridgeSpark(currentW) {
  let h = [];
  try { h = JSON.parse(localStorage.getItem('fridge_hist') || '[]'); } catch(_){}
  if (!Array.isArray(h)) h = [];
  const cur = Number(currentW);
  if (!isNaN(cur)) h.push({ t: Date.now(), w: cur });
  // Keep last 120 samples (~10 min if dashboard ticks every 5s)
  if (h.length > 120) h = h.slice(-120);
  try { localStorage.setItem('fridge_hist', JSON.stringify(h)); } catch(_){}

  const c = document.getElementById('fridge-spark');
  if (!c) return;
  const ctx = c.getContext('2d');
  const W = c.width, H = c.height;
  ctx.clearRect(0, 0, W, H);
  if (h.length < 2) {
    ctx.fillStyle = 'rgba(255,255,255,.3)';
    ctx.font = '11px sans-serif';
    ctx.fillText('Sbírám data… (první vzorek uložen)', 12, H/2 + 4);
    return;
  }
  const vals = h.map(x => x.w);
  const mn = Math.min(...vals);
  const mx = Math.max(...vals);
  const avg = vals.reduce((a,b)=>a+b,0) / vals.length;
  const span = (mx - mn) || 1;
  const pad = 4;
  // Grid lines
  ctx.strokeStyle = 'rgba(255,255,255,.06)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 2; i++) {
    const y = pad + ((H - 2*pad) * i / 2);
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }
  // Line
  ctx.strokeStyle = '#64f4d8';
  ctx.lineWidth = 2;
  ctx.beginPath();
  h.forEach((p, i) => {
    const x = (i / (h.length - 1)) * W;
    const y = H - pad - ((p.w - mn) / span) * (H - 2*pad);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
  // Fill area under line
  ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath();
  ctx.fillStyle = 'rgba(100,244,216,.12)';
  ctx.fill();
  // Update labels
  const setTxt = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
  setTxt('fridge-spark-min', 'min ' + Math.round(mn) + 'W');
  setTxt('fridge-spark-avg', 'avg ' + Math.round(avg) + 'W');
  setTxt('fridge-spark-max', 'max ' + Math.round(mx) + 'W');
  setTxt('fridge-spark-samples', h.length + ' vzorků');
}

// ── Giuseppe (bathroom vacuum) ───────────────────────────────────────────
async function _findGiuseppeDevice() {
  if (typeof varMapLoaded !== 'undefined' && !varMapLoaded) await loadVarMap();
  if (ALL_DEVICES && ALL_DEVICES['Giuseppe']) return { name: 'Giuseppe', ...ALL_DEVICES['Giuseppe'] };
  if (ALL_DEVICES) {
    for (const [k, v] of Object.entries(ALL_DEVICES)) {
      if (k.trim().toLowerCase() === 'giuseppe') return { name: k, ...v };
    }
  }
  try {
    const all = await apiGet('/api/manager/devices/device/');
    for (const [id, d] of Object.entries(all || {})) {
      if (String(d.name || '').trim().toLowerCase() === 'giuseppe') {
        if (ALL_DEVICES) ALL_DEVICES[d.name] = { id, caps: d.capabilities || [] };
        return { name: d.name, id, caps: d.capabilities || [] };
      }
    }
  } catch(_){}
  return null;
}

async function refreshGiuseppe() {
  const el = document.getElementById('giuseppe-stav');
  if (!el) return;
  try {
    const d = await _findGiuseppeDevice();
    if (!d) { el.innerHTML = 'Zařízení "Giuseppe" nenalezeno'; return; }
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const co = detail.capabilitiesObj || {};
    const on = co.onoff ? co.onoff.value : null;
    const bat = co.measure_battery && co.measure_battery.value != null ? Math.round(co.measure_battery.value) + '%' : '—';
    const avail = detail.available === false ? '❌ offline' : '✅ online';
    el.innerHTML = 'Stav: <strong>' + (on === true ? 'UKLÍZÍ' : on === false ? 'stojí' : '—') + '</strong>' +
      ' · Baterie: <strong>' + bat + '</strong> · ' + avail;
  } catch(e) { el.textContent = 'err: ' + e.message; }
}

async function giuseppeStart() {
  try {
    const d = await _findGiuseppeDevice();
    if (!d) { try { flash('⚠ Giuseppe nenalezen'); } catch(_){}; return; }
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/onoff', { value: true });
    try { flash('▶ Giuseppe start cleaning'); } catch(_){}
    setTimeout(refreshGiuseppe, 500);
  } catch(e) { try { flash('✗ ' + e.message); } catch(_){} }
}

async function giuseppeStop() {
  try {
    const d = await _findGiuseppeDevice();
    if (!d) { try { flash('⚠ Giuseppe nenalezen'); } catch(_){}; return; }
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/onoff', { value: false });
    try { flash('⏹ Giuseppe stop'); } catch(_){}
    setTimeout(refreshGiuseppe, 500);
  } catch(e) { try { flash('✗ ' + e.message); } catch(_){} }
}

// ══ END PHASE2 ═══════════════════════════════════════════════════════════

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
        if is_crlf:
            inject2 = inject.replace('\n', '\r\n')
        else:
            inject2 = inject
        if anchor in content:
            content = content.replace(anchor, inject2 + anchor, 1)
            changes.append(label)
        else:
            changes.append('❌ ' + label + ' (anchor not found)')

    apply_before(ANCHOR_FRIDGE, INJECT_FRIDGE, 'Lednice sparkline (kitchen)')
    apply_before(ANCHOR_VACUUM, INJECT_VACUUM, 'Giuseppe vysavač (bathroom)')
    apply_before(ANCHOR_HUM, INJECT_HUM, 'Zvlhčovač panel (bedroom)')
    apply_before(ANCHOR_JS, INJECT_JS, 'JS helpers (sparkline, giuseppe)')

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
    print('PHASE 2 — Humidifier + Giuseppe + Fridge sparkline')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
