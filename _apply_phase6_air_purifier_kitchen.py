"""
PHASE 6 — Air Purifier 4 Lite tile v kitchen zone + config + help

CONTEXT:
  User identifikoval chybějící přímé ovládání čističky v dashboardu.
  Existuje jen toggle "Hlídání čističky" (auto/manual) v Advanced CONFIG,
  a read-only status v appliances card na home page.

REUSE FIRST audit:
  ✅ Existující: sh_air_purifier_router_v1 v1.3 (auto PM2.5 control)
  ✅ Existující: sh_air_purifier_guard_enabled proměnná (on/off guard)
  ✅ Existující: togglePurifierGuard() JS helper
  ❌ Chybí: Přímý ON/OFF tile v kitchen zóně
  ❌ Chybí: Zmínka v ZONE_HELP.kitchen
  ❌ Chybí: Config row v ZONE_CFG.kitchen (hlídání)

ADDS:
  1) Purifier tile v kitchen zone (ON/OFF + PM2.5 + temp + hum + hlídání)
  2) Helpers: refreshPurifier(), togglePurifierDevice(), _findPurifier()
  3) ZONE_HELP.kitchen rozšíření — 🌬 Čistička
  4) ZONE_CFG.kitchen rozšíření — sh_air_purifier_guard_enabled

Idempotent. Marker: PHASE6_AIR_PURIFIER_APPLIED.
"""
import os
import re

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE6_AIR_PURIFIER_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 1: HTML tile v kitchen zone — BEFORE Lednice sparkline (Phase 2)
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_HTML = "  // PHASE2_HUM_VACUUM_FRIDGE_APPLIED — Lednice power sparkline (kitchen)"

INJECT_HTML = """  // PHASE6_AIR_PURIFIER_APPLIED — Čistička vzduchu panel (kitchen)
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

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 2: JS helpers — BEFORE _drawFridgeSpark (phase2 helpers block)
# ═══════════════════════════════════════════════════════════════════════════
ANCHOR_JS = "// ── Lednice sparkline ────────────────────────────────────────────────────"

INJECT_JS = """// ── PHASE6_AIR_PURIFIER_APPLIED — Air Purifier 4 Lite ────────────────────
async function _findPurifier() {
  if (typeof varMapLoaded !== 'undefined' && !varMapLoaded) await loadVarMap();
  if (ALL_DEVICES && ALL_DEVICES['Air Purifier 4 Lite']) return { name: 'Air Purifier 4 Lite', ...ALL_DEVICES['Air Purifier 4 Lite'] };
  if (ALL_DEVICES) {
    for (const [k, v] of Object.entries(ALL_DEVICES)) {
      const kl = k.toLowerCase();
      if (kl.includes('purifier') || kl.includes('čistič') || kl.includes('cistic')) return { name: k, ...v };
    }
  }
  try {
    const all = await apiGet('/api/manager/devices/device/');
    for (const [id, d] of Object.entries(all || {})) {
      const n = String(d.name || '').toLowerCase();
      if (n.includes('purifier') || n.includes('čistič') || n.includes('cistic')) {
        if (ALL_DEVICES) ALL_DEVICES[d.name] = { id, caps: d.capabilities || [] };
        return { name: d.name, id, caps: d.capabilities || [] };
      }
    }
  } catch(_){}
  return null;
}

async function refreshPurifier() {
  const el = document.getElementById('purifier-stav');
  if (!el) return;
  try {
    const d = await _findPurifier();
    if (!d) { el.innerHTML = 'Zařízení "Air Purifier 4 Lite" nenalezeno'; return; }
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const co = detail.capabilitiesObj || {};
    const on = co.onoff ? co.onoff.value : null;
    const temp = co.measure_temperature && co.measure_temperature.value != null ? Math.round(co.measure_temperature.value) : null;
    const hum = co.measure_humidity && co.measure_humidity.value != null ? Math.round(co.measure_humidity.value) : null;
    const pm25 = co.measure_pm25 && co.measure_pm25.value != null ? Math.round(co.measure_pm25.value) : null;
    const avail = detail.available === false ? '❌ offline' : '✅ online';
    let parts = [];
    parts.push('Stav: <strong>' + (on === true ? 'ON' : on === false ? 'OFF' : '—') + '</strong>');
    if (pm25 !== null) {
      const pm25Class = pm25 > 120 ? 'style="color:var(--red);"' : pm25 > 50 ? 'style="color:var(--orange);"' : 'style="color:var(--green);"';
      parts.push('PM2.5: <strong ' + pm25Class + '>' + pm25 + ' μg/m³</strong>');
    }
    if (temp !== null) parts.push('T: ' + temp + '°C');
    if (hum !== null) parts.push('Vlhkost: ' + hum + '%');
    parts.push(avail);
    el.innerHTML = parts.join(' · ');
  } catch(e) { el.textContent = 'err: ' + e.message; }
}

async function togglePurifierDevice(val) {
  try {
    const d = await _findPurifier();
    if (!d) { try { flash('⚠ Čistička nenalezena'); } catch(_){}; return; }
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/onoff', { value: !!val });
    try { flash('🌬 Čistička ' + (val ? 'ZAP' : 'VYP')); } catch(_){}
    setTimeout(refreshPurifier, 400);
  } catch(e) { try { flash('✗ ' + e.message); } catch(_){} }
}

