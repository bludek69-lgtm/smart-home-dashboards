"""
PHASE 6b — Refactor kitchen layout (no scroll)

User feedback:
  1) Čistička = spotřebič (jako trouba/mikrovlnka) — zařadit do Spotřebiče kartu
  2) Lednice graf → přímo do device detail (klik na Lednice tile otevře overlay s grafem)
  3) Eliminovat scroll v kuchyni

CHANGES:
  1) REMOVE Phase 6 standalone "Čistička vzduchu" section
  2) REMOVE Phase 2 standalone "Lednice — spotřeba" section
  3) EXTEND kplugs array (Trouba/Mikro/Lednice/Kávovar) + Čistička
  4) EXTEND openDeviceDetail:
     - key === 'fridge'   → power sparkline card
     - key === 'purifier' → PM2.5 + temp + hum + guard toggle + ON/OFF actions
  5) kplugs entries now carry rawName (Homey device name) pro správné API calls

Idempotent. Marker: PHASE6B_KITCHEN_REFACTOR_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: Replace kplugs block — add purifier, rawName, appliances fallback
# ═══════════════════════════════════════════════════════════════════════════
OLD_KPLUGS = """  // Kitchen plugs monitoring → tiles
  if (zone === 'kitchen') {
    const plugs = DATA?.plugs || {};
    const kplugs = [
      { key: 'oven',    label: 'Trouba',     icon: '🍞' },
      { key: 'micro',   label: 'Mikrovlnka', icon: '📡' },
      { key: 'fridge',  label: 'Lednice',    icon: '🧊' },
      { key: 'coffee',  label: 'Kávovar',    icon: '☕' },
    ];
    const hasPlugData = kplugs.some(p => plugs[p.key]);
    if (hasPlugData) {
      html += '<div class="sect">Spotřebiče</div><div class="dev-tiles">';
      kplugs.forEach(p => {
        const d = plugs[p.key];
        if (!d) return;
        const isOn = !!d.on;
        const powerW = d.power !== null && d.power !== undefined ? Math.round(d.power) : null;
        const tIdx = _tileData.length;
        _tileData.push({key:p.key, name:d.name||p.label, icon:p.icon, type:'plug', on:isOn,
          dim:null, hasDim:false, hasTemp:false, temp:null,
          power:d.power!==undefined?d.power:null, plugTemp:d.temp!==undefined?d.temp:null});
        const hasCfg = (DEVICE_CFG[p.key] || []).length > 0;
      html += '<div class="dev-tile' + (isOn ? ' tile-on' : '') + '" onclick="openDeviceDetail(_tileData[' + tIdx + '])">' +
          (hasCfg ? '<div class="tile-cfg">⚙</div>' : '') +
          '<div class="tile-icon">' + p.icon + '</div>' +
          '<div class="tile-name">' + p.label + '</div>' +
          '<div class="tile-state ' + (isOn ? 'on' : 'off') + '">' + (isOn ? (powerW !== null ? powerW+'W' : 'ON') : 'OFF') + '</div>' +
          '</div>';
      });
      html += '</div>';
    }
  }"""

NEW_KPLUGS = """  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Spotřebiče v kitchen (+ purifier)
  if (zone === 'kitchen') {
    const plugs = DATA?.plugs || {};
    const app = DATA?.appliances || {};
    const kplugs = [
      { key: 'oven',     label: 'Trouba',     icon: '🍞', rawName: 'Forno ad aria calda' },
      { key: 'micro',    label: 'Mikrovlnka', icon: '📡', rawName: 'Mikrovlnka' },
      { key: 'fridge',   label: 'Lednice',    icon: '🧊', rawName: 'Lednice' },
      { key: 'coffee',   label: 'Kávovar',    icon: '☕', rawName: 'Zasuvka Kaffe' },
      { key: 'purifier', label: 'Čistička',   icon: '🌬', rawName: 'Air Purifier 4 Lite' },
    ];
    const hasPlugData = kplugs.some(p => plugs[p.key] || app[p.key]);
    if (hasPlugData) {
      html += '<div class="sect">Spotřebiče</div><div class="dev-tiles">';
      kplugs.forEach(p => {
        const d = plugs[p.key] || app[p.key];
        if (!d) return;
        const isOn = !!d.on;
        const powerW = d.power !== null && d.power !== undefined ? Math.round(d.power) : null;
        const pm25 = (p.key === 'purifier' && d.pm25 != null) ? Math.round(Number(d.pm25)) : null;
        const tIdx = _tileData.length;
        _tileData.push({key:p.key, name:d.name||p.label, rawName:p.rawName, icon:p.icon, type:'plug', on:isOn,
          dim:null, hasDim:false, hasTemp:false, temp:null,
          power:d.power!==undefined?d.power:null, plugTemp:d.temp!==undefined?d.temp:null,
          pm25: pm25, humidity: d.humidity !== undefined ? d.humidity : null});
        const hasCfg = (DEVICE_CFG[p.key] || []).length > 0;
        // Tile state: purifier → PM2.5, jinak W nebo ON
        let stateStr;
        if (!isOn) stateStr = 'OFF';
        else if (pm25 !== null) stateStr = pm25 + ' μg';
        else if (powerW !== null) stateStr = powerW + 'W';
        else stateStr = 'ON';
        const stateCls = (pm25 !== null && pm25 > 120) ? 'warn' : (isOn ? 'on' : 'off');
        html += '<div class="dev-tile' + (isOn ? ' tile-on' : '') + '" onclick="openDeviceDetail(_tileData[' + tIdx + '])">' +
          (hasCfg ? '<div class="tile-cfg">⚙</div>' : '') +
          '<div class="tile-icon">' + p.icon + '</div>' +
          '<div class="tile-name">' + p.label + '</div>' +
          '<div class="tile-state ' + stateCls + '">' + stateStr + '</div>' +
          '</div>';
      });
      html += '</div>';
    }
  }"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: REMOVE Phase 6 standalone Čistička section
