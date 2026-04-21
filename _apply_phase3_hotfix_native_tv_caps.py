"""
PHASE 3 HOTFIX — native TV capabilities místo sh_tv_remote_cmd dispatcher

CONTEXT:
  Phase 3 originálně routovalo channel/arrows/home/back/numpad přes proměnnou
  sh_tv_remote_cmd + Homey dispatcher flow. Uživatel ověřil že Televize v ložnici
  (driver com.android.tv:remote) má VŠECHNY klávesy jako native Homey capabilities:
    key_cursor_up/down/left/right, key_confirm, key_back, key_home,
    key_channel_up/down, key_digit_0..9, key_play, key_pause, key_stop, key_watch_tv

FIX:
  Každá tvXxx() funkce volá _tvSetCap(<cap>, true) přímo. Žádná proměnná,
  žádný dispatcher flow, žádná redundance.

MARKER: PHASE3_HOTFIX_NATIVE_CAPS_APPLIED
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE3_HOTFIX_NATIVE_CAPS_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: Replace dispatcher-based functions with native capability calls
# ═══════════════════════════════════════════════════════════════════════════
OLD_BLOCK = """async function tvStop() { _tvSendCmd('stop'); }
async function tvNext() {
  if (await _tvHasCap('speaker_next')) await _tvSetCap('speaker_next', true);
  else _tvSendCmd('next');
}
async function tvPrev() {
  if (await _tvHasCap('speaker_prev')) await _tvSetCap('speaker_prev', true);
  else _tvSendCmd('prev');
}
// Channel/nav — fallback to variable (user maps to Android TV flow actions)
function tvChUp() { _tvSendCmd('channel_up'); }
function tvChDown() { _tvSendCmd('channel_down'); }
function tvUp() { _tvSendCmd('up'); }
function tvDown() { _tvSendCmd('down'); }
function tvLeft() { _tvSendCmd('left'); }
function tvRight() { _tvSendCmd('right'); }
function tvOk() { _tvSendCmd('ok'); }
function tvHome() { _tvSendCmd('home'); }
function tvBack() { _tvSendCmd('back'); }
function tvDigit(n) { _tvSendCmd('digit_' + n); }"""

NEW_BLOCK = """// PHASE3_HOTFIX_NATIVE_CAPS_APPLIED — přímé capability volání místo dispatcher var
async function tvStop() { await _tvSetCap('key_stop', true); }
async function tvNext() { await _tvSetCap('key_next', true); }
async function tvPrev() { await _tvSetCap('key_previous', true); }
// D-pad + nav + channel + numpad — všechny native booleovské capabilities
async function tvChUp() { await _tvSetCap('key_channel_up', true); }
async function tvChDown() { await _tvSetCap('key_channel_down', true); }
async function tvUp() { await _tvSetCap('key_cursor_up', true); }
async function tvDown() { await _tvSetCap('key_cursor_down', true); }
async function tvLeft() { await _tvSetCap('key_cursor_left', true); }
async function tvRight() { await _tvSetCap('key_cursor_right', true); }
async function tvOk() { await _tvSetCap('key_confirm', true); }
async function tvHome() { await _tvSetCap('key_home', true); }
async function tvBack() { await _tvSetCap('key_back', true); }
async function tvDigit(n) { await _tvSetCap('key_digit_' + n, true); }
async function tvWatchTv() { await _tvSetCap('key_watch_tv', true); }"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: tvPlayPause — use key_play / key_pause instead of speaker_playing toggle
# (cleaner, matches the same capability namespace)
# ═══════════════════════════════════════════════════════════════════════════
OLD_PLAYPAUSE = """async function tvPlayPause() {
  if (await _tvHasCap('speaker_playing')) {
    const data = await _tvGetDetail(true);
    const cur = data && data.detail.capabilitiesObj.speaker_playing ? !!data.detail.capabilitiesObj.speaker_playing.value : false;
    await _tvSetCap('speaker_playing', !cur);
  } else _tvSendCmd('play_pause');
}"""

NEW_PLAYPAUSE = """async function tvPlayPause() {
  // Android TV driver má speaker_playing (play/pause toggle) i key_play/key_pause
  if (await _tvHasCap('speaker_playing')) {
    const data = await _tvGetDetail(true);
    const cur = data && data.detail.capabilitiesObj.speaker_playing ? !!data.detail.capabilitiesObj.speaker_playing.value : false;
    await _tvSetCap('speaker_playing', !cur);
  } else {
    // Fallback na dedikované key_play / key_pause
    const data = await _tvGetDetail(true);
    const playing = data && data.detail.capabilitiesObj.key_play ? !!data.detail.capabilitiesObj.key_play.value : false;
    await _tvSetCap(playing ? 'key_pause' : 'key_play', true);
  }
}"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 3: Update footer text in openTvRemote overlay (remove sh_tv_remote_cmd ref)
# ═══════════════════════════════════════════════════════════════════════════
OLD_FOOTER = """'<div class="dd-card">' +
      '<div class="dd-label">Info</div>' +
      '<div style="font-size:11px;color:var(--tx3);line-height:1.6;">' +
        '<strong>Power/Vol/Play</strong> jdou přímo na TV capabilities.<br>' +
        '<strong>Channel/Arrows/Home/Back/Numpad</strong> píšou do <code>sh_tv_remote_cmd</code> — ' +
        'vytvoř v Homey flow dispatcher (QUANDO cmd cambiata → Android TV flow action).' +
      '</div>' +
    '</div>';"""

NEW_FOOTER = """'<div class="dd-card">' +
      '<div class="dd-label">Info</div>' +
      '<div style="font-size:11px;color:var(--tx3);line-height:1.6;">' +
        'Všechna tlačítka volají přímo Homey capabilities driveru <code>com.android.tv:remote</code>.<br>' +
        'Žádný dispatcher flow není potřeba — <code>key_home</code>, <code>key_cursor_*</code>, ' +
        '<code>key_channel_up/down</code>, <code>key_digit_0..9</code> jsou všechny native.' +
      '</div>' +
    '</div>';"""


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

    def replace(old, new, label):
        nonlocal content
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append(label)
        else:
            changes.append('❌ ' + label + ' (not found)')

    replace(OLD_BLOCK, NEW_BLOCK, 'Channel/Nav/Numpad → native capabilities')
    replace(OLD_PLAYPAUSE, NEW_PLAYPAUSE, 'tvPlayPause refactor')
    replace(OLD_FOOTER, NEW_FOOTER, 'Footer info text update')

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
    print('PHASE 3 HOTFIX — native TV capabilities')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
