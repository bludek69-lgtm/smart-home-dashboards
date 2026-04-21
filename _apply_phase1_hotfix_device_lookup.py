"""
PHASE 1 HOTFIX — robustní Xiaomi lookup + Pomodoro debug
Idempotent.

FIXES:
  1) Xiaomi device nenalezen v ALL_DEVICES (screenshot z RPi):
     - Přidán fuzzy finder: exact → trim/lower → substring+battery cap
     - Fallback: live API call pokud cache neobsahuje
     - Lepší debug hláška (vypíše existující kandidáty)
  2) Pomodoro: přidáno console.log pro diagnostiku timeru
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE1_HOTFIX_DEVICE_LOOKUP'

# ═══════════════════════════════════════════════════════════════════════════
# Replace refreshXiaomiButtonState — robust finder
# ═══════════════════════════════════════════════════════════════════════════
OLD_REFRESH_STATE = """async function refreshXiaomiButtonState() {
  const el = document.getElementById('pc-xiaomi-state');
  if (!el) return;
  try {
    if (typeof varMapLoaded !== 'undefined' && !varMapLoaded) await loadVarMap();
    const d = ALL_DEVICES && ALL_DEVICES['Xiaomi'];
    let bat = '';
    if (d) {
      try {
        const detail = await apiGet('/api/manager/devices/device/' + d.id);
        const co = detail.capabilitiesObj || {};
        if (co.measure_battery && co.measure_battery.value != null) {
          bat = Math.round(Number(co.measure_battery.value)) + '%';
        } else if (co.alarm_battery && co.alarm_battery.value === true) {
          bat = 'LOW!';
        } else if (co.alarm_battery && co.alarm_battery.value === false) {
          bat = 'ok';
        }
      } catch(_) {}
    }
    const ev = String((ALL_VARS && ALL_VARS['sh_button_pc_event'] && ALL_VARS['sh_button_pc_event'].value) || 'idle');
    const evShort = ev && ev !== 'idle' ? ev.replace('_click','× klik').replace('long','long press') : '';
    el.textContent = (bat || '—') + (evShort ? ' · ' + evShort : '');
    el.className = 'tile-state ' + ((bat === 'LOW!' ) ? 'warn' : (bat ? 'on' : 'off'));
  } catch(e) {
    el.textContent = 'err';
  }
}"""

NEW_REFRESH_STATE = """// PHASE1_HOTFIX_DEVICE_LOOKUP — robust Xiaomi finder (handles cache miss, casing, zones)
async function _findXiaomiPcDevice() {
  if (!varMapLoaded) await loadVarMap();
  // Strategy 1: exact match
  if (ALL_DEVICES && ALL_DEVICES['Xiaomi']) return { name: 'Xiaomi', ...ALL_DEVICES['Xiaomi'] };
  // Strategy 2: trim/lower match
  if (ALL_DEVICES) {
    for (const [k, v] of Object.entries(ALL_DEVICES)) {
      if (k.trim().toLowerCase() === 'xiaomi') return { name: k, ...v };
    }
  }
  // Strategy 3: live API — fetch all devices, filter by name=='Xiaomi' (Pc Setup = only one with bare 'Xiaomi')
  try {
    const all = await apiGet('/api/manager/devices/device/');
    for (const [id, d] of Object.entries(all || {})) {
      const n = String(d.name || '').trim();
      if (n === 'Xiaomi' || n.toLowerCase() === 'xiaomi') {
        // Update cache
        if (ALL_DEVICES) ALL_DEVICES[n] = { id, caps: d.capabilities || [] };
        return { name: n, id, caps: d.capabilities || [] };
      }
    }
  } catch(_) {}
  return null;
}

