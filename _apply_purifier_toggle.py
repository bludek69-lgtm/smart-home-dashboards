"""
Add purifier guard toggle to dashboards: button + JS function + state sync.
Idempotent.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# Patch 1: add toggle HTML after auto-scene row
P1_OLD = '''      <div class="tog-row"><span class="card-icon">🌙</span><span class="tog-lbl">Auto-scény (večer relax)</span><div class="toggle" id="tog-auto-scene" onclick="toggleVar('sh_cfg_auto_scene_enabled',this)"></div></div>
    </div>'''

P1_NEW = '''      <div class="tog-row"><span class="card-icon">🌙</span><span class="tog-lbl">Auto-scény (večer relax)</span><div class="toggle" id="tog-auto-scene" onclick="toggleVar('sh_cfg_auto_scene_enabled',this)"></div></div>
      <div class="divider"></div>
      <div class="tog-row"><span class="card-icon">🫁</span><span class="tog-lbl" title="sh_air_purifier_guard_enabled — při OFF čistička běží manuálně">Hlídání čističky</span><div class="toggle" id="tog-purifier" onclick="togglePurifierGuard(this)"></div></div>
    </div>'''

# Patch 2: add togglePurifierGuard before toggleVisitorMode
P2_OLD = 'async function toggleVisitorMode() {'
P2_NEW = '''// FIX 2026-04-20: toggle hlídání čističky + push notifikace při změně
async function togglePurifierGuard(el) {
  try {
    if (!varMapLoaded) await loadVarMap();
    const cur = String(ALL_VARS['sh_air_purifier_guard_enabled']?.value || 'yes').trim().toLowerCase();
    const next = (cur === 'yes' || cur === 'true' || cur === 'on') ? 'no' : 'yes';
    await writeVar('sh_air_purifier_guard_enabled', next);
    if (el) el.classList.toggle('on', next === 'yes');
    const msg = next === 'no'
      ? '🔕 Hlídání čističky VYPNUTO — automatizace už nezasahuje. Zapni zpět až budeš chtít.'
      : '✅ Hlídání čističky ZAPNUTO — systém zase řídí rychlost dle PM2.5.';
    try {
      const payload = JSON.stringify({ severity: 'info', module: 'dashboard_purifier_toggle', message: msg });
      await writeVar('sh_notification_request', 'idle');
      await writeVar('sh_notification_request', payload);
    } catch(_) {}
    showFlash(msg);
    setTimeout(poll, 1500);
  } catch(e) { showFlash('✗ ' + e.message); }
}

async function toggleVisitorMode() {'''

# Patch 3: add state sync to poll
P3_OLD = "setToggle('tog-auto-scene', String(ALL_VARS['sh_cfg_auto_scene_enabled']?.value || 'no'));"
P3_NEW = ("setToggle('tog-auto-scene', String(ALL_VARS['sh_cfg_auto_scene_enabled']?.value || 'no'));\n"
          "  // FIX 2026-04-20: purifier guard toggle (default 'yes' = ON)\n"
          "  setToggle('tog-purifier', String(ALL_VARS['sh_air_purifier_guard_enabled']?.value || 'yes'));")

def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}"); return
    with open(fp,'r',encoding='utf-8',newline='') as f: c = f.read()
    if 'togglePurifierGuard' in c:
        print(f"  ⏭️  ALREADY PATCHED: {os.path.basename(fp)}"); return
    orig = c; changes = []
    for i,(old,new,name) in enumerate([(P1_OLD,P1_NEW,'toggle HTML'),(P2_OLD,P2_NEW,'togglePurifierGuard JS'),(P3_OLD,P3_NEW,'poll state sync')]):
        if old in c:
            c = c.replace(old, new, 1); changes.append(name)
        else:
            crlf = old.replace('\n','\r\n')
            if crlf in c:
                c = c.replace(crlf, new.replace('\n','\r\n'), 1); changes.append(name+'(CRLF)')
            else:
                changes.append('❌ '+name+' pattern NOT FOUND')
    if c != orig:
        with open(fp,'w',encoding='utf-8',newline='') as f: f.write(c)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
        for ch in changes: print(f"     + {ch}")
    else:
        print(f"  ⚠️  NO CHANGES: {os.path.basename(fp)}")

for f in FILES:
    print(f"Processing: {f}")
    patch(f); print()
print('Hotovo.')
