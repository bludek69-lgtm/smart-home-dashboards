"""
Phase 17 (2026-04-21) — Zone disable toggle v heating tile
Přidá ON/OFF přepínač do každého zone tile:
  - click → toggleHeatingZone(zoneId) → přepíná sh_heating_zone_<z>_enabled
  - vizuálně: OFF tile má opacity 0.5 + červený rámeček + ❌ badge
  - scheduler/demand už správně ignorují enabled=no zóny (target → 7°C anti-freeze)

Idempotentní — marker toggleHeatingZone.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'toggleHeatingZone'

# ═══════════════════════════════════════════════════════════════════════════
# 1. Replace zone tile rendering: přidat toggle + enabled-aware styling
# ═══════════════════════════════════════════════════════════════════════════

OLD_ZONE_TILE_TEMPLATE = '''      grid.innerHTML = HEAT_ZONES.map(z => {
        const enabled = String((ALL_VARS['sh_heating_zone_' + z.id + '_enabled'] || {}).value || 'yes').toLowerCase() === 'yes';
        const curr = Number((ALL_VARS['sh_heating_zone_' + z.id + '_current_temp'] || {}).value || -99);
        const tgt = Number((ALL_VARS['sh_heating_zone_' + z.id + '_target_temp'] || {}).value || 20);
        const currTxt = curr > 0 ? curr.toFixed(1) + ' °C' : '— °C';
        const tgtTxt = tgt.toFixed(1) + ' °C';
        const pct = curr > 0 ? Math.max(0, Math.min(100, ((curr - 10) / (28 - 10)) * 100)) : 0;
        const heating = (tgt - curr) > 0.3 && curr > 0;
        const borderColor = !enabled ? 'var(--tx3)' : heating ? 'var(--orange)' : 'var(--bd)';
        return `<div class="heat-zone-tile" style="border-color:${borderColor};">
          <div class="zone-hdr">
            <span>${z.icon}</span>
            <strong>${z.label}</strong>
            ${!enabled ? '<span style="color:var(--tx3);font-size:10px;margin-left:auto;">off</span>' : heating ? '<span style="color:var(--orange);font-size:10px;margin-left:auto;">🔥 topí</span>' : ''}
          </div>
          <div class="zone-temps">
            <span class="curr">${currTxt}</span>
            <span class="tgt">→ ${tgtTxt}</span>
          </div>
          <div class="zone-bar"><div class="zone-bar-fill" style="width:${pct}%;"></div></div>
        </div>`;
      }).join('');'''

NEW_ZONE_TILE_TEMPLATE = '''      grid.innerHTML = HEAT_ZONES.map(z => {
        const enabled = String((ALL_VARS['sh_heating_zone_' + z.id + '_enabled'] || {}).value || 'yes').toLowerCase() === 'yes';
        const curr = Number((ALL_VARS['sh_heating_zone_' + z.id + '_current_temp'] || {}).value || -99);
        const tgt = Number((ALL_VARS['sh_heating_zone_' + z.id + '_target_temp'] || {}).value || 20);
        const currTxt = curr > 0 ? curr.toFixed(1) + ' °C' : '— °C';
        const tgtTxt = tgt.toFixed(1) + ' °C';
        const pct = curr > 0 ? Math.max(0, Math.min(100, ((curr - 10) / (28 - 10)) * 100)) : 0;
        const heating = enabled && (tgt - curr) > 0.3 && curr > 0;
        const borderColor = !enabled ? 'var(--red)' : heating ? 'var(--orange)' : 'var(--bd)';
        const tileOpacity = !enabled ? '0.55' : '1';
        const statusBadge = !enabled
          ? '<span style="color:var(--red);font-size:10px;">❌ VYPNUTO</span>'
          : heating ? '<span style="color:var(--orange);font-size:10px;">🔥 topí</span>' : '';
        const toggleLabel = enabled ? '✅ ZAP' : '❌ VYP';
        const toggleColor = enabled ? 'var(--green)' : 'var(--red)';
        return `<div class="heat-zone-tile" style="border-color:${borderColor}; opacity:${tileOpacity};">
          <div class="zone-hdr">
            <span>${z.icon}</span>
            <strong>${z.label}</strong>
            <div class="zone-tog-btn" onclick="toggleHeatingZone('${z.id}'); event.stopPropagation();"
                 style="margin-left:auto;padding:2px 6px;font-size:10px;border:1px solid ${toggleColor};color:${toggleColor};border-radius:3px;cursor:pointer;font-family:var(--mono);">
              ${toggleLabel}
            </div>
          </div>
          <div style="font-size:9px;color:var(--tx3);margin-top:-2px;margin-bottom:4px;">${statusBadge}</div>
          <div class="zone-temps">
            <span class="curr">${currTxt}</span>
            <span class="tgt">→ ${tgtTxt}</span>
          </div>
          <div class="zone-bar"><div class="zone-bar-fill" style="width:${pct}%;"></div></div>
        </div>`;
      }).join('');'''

# ═══════════════════════════════════════════════════════════════════════════
# 2. Add toggleHeatingZone function
# ═══════════════════════════════════════════════════════════════════════════

NEW_TOGGLE_FN = '''

async function toggleHeatingZone(zoneId) {
  try {
    if (!varMapLoaded) await loadVarMap();
    const varName = 'sh_heating_zone_' + zoneId + '_enabled';
    const cur = String((ALL_VARS[varName] || {}).value || 'yes').toLowerCase();
    const newVal = cur === 'yes' ? 'no' : 'yes';
    await writeVar(varName, newVal);
    if (ALL_VARS[varName]) ALL_VARS[varName].value = newVal;
    try { flash((newVal === 'no' ? '❌ Vypnuto: ' : '✅ Zapnuto: ') + zoneId); } catch(_){}
    setTimeout(refreshHeating, 200);
  } catch (e) { try { flash('✗ ' + e.message); } catch(_){} }
}
'''

# Insert before existing setHeatingMode function
FN_ANCHOR = re.compile(r'(\nasync function setHeatingMode\()')


def patch_file(path):
    if not os.path.exists(path):
        print(f'  ✗ NOT FOUND: {path}')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if MARKER in html:
        print(f'  ✓ already patched: {os.path.basename(path)}')
        return True

    orig_len = len(html)

    # 1. Replace zone tile template
    if OLD_ZONE_TILE_TEMPLATE not in html:
        print(f'  ✗ old template not found: {os.path.basename(path)}')
        return False
    html = html.replace(OLD_ZONE_TILE_TEMPLATE, NEW_ZONE_TILE_TEMPLATE, 1)

    # 2. Insert toggleHeatingZone function
    m = FN_ANCHOR.search(html)
    if not m:
        print(f'  ✗ fn anchor not found: {os.path.basename(path)}')
        return False
    html = html[:m.start()] + NEW_TOGGLE_FN + m.group(0) + html[m.end():]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(path)} ({len(html)-orig_len:+d} bytes)')
    return True


def main():
    print('Phase 17: Zone disable toggle in heating tiles')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