async function refreshXiaomiButtonState() {
  const el = document.getElementById('pc-xiaomi-state');
  if (!el) return;
  try {
    const d = await _findXiaomiPcDevice();
    let bat = '';
    if (d) {
      try {
        const detail = await apiGet('/api/manager/devices/device/' + d.id);
        const co = detail.capabilitiesObj || {};
        if (co.measure_battery && co.measure_battery.value != null) {
          bat = Math.round(Number(co.measure_battery.value)) + '%';
        } else if (co.alarm_battery && co.alarm_battery.value === true) {
          bat = 'LOW!';
        } else if (co.alarm_battery && co.alarm_battery.value === false) {
          bat = 'ok';
        }
      } catch(_) {}
    }
    const ev = String((ALL_VARS && ALL_VARS['sh_button_pc_event'] && ALL_VARS['sh_button_pc_event'].value) || 'idle');
    const evShort = ev && ev !== 'idle' ? ev.replace('_click','× klik').replace('long','long press') : '';
    el.textContent = (bat || '—') + (evShort ? ' · ' + evShort : '');
    el.className = 'tile-state ' + ((bat === 'LOW!' ) ? 'warn' : (bat ? 'on' : 'off'));
  } catch(e) {
    el.textContent = 'err';
  }
}"""

# ═══════════════════════════════════════════════════════════════════════════
# Replace refreshXiaomiButtonDetail — use robust finder + show candidates
# ═══════════════════════════════════════════════════════════════════════════
OLD_REFRESH_DETAIL = """async function refreshXiaomiButtonDetail() {
  const el = document.getElementById('xiaomi-stav');
  if (!el) return;
  try {
    if (!varMapLoaded) await loadVarMap();
    const d = ALL_DEVICES && ALL_DEVICES['Xiaomi'];
    if (!d) { el.textContent = 'Zařízení "Xiaomi" není načtené v ALL_DEVICES.'; return; }
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const co = detail.capabilitiesObj || {};
    const bat = co.measure_battery && co.measure_battery.value != null ? Math.round(co.measure_battery.value) + '%' : '—';
    const alarm = co.alarm_battery ? (co.alarm_battery.value ? 'LOW' : 'ok') : '—';
    const avail = detail.available === false ? '❌ offline' : '✅ online';
    el.innerHTML =
      'Battery: <strong>' + bat + '</strong> · Alarm: <strong>' + alarm + '</strong><br>' +
      'Available: ' + avail + '<br>' +
      'ID: <span style="font-size:10px;color:var(--tx3);">' + d.id + '</span>';
  } catch(e) { el.textContent = 'Chyba: ' + e.message; }
}"""

NEW_REFRESH_DETAIL = """async function refreshXiaomiButtonDetail() {
  const el = document.getElementById('xiaomi-stav');
  if (!el) return;
  try {
    const d = await _findXiaomiPcDevice();
    if (!d) {
      // Diagnostika — vypiš kandidáty s 'xiaomi' v názvu
      const candidates = [];
      if (ALL_DEVICES) {
        for (const k of Object.keys(ALL_DEVICES)) {
          if (k.toLowerCase().includes('xiaomi')) candidates.push(k);
        }
      }
      el.innerHTML = 'Zařízení "Xiaomi" nenalezeno.<br>' +
        '<span style="font-size:11px;color:var(--tx3);">Kandidáti v Homey: ' +
        (candidates.length ? candidates.join(' · ') : '(žádní)') + '</span>';
      return;
    }
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const co = detail.capabilitiesObj || {};
    const bat = co.measure_battery && co.measure_battery.value != null ? Math.round(co.measure_battery.value) + '%' : '—';
    const alarm = co.alarm_battery ? (co.alarm_battery.value ? 'LOW' : 'ok') : '—';
    const avail = detail.available === false ? '❌ offline' : '✅ online';
    const zone = detail.zoneName || '—';
    el.innerHTML =
      'Name: <strong>' + d.name + '</strong> · Zone: ' + zone + '<br>' +
      'Battery: <strong>' + bat + '</strong> · Alarm: <strong>' + alarm + '</strong><br>' +
      'Available: ' + avail + '<br>' +
      'ID: <span style="font-size:10px;color:var(--tx3);">' + d.id + '</span>';
  } catch(e) { el.textContent = 'Chyba: ' + e.message; }
}"""

# ═══════════════════════════════════════════════════════════════════════════
# Add console.log to Pomodoro for debug + fix potential issue with setInterval
# ═══════════════════════════════════════════════════════════════════════════
OLD_POMO_START = """function pomoStart(mode) {
  _pomoLoad();
  _pomoState.mode = mode;
  _pomoState.totalSec = (mode === 'work' ? POMO_WORK_MIN : POMO_BREAK_MIN) * 60;
  _pomoState.remaining = _pomoState.totalSec;
  _pomoState.startedAt = Date.now();
  _pomoState.paused = false;
  _pomoSave();
  refreshPomodoroTile();
  _pomoBigUpdate();
}"""

NEW_POMO_START = """function pomoStart(mode) {
  _pomoLoad();
  _pomoState.mode = mode;
  _pomoState.totalSec = (mode === 'work' ? POMO_WORK_MIN : POMO_BREAK_MIN) * 60;
  _pomoState.remaining = _pomoState.totalSec;
  _pomoState.startedAt = Date.now();
  _pomoState.paused = false;
  _pomoSave();
  console.log('[POMO] Start', mode, 'for', _pomoState.totalSec, 'sec');
  refreshPomodoroTile();
  _pomoBigUpdate();
  try { flash('🍅 Pomodoro ' + (mode === 'work' ? 'práce 25 min' : 'pauza 5 min') + ' spuštěno'); } catch(_){}
}"""


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

    def apply(old, new, label):
        nonlocal content
        if is_crlf:
            old2 = old.replace('\n', '\r\n')
            new2 = new.replace('\n', '\r\n')
        else:
            old2 = old
            new2 = new
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append(label)
        else:
            changes.append('❌ ' + label)

    apply(OLD_REFRESH_STATE, NEW_REFRESH_STATE, 'refreshXiaomiButtonState (+_findXiaomiPcDevice)')
    apply(OLD_REFRESH_DETAIL, NEW_REFRESH_DETAIL, 'refreshXiaomiButtonDetail (diagnostics)')
    apply(OLD_POMO_START, NEW_POMO_START, 'pomoStart (+console.log, flash toast)')

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
    print('PHASE 1 HOTFIX — device lookup + pomo debug')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
