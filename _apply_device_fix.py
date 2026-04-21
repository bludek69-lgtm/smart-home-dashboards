"""
Apply "Zařízení X nenalezeno" fix to all dashboard HTML files.

Fixes applied:
1. Add _normalizeName() + resolveDeviceName() helpers before setDeviceCap
2. Make setDeviceCap use resolveDeviceName() for fuzzy matching
3. Add rawName to _tileData.push so onclick handlers can use real Homey name
4. Update openDeviceDetail ON/OFF + sliders to use apiName = d.rawName || d.name

Run once; idempotent (skips file if already patched).
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\rasberi\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\1\smart_home_rpi.html',
]

# FIX 1 — replace setDeviceCap definition with resolveDeviceName helpers + updated body
SETCAP_OLD = '''async function setDeviceCap(deviceName, capability, value) {
  try {
    if (!varMapLoaded) await loadVarMap();
    const d = ALL_DEVICES[deviceName];
    if (!d) { flash('⚠ Zařízení ' + deviceName + ' nenalezeno'); return; }
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/' + capability, { value });
    flash('✓ ' + deviceName + ' → ' + capability + ' = ' + value);
  } catch(e) { flash('✗ ' + e.message); }
}'''

SETCAP_NEW = '''// FIX 2026-04-20: resolveDeviceName — fuzzy match friendly labels ("Stůl jídelna")
//   na skutečná Homey jména ("Stul Jidelna1"). Normalizuje háčky/case/čísla.
function _normalizeName(s) {
  return String(s || '').toLowerCase().trim()
    .replace(/ů/g,'u').replace(/í/g,'i').replace(/á/g,'a').replace(/é/g,'e')
    .replace(/ě/g,'e').replace(/š/g,'s').replace(/č/g,'c').replace(/ř/g,'r')
    .replace(/ž/g,'z').replace(/ý/g,'y').replace(/ú/g,'u').replace(/ň/g,'n')
    .replace(/ť/g,'t').replace(/ď/g,'d').replace(/\\d+$/,'').trim();
}
function resolveDeviceName(displayName) {
  if (!displayName || !ALL_DEVICES) return displayName;
  if (ALL_DEVICES[displayName]) return displayName;
  const norm = _normalizeName(displayName);
  for (const k of Object.keys(ALL_DEVICES)) {
    if (_normalizeName(k) === norm) return k;
  }
  for (const k of Object.keys(ALL_DEVICES)) {
    const nk = _normalizeName(k);
    if (nk.includes(norm) || norm.includes(nk)) return k;
  }
  return displayName;
}

async function setDeviceCap(deviceName, capability, value) {
  try {
    if (!varMapLoaded) await loadVarMap();
    const resolved = resolveDeviceName(deviceName);
    const d = ALL_DEVICES[resolved];
    if (!d) { flash('⚠ Zařízení ' + deviceName + ' nenalezeno (resolved: ' + resolved + ')'); return; }
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/' + capability, { value });
    flash('✓ ' + resolved + ' → ' + capability + ' = ' + value);
  } catch(e) { flash('✗ ' + e.message); }
}'''

# FIX 2 — _tileData.push in renderZoneDetail (light devices)
TILE_OLD = '''      const tIdx = _tileData.length;
      _tileData.push({key:k, name:safeName, icon:dd.icon, type:dd.type, on:isOn,
        dim: lv.dim !== undefined ? lv.dim : null,
        hasDim: hasDim, hasTemp: hasTemp,
        temp: lv.light_temperature !== undefined ? lv.light_temperature : null,
        power: lv.power !== undefined ? lv.power : null,
        plugTemp: lv.temperature !== undefined ? lv.temperature : null});'''

TILE_NEW = '''      const tIdx = _tileData.length;
      // FIX 2026-04-20: rawName = Homey physical device name (z bridge data),
      //   name = friendly label ("Stůl jídelna"). API calls používají rawName.
      _tileData.push({key:k, name:safeName, rawName:rawName, icon:dd.icon, type:dd.type, on:isOn,
        dim: lv.dim !== undefined ? lv.dim : null,
        hasDim: hasDim, hasTemp: hasTemp,
        temp: lv.light_temperature !== undefined ? lv.light_temperature : null,
        power: lv.power !== undefined ? lv.power : null,
        plugTemp: lv.temperature !== undefined ? lv.temperature : null});'''

# FIX 3 — ON/OFF buttons in openDeviceDetail (ZAP/VYP)
ONOFF_OLD = '''  // ON/OFF card
  html += '<div class="dd-card">' +
    '<div class="dd-label">Stav</div>' +
    '<div class="dd-onoff">' +
      '<div class="dd-btn dd-btn-on' + (d.on ? ' active' : '') + '" onclick="ddSetOnOff(\\'' + d.name + '\\',true)">▶ ZAP</div>' +
      '<div class="dd-btn dd-btn-off' + (!d.on ? ' active' : '') + '" onclick="ddSetOnOff(\\'' + d.name + '\\',false)">⏹ VYP</div>' +
    '</div>' +
  '</div>';'''

ONOFF_NEW = '''  // ON/OFF card — FIX 2026-04-20: preferuj rawName (Homey device name) před friendly label
  const apiName = d.rawName || d.name;
  html += '<div class="dd-card">' +
    '<div class="dd-label">Stav</div>' +
    '<div class="dd-onoff">' +
      '<div class="dd-btn dd-btn-on' + (d.on ? ' active' : '') + '" onclick="ddSetOnOff(\\'' + apiName + '\\',true)">▶ ZAP</div>' +
      '<div class="dd-btn dd-btn-off' + (!d.on ? ' active' : '') + '" onclick="ddSetOnOff(\\'' + apiName + '\\',false)">⏹ VYP</div>' +
    '</div>' +
  '</div>';'''

# FIX 4 — Dim slider in openDeviceDetail
DIM_OLD = '''  // Dim slider
  if (d.hasDim && d.type !== 'blind') {
    const dimPct = Math.round((d.dim || 0) * 100);
    html += '<div class="dd-card">' +
      '<div class="dd-label">Jas</div>' +
      '<div class="dd-slider-row">' +
        '<div class="dd-sl-icon">☀️</div>' +
        '<input type="range" min="1" max="100" value="' + dimPct + '"' +
          ' oninput="this.parentElement.querySelector(\\'.dd-sl-val\\').textContent=this.value+\\'%\\'"' +
          ' onchange="setDeviceCap(\\'' + d.name + '\\',\\'dim\\',this.value/100)">' +
        '<div class="dd-sl-val">' + dimPct + '%</div>' +
      '</div>' +
    '</div>';
  }'''

DIM_NEW = '''  // Dim slider — FIX 2026-04-20: apiName (rawName || name) pro API calls
  if (d.hasDim && d.type !== 'blind') {
    const dimPct = Math.round((d.dim || 0) * 100);
    html += '<div class="dd-card">' +
      '<div class="dd-label">Jas</div>' +
      '<div class="dd-slider-row">' +
        '<div class="dd-sl-icon">☀️</div>' +
        '<input type="range" min="1" max="100" value="' + dimPct + '"' +
          ' oninput="this.parentElement.querySelector(\\'.dd-sl-val\\').textContent=this.value+\\'%\\'"' +
          ' onchange="setDeviceCap(\\'' + apiName + '\\',\\'dim\\',this.value/100)">' +
        '<div class="dd-sl-val">' + dimPct + '%</div>' +
      '</div>' +
    '</div>';
  }'''

# FIX 5 — ddSetOnOff simplification (remove old fuzzy logic if present)
DDSETONOFF_OLD_SIMPLE = '''function ddSetOnOff(name, val) {
  setDeviceCap(name, 'onoff', val);
  // Visually update buttons immediately
  const btns = document.querySelectorAll('.dd-onoff .dd-btn');
  btns.forEach(b => b.classList.remove('active'));
  if (val) {
    btns[0]?.classList.add('active');
  } else {
    btns[1]?.classList.add('active');
  }
}'''

DDSETONOFF_NEW = '''function ddSetOnOff(name, val) {
  // setDeviceCap už má resolveDeviceName interně
  setDeviceCap(name, 'onoff', val);
  const btns = document.querySelectorAll('.dd-onoff .dd-btn');
  btns.forEach(b => b.classList.remove('active'));
  if (val) btns[0]?.classList.add('active');
  else     btns[1]?.classList.add('active');
}'''

def apply_fixes(filepath):
    if not os.path.exists(filepath):
        print(f"  ❌ SKIP: {filepath} neexistuje")
        return
    with open(filepath, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    original = content
    changes = []

    # Detect if already patched (idempotent)
    if 'function resolveDeviceName' in content:
        print(f"  ⏭️  ALREADY PATCHED: {os.path.basename(filepath)}")
        return

    # FIX 1: setDeviceCap
    if SETCAP_OLD in content:
        content = content.replace(SETCAP_OLD, SETCAP_NEW, 1)
        changes.append('setDeviceCap + resolveDeviceName')
    else:
        # Try with CRLF variant
        setcap_old_crlf = SETCAP_OLD.replace('\n', '\r\n')
        if setcap_old_crlf in content:
            content = content.replace(setcap_old_crlf, SETCAP_NEW.replace('\n', '\r\n'), 1)
            changes.append('setDeviceCap + resolveDeviceName (CRLF)')

    # FIX 2: _tileData.push (LIGHT)
    if TILE_OLD in content:
        content = content.replace(TILE_OLD, TILE_NEW, 1)
        changes.append('_tileData rawName')
    else:
        tile_old_crlf = TILE_OLD.replace('\n', '\r\n')
        if tile_old_crlf in content:
            content = content.replace(tile_old_crlf, TILE_NEW.replace('\n', '\r\n'), 1)
            changes.append('_tileData rawName (CRLF)')

    # FIX 3: ON/OFF buttons
    if ONOFF_OLD in content:
        content = content.replace(ONOFF_OLD, ONOFF_NEW, 1)
        changes.append('ON/OFF apiName')
    else:
        onoff_old_crlf = ONOFF_OLD.replace('\n', '\r\n')
        if onoff_old_crlf in content:
            content = content.replace(onoff_old_crlf, ONOFF_NEW.replace('\n', '\r\n'), 1)
            changes.append('ON/OFF apiName (CRLF)')

    # FIX 4: Dim slider
    if DIM_OLD in content:
        content = content.replace(DIM_OLD, DIM_NEW, 1)
        changes.append('Dim slider apiName')
    else:
        dim_old_crlf = DIM_OLD.replace('\n', '\r\n')
        if dim_old_crlf in content:
            content = content.replace(dim_old_crlf, DIM_NEW.replace('\n', '\r\n'), 1)
            changes.append('Dim slider apiName (CRLF)')

    # FIX 5: ddSetOnOff simplification (optional)
    if DDSETONOFF_OLD_SIMPLE in content:
        content = content.replace(DDSETONOFF_OLD_SIMPLE, DDSETONOFF_NEW, 1)
        changes.append('ddSetOnOff simplified')

    if content != original:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(filepath)}")
        for c in changes:
            print(f"     + {c}")
    else:
        print(f"  ⚠️  NO CHANGES: {os.path.basename(filepath)} — patterns nesedí (starší struktura?)")

if __name__ == '__main__':
    print("Applying dashboard device-name fixes...\n")
    for f in FILES:
        print(f"Processing: {f}")
        apply_fixes(f)
        print()
    print("Hotovo.")
