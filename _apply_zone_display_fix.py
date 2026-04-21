"""
Replace global DEVICE_DISPLAY with DEVICE_DISPLAY_BY_ZONE + zone-aware lookup
in remaining dashboards. Idempotent.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

P1_OLD = """// Friendly name + icon per data key
const DEVICE_DISPLAY = {
  // Jídelna
  light_1: { name: 'Sektorka', icon: '💡', type: 'light' },
  light_2: { name: 'Stůl jídelna', icon: '💡', type: 'light' },
  strip:   { name: 'Led pásek', icon: '🎗', type: 'light' },
  // Kitchen
  light_3: { name: 'Kuchyně 1', icon: '💡', type: 'light' },
  light_4: { name: 'Kuchyně 2', icon: '💡', type: 'light' },
  // Bedroom
  light:     { name: 'Žárovka', icon: '💡', type: 'light' },
  lampicka:  { name: 'Lampička', icon: '🛋', type: 'light' },
  e14_1:     { name: 'E14 žárovka 1', icon: '💡', type: 'light' },
  e14_2:     { name: 'E14 žárovka 2', icon: '💡', type: 'light' },
  // Plugs
  plug:    { name: 'PC zásuvka', icon: '🔌', type: 'plug' },
  boiler:  { name: 'Boiler', icon: '🔥', type: 'plug' },
  // Generic fallbacks by key pattern
};"""

P1_NEW = """// FIX 2026-04-20: ZONE-AWARE DEVICE_DISPLAY
// Bridge používá stejné klíče v různých zónách (jidelna.light_2 = Stul Jidelna,
// kitchen.light_2 = Kitchen Bulb 1) → globální mapa vedla k misnames.
const DEVICE_DISPLAY_BY_ZONE = {
  jidelna: {
    light_2: { name: 'Stůl jídelna', icon: '💡', type: 'light' },
    strip:   { name: 'Led pásek',    icon: '🎗', type: 'light' },
  },
  kitchen: {
    light_1: { name: 'Sektorka',   icon: '💡', type: 'light' },
    light_2: { name: 'Kuchyně 1',  icon: '💡', type: 'light' },
    light_3: { name: 'Kuchyně 2',  icon: '💡', type: 'light' },
    light_4: { name: 'Kuchyně 3',  icon: '💡', type: 'light' },
  },
  bedroom: {
    light:    { name: 'Žárovka',         icon: '💡', type: 'light' },
    strip:    { name: 'LED pásek postel', icon: '🎗', type: 'light' },
    lampicka: { name: 'Lampička',         icon: '🛋', type: 'light' },
    e14_1:    { name: 'E14 žárovka 1',    icon: '💡', type: 'light' },
    e14_2:    { name: 'E14 žárovka 2',    icon: '💡', type: 'light' },
  },
  bathroom: { light: { name: 'Světlo koupelna', icon: '💡', type: 'light' } },
  toilet:   { light: { name: 'Světlo toaleta',  icon: '💡', type: 'light' } },
  pracovna: {
    light: { name: 'Žárovka pracovna', icon: '💡', type: 'light' },
    plug:  { name: 'Zásuvka PC',       icon: '🔌', type: 'plug'  },
  },
  pradelna: {
    light:  { name: 'Světlo prádelna', icon: '💡', type: 'light' },
    boiler: { name: 'Boiler',          icon: '🔥', type: 'plug'  },
  },
  predsin:  { light: { name: 'Světlo předsíň', icon: '💡', type: 'light' } },
};
const DEVICE_DISPLAY = {
  plug:    { name: 'Zásuvka', icon: '🔌', type: 'plug' },
  boiler:  { name: 'Boiler',  icon: '🔥', type: 'plug' },
};"""

P2_OLD = """  function getDeviceDisplay(key) {
    if (DEVICE_DISPLAY[key]) return DEVICE_DISPLAY[key];
    const k = key.toLowerCase();
    if (k.includes('plug') || k.includes('boiler') || k.includes('office') || k.includes('zasuvka')) return { name: key, icon: '🔌', type: 'plug' };
    if (k.includes('strip')) return { name: key, icon: '🎗', type: 'light' };
    if (k.includes('lampicka') || k.includes('lamp')) return { name: key, icon: '🛋', type: 'light' };
    if (k.includes('tv')) return { name: key, icon: '📺', type: 'plug' };
    return { name: key, icon: '💡', type: 'light' };
  }"""

P2_NEW = """  // FIX 2026-04-20: zone-aware — zone je captured z renderZoneDetail(zone)
  function getDeviceDisplay(key) {
    const zoneMap = (typeof DEVICE_DISPLAY_BY_ZONE !== 'undefined') ? DEVICE_DISPLAY_BY_ZONE[zone] : null;
    if (zoneMap && zoneMap[key]) return zoneMap[key];
    if (DEVICE_DISPLAY[key]) return DEVICE_DISPLAY[key];
    const k = key.toLowerCase();
    if (k.includes('plug') || k.includes('boiler') || k.includes('office') || k.includes('zasuvka')) return { name: key, icon: '🔌', type: 'plug' };
    if (k.includes('strip')) return { name: key, icon: '🎗', type: 'light' };
    if (k.includes('lampicka') || k.includes('lamp')) return { name: key, icon: '🛋', type: 'light' };
    if (k.includes('tv')) return { name: key, icon: '📺', type: 'plug' };
    return { name: key, icon: '💡', type: 'light' };
  }"""

P3_OLD = """    // Room devices (lights, plugs from roomData)
    devs.forEach(([k, lv]) => {
      const dd = DEVICE_DISPLAY[k] || {name:k, icon:'💡', type:'light'};"""

P3_NEW = """    // Room devices — FIX 2026-04-20: zone-aware lookup
    devs.forEach(([k, lv]) => {
      const zm = (typeof DEVICE_DISPLAY_BY_ZONE !== 'undefined') ? DEVICE_DISPLAY_BY_ZONE[zone.key] : null;
      const dd = (zm && zm[k]) || DEVICE_DISPLAY[k] || {name:k, icon:'💡', type:'light'};"""

def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}"); return
    with open(fp,'r',encoding='utf-8',newline='') as f: c = f.read()
    if 'DEVICE_DISPLAY_BY_ZONE' in c:
        print(f"  ⏭️  ALREADY PATCHED: {os.path.basename(fp)}"); return
    orig = c; changed = []
    for old, new, name in [(P1_OLD,P1_NEW,'DEVICE_DISPLAY_BY_ZONE'),(P2_OLD,P2_NEW,'getDeviceDisplay zone-aware'),(P3_OLD,P3_NEW,'Home page zone lookup')]:
        if old in c:
            c = c.replace(old, new, 1); changed.append(name)
        else:
            crlf = old.replace('\n','\r\n')
            if crlf in c:
                c = c.replace(crlf, new.replace('\n','\r\n'), 1); changed.append(name+'(CRLF)')
            else:
                changed.append('❌ '+name)
    if c != orig:
        with open(fp,'w',encoding='utf-8',newline='') as f: f.write(c)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
        for ch in changed: print(f"     + {ch}")
    else:
        print(f"  ⚠️  NO CHANGES: {os.path.basename(fp)}")

for f in FILES:
    print(f"Processing: {f}")
    patch(f); print()
print('Hotovo.')