# ═══════════════════════════════════════════════════════════════════════════
OLD_PHASE6_BLOCK = """  // PHASE6_AIR_PURIFIER_APPLIED — Čistička vzduchu panel (kitchen)
  if (zone === 'kitchen') {
    html += '<div class="sect">Čistička vzduchu</div><div class="card">';
    html += '<div class="card-row">' +
      '<span class="card-icon">🌬</span>' +
      '<span class="card-lbl" id="purifier-stav">Načítám…</span>' +
    '</div>';
    html += '<div class="divider"></div>' +
      '<div class="btn-row">' +
        '<div class="btn" onclick="togglePurifierDevice(true)">▶ Zapnout</div>' +
        '<div class="btn danger" onclick="togglePurifierDevice(false)">⏹ Vypnout</div>' +
        '<div class="btn" onclick="refreshPurifier()">↻ Obnovit</div>' +
      '</div>';
    html += '<div class="divider"></div>' +
      '<div class="tog-row" style="padding:4px 0;">' +
        '<span class="card-icon">🫁</span>' +
        '<span class="tog-lbl" title="sh_air_purifier_guard_enabled — při OFF čistička běží manuálně podle PM2.5 auto režimu">Automatický režim (PM2.5)</span>' +
        '<div class="toggle" id="tog-purifier-kitchen" onclick="togglePurifierGuard(this)"></div>' +
      '</div>';
    html += '</div>';
    setTimeout(function() {
      refreshPurifier();
      // Sync toggle z existujícího ALL_VARS state
      try {
        const v = String((ALL_VARS||{})['sh_air_purifier_guard_enabled']?.value || 'yes').trim().toLowerCase();
        const t = document.getElementById('tog-purifier-kitchen');
        if (t) t.classList.toggle('on', v === 'yes' || v === 'true' || v === 'on');
      } catch(_){}
    }, 80);
  }

"""

NEW_PHASE6_BLOCK = """  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Čistička moved to Spotřebiče tile (openDeviceDetail)

"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 3: REMOVE Phase 2 standalone Lednice sparkline section
# ═══════════════════════════════════════════════════════════════════════════
OLD_PHASE2_FRIDGE_BLOCK = """  // PHASE2_HUM_VACUUM_FRIDGE_APPLIED — Lednice power sparkline (kitchen)
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

