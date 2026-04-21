"""
PHASE 10 — Tooltipy všude + rozšířené device ikony v home page zónách

USER:
  1) "při najeti na ikonu myší někde funguje napověda někde ne — oprav všude"
  2) "přidej na home stránce ikony zařízení do zón"

FIXES:
  A) roomInds() — každá .ri ikonka dostane title= s názvem device + stavem
     (Sektorka1 · ON, Zvlhčovač · OFF · 0W, atd.)
  B) updateRoomFloor() — napojit DATA.plugs pro všechny zóny (HOME_ZONES config)
  C) JS-generované dev-tile v renderZoneDetail dostanou title
  D) Home page hd-tile dostane title
  E) Zone cards `.zone-card` title rozšířen o device counts

Idempotent. Marker: PHASE10_TOOLTIPS_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: roomInds() — add title tooltips to all indicator spans
# ═══════════════════════════════════════════════════════════════════════════
OLD_ROOMINDS = """function roomInds(data) {
  if (!data) return '<span class="ri off">—</span>';
  const parts = [];
  const deviceIcon = (key) => {
    if (DEVICE_DISPLAY[key]) return DEVICE_DISPLAY[key].icon;
    const k = key.toLowerCase();
    if (k.includes('plug') || k.includes('boiler') || k.includes('office')) return '🔌';
    if (k.includes('strip')) return '🎗';
    if (k.includes('lampicka') || k.includes('lamp')) return '🛋';
    if (k.includes('e14')) return '💡';
    if (k.includes('light')) return '💡';
    if (k.includes('fan') || k.includes('digestor')) return '🌀';
    if (k.includes('purifier')) return '🌬';
    if (k.includes('humidifier')) return '💧';
    if (k.includes('tv')) return '📺';
    return '💡';
  };
  for (const [k, v] of Object.entries(data)) {
    if (v && typeof v === 'object' && 'on' in v) {
      parts.push('<span class="ri ' + (v.on ? 'on' : 'off') + '">' + deviceIcon(k) + '</span>');
    }
  }
  if (data.speaker_playing) parts.push('<span class="ri aud">🔊</span>');
  if ('lux' in data && data.lux !== null) parts.push('<span class="ri"><span class="ri-txt">' + Math.round(data.lux) + 'lx</span></span>');
  if ('temp' in data && data.temp !== null) parts.push('<span class="ri"><span class="ri-txt">' + data.temp + '°</span></span>');
  if (data.blind) parts.push('<span class="ri">▬<span class="ri-txt">' + Math.round((data.blind.position||0)*100) + '%</span></span>');
  if ('window' in data) parts.push('<span class="ri ' + (data.window ? 'warn' : 'off') + '">🪟</span>');
  return parts.join('') || '';
}"""

NEW_ROOMINDS = """// PHASE10_TOOLTIPS_APPLIED — každý indicator má title tooltip
function roomInds(data) {
  if (!data) return '<span class="ri off" title="Žádná data">—</span>';
  const parts = [];
  const deviceIcon = (key) => {
    if (DEVICE_DISPLAY[key]) return DEVICE_DISPLAY[key].icon;
    const k = key.toLowerCase();
    if (k.includes('plug') || k.includes('boiler') || k.includes('office')) return '🔌';
    if (k.includes('strip')) return '🎗';
    if (k.includes('lampicka') || k.includes('lamp')) return '🛋';
    if (k.includes('e14')) return '💡';
    if (k.includes('light')) return '💡';
    if (k.includes('fan') || k.includes('digestor')) return '🌀';
    if (k.includes('purifier')) return '🌬';
    if (k.includes('humidifier')) return '💧';
    if (k.includes('tv')) return '📺';
    if (k.includes('fridge') || k.includes('lednice')) return '🧊';
    if (k.includes('oven') || k.includes('trouba')) return '🍞';
    if (k.includes('micro') || k.includes('mikro')) return '📡';
    if (k.includes('coffee') || k.includes('kaffe') || k.includes('kávovar')) return '☕';
    return '💡';
  };
  const deviceLabel = (key, v) => {
    const label = (v && v.name) ? v.name : key.replace(/_/g,' ');
    const state = v.on ? 'ZAP' : 'VYP';
    let extra = '';
    if (v.dim !== undefined && v.dim !== null) extra += ' · ' + Math.round(v.dim * 100) + '%';
    if (v.power !== undefined && v.power !== null) extra += ' · ' + Math.round(v.power) + 'W';
    if (v.temp !== undefined && v.temp !== null && typeof v.temp === 'number') extra += ' · ' + Math.round(v.temp) + '°C';
    return label + ' · ' + state + extra;
  };
  for (const [k, v] of Object.entries(data)) {
    if (v && typeof v === 'object' && 'on' in v) {
      const tooltip = deviceLabel(k, v);
      parts.push('<span class="ri ' + (v.on ? 'on' : 'off') + '" title="' + tooltip.replace(/"/g,'&quot;') + '">' + deviceIcon(k) + '</span>');
    }
  }
  if (data.speaker_playing) parts.push('<span class="ri aud" title="Reproduktor hraje">🔊</span>');
  if ('lux' in data && data.lux !== null) parts.push('<span class="ri" title="Osvětlení ' + Math.round(data.lux) + ' lux"><span class="ri-txt">' + Math.round(data.lux) + 'lx</span></span>');
  if ('temp' in data && data.temp !== null) parts.push('<span class="ri" title="Teplota ' + data.temp + '°C"><span class="ri-txt">' + data.temp + '°</span></span>');
  if ('humidity' in data && data.humidity !== null) parts.push('<span class="ri" title="Vlhkost ' + data.humidity + '%"><span class="ri-txt">' + data.humidity + '%</span></span>');
  if ('motion' in data) parts.push('<span class="ri ' + (data.motion ? 'on' : 'off') + '" title="Pohyb: ' + (data.motion ? 'detekován' : 'klid') + '">🚶</span>');
  if ('presence' in data) parts.push('<span class="ri ' + (data.presence ? 'on' : 'off') + '" title="Přítomnost: ' + (data.presence ? 'ANO' : 'NE') + '">👁</span>');
  if (data.blind) parts.push('<span class="ri" title="Roleta Fyrtur1 · ' + Math.round((data.blind.position||0)*100) + '%">▬<span class="ri-txt">' + Math.round((data.blind.position||0)*100) + '%</span></span>');
  if ('window' in data) parts.push('<span class="ri ' + (data.window ? 'warn' : 'off') + '" title="Okno: ' + (data.window ? 'OTEVŘENO' : 'zavřeno') + '">🪟</span>');
  return parts.join('') || '';
}"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH B: updateRoomFloor receives plugs from DATA.plugs for all zones
# ═══════════════════════════════════════════════════════════════════════════
OLD_UPDATE_ALL = """  updateRoomFloor('jidelna',  r.jidelna);
  updateRoomFloor('kitchen',  kitchenWithPlugs);
  updateRoomFloor('bedroom',  r.bedroom);
  updateRoomFloor('bathroom', r.bathroom);
  updateRoomFloor('pracovna', r.pracovna);"""

NEW_UPDATE_ALL = """  // PHASE10_TOOLTIPS_APPLIED — mergni plugs do každé zóny (více ikon v home floor grid)
  const mergePlugs = (zd, plugKeys) => {
    const merged = Object.assign({}, zd || {});
    (plugKeys || []).forEach(pk => { if (d.plugs && d.plugs[pk]) merged[pk] = d.plugs[pk]; });
    return merged;
  };
  updateRoomFloor('jidelna',  r.jidelna);
  updateRoomFloor('kitchen',  kitchenWithPlugs);
  updateRoomFloor('bedroom',  mergePlugs(r.bedroom, ['tv','humidifier']));
  updateRoomFloor('bathroom', r.bathroom);
  updateRoomFloor('pracovna', mergePlugs(r.pracovna, ['office']));"""

# Same for zone cards
OLD_ZONE_CARDS = """  updateZoneCard('pracovna', r.pracovna);"""
NEW_ZONE_CARDS = """  updateZoneCard('pracovna', mergePlugs(r.pracovna, ['office']));"""

# Bedroom zone card too
OLD_BEDROOM_ZC = """  updateZoneCard('bedroom',  r.bedroom);"""
NEW_BEDROOM_ZC = """  updateZoneCard('bedroom',  mergePlugs(r.bedroom, ['tv','humidifier']));"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH C: Add title to dev-tile generation in renderZoneDetail
# We target the main dev-tile template (renderDeviceSection)
# ═══════════════════════════════════════════════════════════════════════════
OLD_DEV_TILE = """      out += '<div class="dev-tile' + (isOn ? ' tile-on' : '') + '" onclick="openDeviceDetail(_tileData[' + tIdx + '])">' +
        (hasCfg ? '<div class="tile-cfg">⚙</div>' : '') +
        '<div class="tile-icon">' + dd.icon + '</div>' +
        '<div class="tile-name">' + devName + '</div>' +
        '<div class="tile-state ' + (isOn ? 'on' : 'off') + '">' + (isOn ? (hasDim ? dimVal+'%' : 'ON') : 'OFF') + '</div>' +
        (hasDim && isOn ? '<div class="tile-dim"><div class="tile-dim-fill" style="width:'+dimVal+'%"></div></div>' : '') +
        '</div>';"""

NEW_DEV_TILE = """      const tileTooltip = devName + ' · ' + (isOn ? 'ZAP' : 'VYP') + (hasDim && isOn ? ' · ' + dimVal + '%' : '') + ' · klikni pro detail';
      out += '<div class="dev-tile' + (isOn ? ' tile-on' : '') + '" onclick="openDeviceDetail(_tileData[' + tIdx + '])" title="' + tileTooltip.replace(/"/g,'&quot;') + '">' +
        (hasCfg ? '<div class="tile-cfg" title="Dostupná konfigurace">⚙</div>' : '') +
        '<div class="tile-icon">' + dd.icon + '</div>' +
        '<div class="tile-name">' + devName + '</div>' +
        '<div class="tile-state ' + (isOn ? 'on' : 'off') + '">' + (isOn ? (hasDim ? dimVal+'%' : 'ON') : 'OFF') + '</div>' +
        (hasDim && isOn ? '<div class="tile-dim"><div class="tile-dim-fill" style="width:'+dimVal+'%"></div></div>' : '') +
        '</div>';"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH D: hd-tile (home devices) — add title
# ═══════════════════════════════════════════════════════════════════════════
OLD_HD_TILE = """      html += '<div class="hd-tile' + (isOn ? ' hd-on' : '') + '" onclick="openDeviceDetail(_tileData[' + tIdx + '])">' +
        '<div class="hd-icon">' + dd.icon + '</div>' +
        '<div class="hd-name">' + nm + '</div>' +
        '<div class="hd-val ' + (isOn ? 'on' : 'off') + '">' + (isOn ? (dimVal !== null ? dimVal+'%' : 'ON') : 'OFF') + '</div>' +
      '</div>';"""

NEW_HD_TILE = """      const hdTipRoom = nm + ' · ' + (isOn ? 'ZAP' : 'VYP') + (dimVal !== null && isOn ? ' · ' + dimVal + '%' : '') + ' · klikni pro detail';
      html += '<div class="hd-tile' + (isOn ? ' hd-on' : '') + '" onclick="openDeviceDetail(_tileData[' + tIdx + '])" title="' + hdTipRoom.replace(/"/g,'&quot;') + '">' +
        '<div class="hd-icon">' + dd.icon + '</div>' +
        '<div class="hd-name">' + nm + '</div>' +
        '<div class="hd-val ' + (isOn ? 'on' : 'off') + '">' + (isOn ? (dimVal !== null ? dimVal+'%' : 'ON') : 'OFF') + '</div>' +
      '</div>';"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH E: Add title to room floor-grid elements themselves + CSS cursor hint
# (already have onclick, add title with zone name + count)
# ═══════════════════════════════════════════════════════════════════════════
OLD_UPDATE_FN = """function updateRoomFloor(id, ...sources) {
  const el = document.getElementById('ri-' + id);
  if (!el) return;
  const data = Object.assign({}, ...sources.filter(Boolean));
  el.innerHTML = roomInds(data);
  const fr = document.getElementById('fr-' + id);
  if (fr) {
    const hasLight = Object.values(data).some(v => v && typeof v === 'object' && v.on === true);
    fr.classList.toggle('lit', hasLight);
  }
}"""

NEW_UPDATE_FN = """function updateRoomFloor(id, ...sources) {
  const el = document.getElementById('ri-' + id);
  if (!el) return;
  const data = Object.assign({}, ...sources.filter(Boolean));
  el.innerHTML = roomInds(data);
  const fr = document.getElementById('fr-' + id);
  if (fr) {
    const devs = Object.entries(data).filter(([k,v]) => v && typeof v === 'object' && 'on' in v);
    const hasLight = devs.some(([k,v]) => v.on === true);
    fr.classList.toggle('lit', hasLight);
    // PHASE10_TOOLTIPS_APPLIED — tooltip na celé zóně
    const zoneNames = {jidelna:'Jídelna',kitchen:'Kuchyně',bedroom:'Ložnice',bathroom:'Koupelna',pracovna:'Pracovna',pradelna:'Prádelna',predsin:'Předsíň',toilet:'Toaleta',spolecne:'Společné'};
    const onCount = devs.filter(([k,v]) => v.on === true).length;
    const totalCount = devs.length;
    const tempStr = data.temp !== undefined && data.temp !== null ? ' · ' + data.temp + '°C' : '';
    const luxStr = data.lux !== undefined && data.lux !== null ? ' · ' + Math.round(data.lux) + 'lx' : '';
    fr.title = (zoneNames[id] || id) + ' · ' + onCount + '/' + totalCount + ' zap' + tempStr + luxStr + ' · klikni pro detail';
  }
}"""

OLD_ZONE_CARD_FN = """function updateZoneCard(id, data) {
  const el = document.getElementById('zci-' + id);
  if (!el) return;
  el.innerHTML = roomInds(data || {});
  const card = document.getElementById('zc-' + id);
  if (card) {
    const hasLight = Object.values(data || {}).some(v => v && typeof v === 'object' && v.on === true);
    card.classList.toggle('lit', hasLight);
    card.classList.toggle('aud', !!(data?.speaker_playing));
    // Update meta text
    const meta = card.querySelector('.zc-meta');
    if (meta && data?.temp !== undefined) meta.textContent = data.temp + '°C' + (data.humidity ? ' · ' + data.humidity + '%' : '');
  }
}"""

NEW_ZONE_CARD_FN = """function updateZoneCard(id, data) {
  const el = document.getElementById('zci-' + id);
  if (!el) return;
  el.innerHTML = roomInds(data || {});
  const card = document.getElementById('zc-' + id);
  if (card) {
    const devs = Object.entries(data || {}).filter(([k,v]) => v && typeof v === 'object' && 'on' in v);
    const hasLight = devs.some(([k,v]) => v.on === true);
    card.classList.toggle('lit', hasLight);
    card.classList.toggle('aud', !!(data?.speaker_playing));
    // Update meta text
    const meta = card.querySelector('.zc-meta');
    if (meta && data?.temp !== undefined) meta.textContent = data.temp + '°C' + (data.humidity ? ' · ' + data.humidity + '%' : '');
    // PHASE10_TOOLTIPS_APPLIED — tooltip
    const zoneNames = {jidelna:'Jídelna',kitchen:'Kuchyně',bedroom:'Ložnice',bathroom:'Koupelna',pracovna:'Pracovna',pradelna:'Prádelna',predsin:'Předsíň',toilet:'Toaleta',spolecne:'Společné'};
    const onCount = devs.filter(([k,v]) => v.on === true).length;
    card.title = (zoneNames[id] || id) + ' · ' + onCount + '/' + devs.length + ' zařízení zapnuto · klikni pro detail';
  }
}"""


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
        if marker and marker in content:
            changes.append('⏭ ' + label + ' (už applied)')
            return
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ ' + label)
        else:
            changes.append('⏭ ' + label + ' (anchor missing)')

    # A. roomInds
    replace(OLD_ROOMINDS, NEW_ROOMINDS, 'roomInds() s tooltips + motion/presence/humidity',
            marker='PHASE10_TOOLTIPS_APPLIED — každý indicator')

    # B. updateRoomFloor calls (merge plugs)
    replace(OLD_UPDATE_ALL, NEW_UPDATE_ALL, 'updateRoomFloor calls (merge plugs)',
            marker='PHASE10_TOOLTIPS_APPLIED — mergni plugs')

    replace(OLD_ZONE_CARDS, NEW_ZONE_CARDS, 'updateZoneCard pracovna (+office plug)')
    replace(OLD_BEDROOM_ZC, NEW_BEDROOM_ZC, 'updateZoneCard bedroom (+tv/humidifier plugs)')

    # C. dev-tile
    replace(OLD_DEV_TILE, NEW_DEV_TILE, 'dev-tile title attr')

    # D. hd-tile
    replace(OLD_HD_TILE, NEW_HD_TILE, 'hd-tile title attr')

    # E. updateRoomFloor fn + updateZoneCard fn (add title)
    replace(OLD_UPDATE_FN, NEW_UPDATE_FN, 'updateRoomFloor() s tooltipem na celé zóně',
            marker='PHASE10_TOOLTIPS_APPLIED — tooltip na celé zóně')
    replace(OLD_ZONE_CARD_FN, NEW_ZONE_CARD_FN, 'updateZoneCard() s tooltipem',
            marker='PHASE10_TOOLTIPS_APPLIED — tooltip')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 10 — Tooltips + Home zone device ikony')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