"""

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 3: ZONE_HELP.kitchen — add 🌬 Čistička entry (regex append)
# Matches different variants (RPi short vs desktop detailed)
# ═══════════════════════════════════════════════════════════════════════════
ZONE_HELP_ITEM = "      '<strong>🌬 Air Purifier 4 Lite</strong> — ON/OFF tile v kuchyni + PM2.5/temp/hum live. Auto režim dle PM2.5 (sh_air_purifier_router_v1).'"

# ═══════════════════════════════════════════════════════════════════════════
# INJECT 4: ZONE_CFG.kitchen — add purifier config row
# Anchor: "sh_cfg_plug_inactivity_w" (existing kitchen config item)
# ═══════════════════════════════════════════════════════════════════════════
OLD_CFG = """    { name: 'sh_cfg_plug_inactivity_w',       label: 'Zásuvka — práh nečinnosti', unit: 'W',
      desc: 'Pod touto spotřebou je spotřebič považován za zapomenutý/nečinný (trouba zapnutá ale nic v ní).' },"""

NEW_CFG = """    { name: 'sh_cfg_plug_inactivity_w',       label: 'Zásuvka — práh nečinnosti', unit: 'W',
      desc: 'Pod touto spotřebou je spotřebič považován za zapomenutý/nečinný (trouba zapnutá ale nic v ní).' },
    { name: 'sh_air_purifier_guard_enabled',  label: 'Čistička — auto režim (PM2.5)', unit: '', type: 'text',
      desc: 'yes = sh_air_purifier_router_v1 řídí čističku automaticky dle PM2.5. no = čistička běží manuálně. Viz 🌬 tile v Kuchyni.' },"""


def patch_zone_help(content, is_crlf, zone, new_item):
    """Append new item to ZONE_HELP[zone].items (robust regex-based)"""
    nl = '\r\n' if is_crlf else '\n'
    new_item_ws = new_item.replace('\n', nl) if is_crlf else new_item

    # Detect if already applied by checking for "🌬 Air Purifier" in content around kitchen ZONE_HELP
    zone_start_pat = rf'  {zone}: \{{'
    m = re.search(zone_start_pat, content)
    if not m:
        return content, f"❌ ZONE_HELP {zone} (zone nenalezen)"
    start = m.start()
    items_start = content.find('items: [', start)
    if items_start == -1:
        return content, f"❌ ZONE_HELP {zone} (items array nenalezen)"
    items_end = content.find(']', items_start)
    if items_end == -1:
        return content, f"❌ ZONE_HELP {zone} (items ] nenalezen)"
    flow_pos = content.find('flow:', items_start)
    if flow_pos != -1 and flow_pos < items_end:
        return content, f"❌ ZONE_HELP {zone} (corrupt)"

    # Check if purifier already in items
    items_block = content[items_start:items_end]
    if '🌬 Air Purifier' in items_block or 'Air Purifier 4 Lite' in items_block:
        return content, f"⏭ ZONE_HELP {zone} (už obsahuje Air Purifier)"

    # Check whether last item ends with comma
    before = content[items_start + len('items: ['):items_end]
    stripped = before.rstrip()
    needs_comma = bool(stripped) and not stripped.endswith(',')

    prefix = ',' + nl if needs_comma else nl
    injected = prefix + new_item_ws + nl
    new_content = content[:items_end] + injected + content[items_end:]
    return new_content, f"+ ZONE_HELP {zone}"


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP (not found): {fp}")
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
            changes.append('⏭ ' + label + ' (není anchor / už applied)')

    # 1. HTML tile injection
    if ANCHOR_HTML in content:
        inj = INJECT_HTML.replace('\n', '\r\n') if is_crlf else INJECT_HTML
        if 'PHASE6_AIR_PURIFIER_APPLIED' not in content:
            content = content.replace(ANCHOR_HTML, inj + ANCHOR_HTML, 1)
            changes.append('+ HTML tile (purifier in kitchen)')
        else:
            changes.append('⏭ HTML tile (už applied)')
    else:
        changes.append('❌ HTML anchor nenalezen')

    # 2. JS helpers (only if not already applied)
    if 'PHASE6_AIR_PURIFIER_APPLIED — Air Purifier 4 Lite' not in content:
        if ANCHOR_JS in content:
            inj = INJECT_JS.replace('\n', '\r\n') if is_crlf else INJECT_JS
            content = content.replace(ANCHOR_JS, inj + ANCHOR_JS, 1)
            changes.append('+ JS helpers (_findPurifier, refreshPurifier, togglePurifierDevice)')
        else:
            changes.append('❌ JS anchor nenalezen')
    else:
        changes.append('⏭ JS helpers (už applied)')

    # 3. ZONE_HELP.kitchen
    content, msg = patch_zone_help(content, is_crlf, 'kitchen', ZONE_HELP_ITEM)
    changes.append(msg)

    # 4. ZONE_CFG.kitchen
    replace(OLD_CFG, NEW_CFG, 'ZONE_CFG.kitchen (sh_air_purifier_guard_enabled)')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 6 — Air Purifier 4 Lite → kitchen zone + config + help')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
