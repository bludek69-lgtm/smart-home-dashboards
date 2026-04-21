"""
PHASE 3 CLEANUP — odstranit dead code po native caps hotfix
Idempotent. Marker: PHASE3_CLEANUP_DEAD_CODE_APPLIED.

CONTEXT:
  Po _apply_phase3_hotfix_native_tv_caps.py zůstal nepoužitý kód:
    - const TV_CMD_VAR = 'sh_tv_remote_cmd'  (už není kam referencováno)
    - async function _tvSendCmd(cmd) { ... }  (žádná tvXxx() funkce ji už nevolá)
    - komentáře o dispatcher flow

REMOVES:
  - TV_CMD_VAR const
  - _tvSendCmd() funkce (celý blok)
  - Staré komentáře o sh_tv_remote_cmd
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE3_CLEANUP_DEAD_CODE_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: Remove TV_CMD_VAR const line
# ═══════════════════════════════════════════════════════════════════════════
OLD_CMD_VAR = """const TV_DEVICE_NAME = 'Televize v ložnici';
const TV_CMD_VAR = 'sh_tv_remote_cmd';
"""
NEW_CMD_VAR = """const TV_DEVICE_NAME = 'Televize v ložnici';
// PHASE3_CLEANUP_DEAD_CODE_APPLIED — TV_CMD_VAR removed (unused after native caps hotfix)
"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: Remove _tvSendCmd function block + its comments
# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
# PATCH 3: Remove _tvSendCmd fallbacks from tvMute/tvVolUp/tvVolDown/tvVolSet
# (all volume_* capabilities are confirmed native for com.android.tv:remote)
# ═══════════════════════════════════════════════════════════════════════════
OLD_VOL_BLOCK = """async function tvMute() {
  if (await _tvHasCap('volume_mute')) {
    const data = await _tvGetDetail(true);
    const cur = data && data.detail.capabilitiesObj.volume_mute ? !!data.detail.capabilitiesObj.volume_mute.value : false;
    await _tvSetCap('volume_mute', !cur);
  } else { _tvSendCmd('mute'); }
  setTimeout(refreshTvOverlay, 300);
}
async function tvVolUp() {
  if (await _tvHasCap('volume_up')) await _tvSetCap('volume_up', true);
  else { _tvSendCmd('vol_up'); }
  setTimeout(refreshTvOverlay, 300);
}
async function tvVolDown() {
  if (await _tvHasCap('volume_down')) await _tvSetCap('volume_down', true);
  else { _tvSendCmd('vol_down'); }
  setTimeout(refreshTvOverlay, 300);
}
async function tvVolSet(pct) {
  if (await _tvHasCap('volume_set')) await _tvSetCap('volume_set', Number(pct)/100);
  else _tvSendCmd('vol_' + Math.round(pct));
}"""

NEW_VOL_BLOCK = """async function tvMute() {
  const data = await _tvGetDetail(true);
  const cur = data && data.detail.capabilitiesObj.volume_mute ? !!data.detail.capabilitiesObj.volume_mute.value : false;
  await _tvSetCap('volume_mute', !cur);
  setTimeout(refreshTvOverlay, 300);
}
async function tvVolUp() { await _tvSetCap('volume_up', true); setTimeout(refreshTvOverlay, 300); }
async function tvVolDown() { await _tvSetCap('volume_down', true); setTimeout(refreshTvOverlay, 300); }
async function tvVolSet(pct) { await _tvSetCap('volume_set', Number(pct)/100); }"""

OLD_SEND_CMD = """// Write to sh_tv_remote_cmd variable (fallback for non-capability actions)
// Homey flow on user side: QUANDO sh_tv_remote_cmd è cambiata → dispatch
async function _tvSendCmd(cmd) {
  try {
    if (!varMapLoaded) await loadVarMap();
    const v = ALL_VARS && ALL_VARS[TV_CMD_VAR];
    if (!v) {
      try { flash('⚠ Proměnná ' + TV_CMD_VAR + ' chybí. Vytvoř ji v Homey (string).'); } catch(_){}
      return false;
    }
    // Reset to idle first (so same cmd can fire repeatedly)
    await writeVar(TV_CMD_VAR, 'idle');
    await writeVar(TV_CMD_VAR, cmd);
    try { flash('📺 ' + cmd); } catch(_){}
    return true;
  } catch(e) {
    try { flash('✗ ' + e.message); } catch(_){}
    return false;
  }
}

"""

NEW_SEND_CMD = """// PHASE3_CLEANUP_DEAD_CODE_APPLIED — _tvSendCmd removed (replaced by native caps)
"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP (not found): {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    # Každý replace je individuálně idempotentní (OLD not found = skip)
    orig = content
    changes = []
    is_crlf = '\r\n' in content[:4096]

    def replace(old, new, label):
        nonlocal content
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append(label)
        else:
            changes.append('❌ ' + label + ' (not found)')

    replace(OLD_CMD_VAR, NEW_CMD_VAR, 'Remove TV_CMD_VAR const')
    replace(OLD_SEND_CMD, NEW_SEND_CMD, 'Remove _tvSendCmd function')
    replace(OLD_VOL_BLOCK, NEW_VOL_BLOCK, 'Simplify tvMute/tvVolUp/tvVolDown/tvVolSet (drop _tvSendCmd fallbacks)')

    # ❌ (not found) = už aplikováno DŘÍVE, ne chyba. Save pokud se něco změnilo.
    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
        for c in changes:
            icon = '⏭️' if c.startswith('❌') else '+'
            label = c.replace('❌ ', '').replace(' (not found)', ' (už applied)') if c.startswith('❌') else c
            print(f"     {icon} {label}")
    else:
        print(f"  ⏭️  NO CHANGE (all already applied): {os.path.basename(fp)}")


if __name__ == '__main__':
    print('PHASE 3 CLEANUP — remove dead code')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
