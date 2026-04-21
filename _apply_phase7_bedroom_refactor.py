"""
PHASE 7 — Bedroom zone no-scroll refactor

User feedback (po phase6b kuchyně refactor): stejně upravit ložnici.

CURRENT STATE (4 separátní sekce = scroll):
  1) "Zásuvky"      — grid (TV zasuvka, Zvlhčovač)
  2) "TV · Ovládání" — grid s 1 tile (TV remote)
  3) "Zvlhčovač"    — standalone card (redundant s #1)
  4) "Audio"        — static info card

REFACTOR (1 sekce, detaily v overlay):
  1) "Zásuvky & Ovládání" — unified grid (TV zasuvka · Zvlhčovač · TV remote)
  + small info note about audio (no standalone card)

CHANGES:
  - bplugs extended with rawName
  - TV remote tile přesunut do stejného gridu
  - Zvlhčovač standalone section REMOVED
  - Audio standalone section REPLACED with small inline note
  - openDeviceDetail: d.key === 'humidifier' → show auto-mode config + humidity sensor

Idempotent. Marker: PHASE7_BEDROOM_REFACTOR_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: Replace bedroom plugs + TV remote + Zvlhčovač + Audio into ONE grid
# ═══════════════════════════════════════════════════════════════════════════
OLD_BEDROOM_BLOCK = """  // Ložnice — zásuvky → tiles
  if (zone === 'bedroom') {
    const plugs = DATA?.plugs || {};
    const bplugs = [
      { key: 'tv',         label: 'TV zasuvka', icon: '📺' },
      { key: 'humidifier', label: 'Zvlhčovač',  icon: '💧' },
    ];
    const hasBedPlugData = bplugs.some(p => plugs[p.key]);
    if (hasBedPlugData) {
      html += '<div class="sect">Zásuvky</div><div class="dev-tiles">';
      bplugs.forEach(p => {
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

NEW_BEDROOM_BLOCK = """  // PHASE7_BEDROOM_REFACTOR_APPLIED — unified Zásuvky & Ovládání grid
  if (zone === 'bedroom') {
    const plugs = DATA?.plugs || {};
    const bplugs = [
      { key: 'tv',         label: 'TV zásuvka', icon: '🔌', rawName: 'TV zasuvka' },
      { key: 'humidifier', label: 'Zvlhčovač',  icon: '💧', rawName: 'Zvlhčovač1' },
    ];
    const hasBedPlugData = bplugs.some(p => plugs[p.key]);
    html += '<div class="sect">Zásuvky & Ovládání</div><div class="dev-tiles">';
    // Plug tiles
    if (hasBedPlugData) {
      bplugs.forEach(p => {
        const d = plugs[p.key];
        if (!d) return;
        const isOn = !!d.on;
        const powerW = d.power !== null && d.power !== undefined ? Math.round(d.power) : null;
        const tIdx = _tileData.length;
        _tileData.push({key:p.key, name:d.name||p.label, rawName:p.rawName, icon:p.icon, type:'plug', on:isOn,
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
    }
    // TV remote tile (in same grid)
    html += '<div class="dev-tile" id="bed-tv-tile" onclick="openTvRemote()">' +
      '<div class="tile-icon">📺</div>' +
      '<div class="tile-name">TV remote</div>' +
      '<div class="tile-state off" id="bed-tv-state">—</div>' +
    '</div>';
    html += '</div>';
    setTimeout(refreshTvTile, 120);
    // Small audio note (no standalone card)
    html += '<div style="font-size:10px;color:var(--tx3);padding:6px 10px;text-align:center;background:rgba(255,255,255,.03);border-radius:8px;margin-top:4px;">🔊 Audio (TTS, briefing, rádio) → přes reproduktor Kuchyň</div>';
  }"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: REMOVE Phase 3 TV remote standalone section
# ═══════════════════════════════════════════════════════════════════════════
OLD_PHASE3_TV_TILE = """  // PHASE3_TV_REMOTE_APPLIED — TV remote tile (bedroom)
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

NEW_PHASE3_TV_TILE = """  // PHASE7_BEDROOM_REFACTOR_APPLIED — TV remote tile moved to unified grid

"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 3: REMOVE Phase 2 Zvlhčovač standalone section
# ═══════════════════════════════════════════════════════════════════════════
OLD_PHASE2_HUM = """  // PHASE2_HUM_VACUUM_FRIDGE_APPLIED — Zvlhčovač panel (bedroom)
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

NEW_PHASE2_HUM = """  // PHASE7_BEDROOM_REFACTOR_APPLIED — Zvlhčovač panel moved to openDeviceDetail

"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 4: REMOVE Speaker bedroom note (static info card)
# ═══════════════════════════════════════════════════════════════════════════
OLD_AUDIO_CARD = """  // Speaker (bedroom — ZRUŠEN, vše přes Kuchyň)
  if (zone === 'bedroom') {
    html += '<div class="sect">Audio</div><div class="card">';
    html += '<div class="card-row"><span class="card-icon">🔊</span><span class="card-lbl">Veškeré audio (TTS, briefing, rádio) jde přes reproduktor Kuchyň</span></div>';
    html += '</div>';
  }

"""

NEW_AUDIO_CARD = """  // PHASE7_BEDROOM_REFACTOR_APPLIED — Audio note moved inline do unified grid

"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 5: Add openDeviceDetail conditional for d.key === 'humidifier'
# Anchor: PHASE6B purifier block start (same injection point)
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_DETAIL = "  // PHASE6B_KITCHEN_REFACTOR_APPLIED — Lednice sparkline in detail"

INJECT_DETAIL = """  // PHASE7_BEDROOM_REFACTOR_APPLIED — Zvlhčovač detail
  if (d.key === 'humidifier') {
    const roomHum = (DATA && DATA.rooms && DATA.rooms.bedroom && DATA.rooms.bedroom.humidity != null) ? DATA.rooms.bedroom.humidity : null;
    const humLow = Number((ALL_VARS && ALL_VARS['sh_cfg_humidity_low'] && ALL_VARS['sh_cfg_humidity_low'].value) || 30);
    const humHigh = Number((ALL_VARS && ALL_VARS['sh_cfg_humidity_high'] && ALL_VARS['sh_cfg_humidity_high'].value) || 45);
    html += '<div class="dd-card">' +
      '<div class="dd-label">Vlhkost v ložnici</div>' +
      '<div style="font-family:var(--mono);font-size:28px;font-weight:600;color:var(--cyan);padding:8px 0;">' +
        (roomHum !== null ? roomHum + '%' : '—') +
      '</div>' +
      '<div style="font-size:11px;color:var(--tx3);">Z senzoru Temperature and Humidity Sensor ložnice</div>' +
    '</div>' +
    '<div class="dd-card">' +
      '<div class="dd-label">Auto-režim (flow)</div>' +
      '<div style="font-size:13px;line-height:1.8;">' +
        '▶ Zapne pod <strong style="color:var(--green);">' + humLow + '%</strong> vlhkosti<br>' +
        '⏹ Vypne nad <strong style="color:var(--orange);">' + humHigh + '%</strong> vlhkosti' +
      '</div>' +
      '<div style="font-size:10px;color:var(--tx3);margin-top:8px;line-height:1.5;">' +
        'Editovatelné v CONFIG → Ložnice: sh_cfg_humidity_low · sh_cfg_humidity_high' +
      '</div>' +
    '</div>';
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

    def replace(old, new, label, marker=None):
        nonlocal content
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if marker and marker in content:
            changes.append('⏭ ' + label + ' (už applied)')
            return
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ ' + label)
        else:
            changes.append('⏭ ' + label + ' (anchor missing — pravděpodobně už applied)')

    replace(OLD_BEDROOM_BLOCK, NEW_BEDROOM_BLOCK, 'Unified Zásuvky & Ovládání grid',
            marker='PHASE7_BEDROOM_REFACTOR_APPLIED — unified Zásuvky & Ovládání')
    replace(OLD_PHASE3_TV_TILE, NEW_PHASE3_TV_TILE, 'Remove Phase 3 TV remote standalone',
            marker='PHASE7_BEDROOM_REFACTOR_APPLIED — TV remote tile moved')
    replace(OLD_PHASE2_HUM, NEW_PHASE2_HUM, 'Remove Phase 2 Zvlhčovač standalone',
            marker='PHASE7_BEDROOM_REFACTOR_APPLIED — Zvlhčovač panel moved')
    replace(OLD_AUDIO_CARD, NEW_AUDIO_CARD, 'Remove Audio static card',
            marker='PHASE7_BEDROOM_REFACTOR_APPLIED — Audio note moved')

    # Inject humidifier detail rendering
    if 'PHASE7_BEDROOM_REFACTOR_APPLIED — Zvlhčovač detail' in content:
        changes.append('⏭ Humidifier detail (už applied)')
    elif ANCHOR_DETAIL in content:
        inj = INJECT_DETAIL.replace('\n', '\r\n') if is_crlf else INJECT_DETAIL
        content = content.replace(ANCHOR_DETAIL, inj + ANCHOR_DETAIL, 1)
        changes.append('+ openDeviceDetail humidifier conditional')
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
    print('PHASE 7 — Bedroom no-scroll refactor')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