NEW_PHASE2_FRIDGE_BLOCK = """  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Lednice sparkline moved to openDeviceDetail

"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 4: Add conditional rendering in openDeviceDetail for fridge + purifier
# Anchor: " // Power & temperature (plugs)" — existing plug monitoring block
# Inject BEFORE to catch fridge/purifier specifically
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_DETAIL = "  // Power & temperature (plugs)"

INJECT_DETAIL = """  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Lednice sparkline in detail
  if (d.key === 'fridge') {
    const curW = d.power !== null && d.power !== undefined ? Math.round(d.power) : 0;
    html += '<div class="dd-card">' +
      '<div class="dd-label">Spotřeba v čase</div>' +
      '<canvas id="fridge-spark" width="600" height="80" style="width:100%;height:80px;display:block;margin-top:4px;border-radius:8px;background:rgba(255,255,255,.03);"></canvas>' +
      '<div style="display:flex;justify-content:space-between;font-size:10px;color:var(--tx3);font-family:var(--mono);margin-top:6px;">' +
        '<span id="fridge-spark-min">min —</span>' +
        '<span id="fridge-spark-avg">avg —</span>' +
        '<span id="fridge-spark-max">max —</span>' +
        '<span id="fridge-spark-samples">0 vzorků</span>' +
      '</div>' +
    '</div>';
    setTimeout(function(){ _drawFridgeSpark(curW); }, 60);
  }

  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Čistička ovládání v detail
  if (d.key === 'purifier') {
    html += '<div class="dd-card">' +
      '<div class="dd-label">Stav čističky (live)</div>' +
      '<div id="purifier-stav" style="font-family:var(--mono);font-size:13px;line-height:1.6;">Načítám…</div>' +
      '<div class="divider"></div>' +
      '<div class="btn" onclick="refreshPurifier()" style="margin-top:6px;">↻ Obnovit</div>' +
    '</div>' +
    '<div class="dd-card">' +
      '<div class="dd-label">Automatický režim (PM2.5)</div>' +
      '<div class="tog-row" style="padding:4px 0;">' +
        '<span class="card-icon">🫁</span>' +
        '<span class="tog-lbl" title="sh_air_purifier_guard_enabled — při OFF čistička běží jen podle tlačítka ZAP/VYP">Hlídání PM2.5 (sh_air_purifier_router_v1)</span>' +
        '<div class="toggle" id="tog-purifier-kitchen" onclick="togglePurifierGuard(this)"></div>' +
      '</div>' +
      '<div style="font-size:10px;color:var(--tx3);margin-top:6px;line-height:1.5;">' +
        'ON = router řídí dle PM2.5. OFF = jen manuální ovládání.' +
      '</div>' +
    '</div>';
    setTimeout(function() {
      refreshPurifier();
      try {
        const v = String((ALL_VARS||{})['sh_air_purifier_guard_enabled']?.value || 'yes').trim().toLowerCase();
        const t = document.getElementById('tog-purifier-kitchen');
        if (t) t.classList.toggle('on', v === 'yes' || v === 'true' || v === 'on');
      } catch(_){}
    }, 80);
  }

"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    orig = content
    changes = []
    is_crlf = '\r\n' in content[:4096]

    def replace(old, new, label):
        nonlocal content
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ ' + label)
        else:
            changes.append('⏭ ' + label + ' (není, zřejmě už aplikováno)')

    # 1. kplugs extension
    if 'PHASE6B_KITCHEN_REFACTOR_APPLIED — Spotřebiče v kitchen' in content:
        changes.append('⏭ kplugs (už applied)')
    else:
        replace(OLD_KPLUGS, NEW_KPLUGS, 'kplugs (+ purifier, rawName, appliances fallback)')

    # 2. Remove Phase 6 standalone
    replace(OLD_PHASE6_BLOCK, NEW_PHASE6_BLOCK, 'Remove Phase 6 standalone Čistička section')

    # 3. Remove Phase 2 Lednice standalone
    replace(OLD_PHASE2_FRIDGE_BLOCK, NEW_PHASE2_FRIDGE_BLOCK, 'Remove Phase 2 standalone Lednice section')

    # 4. Inject detail overlay rendering
    if 'PHASE6B_KITCHEN_REFACTOR_APPLIED — Lednice sparkline in detail' in content:
        changes.append('⏭ openDeviceDetail fridge/purifier (už applied)')
    elif ANCHOR_DETAIL in content:
        inj = INJECT_DETAIL.replace('\n', '\r\n') if is_crlf else INJECT_DETAIL
        content = content.replace(ANCHOR_DETAIL, inj + ANCHOR_DETAIL, 1)
        changes.append('+ openDeviceDetail conditionals (fridge sparkline + purifier controls)')
    else:
        changes.append('❌ openDeviceDetail anchor nenalezen')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 6b — Kitchen layout refactor (no scroll)')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
