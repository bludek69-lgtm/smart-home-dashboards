"""
PHASE 9 — Nest Hub Max speaker detail enhanced

USER: "parametry nest max dopln do dasboardu, dá se tam přehrávat i video"

Device: nest max Ložnice 2 (Google Nest Hub Max)
  Driver: com.google.chromecast:cast
  Capabilities: speaker_playing, speaker_next, speaker_prev, speaker_artist,
                speaker_track, speaker_album, volume_set, volume_mute
                + albumart image

CHANGES:
  Rozšířit existing speaker detail overlay o:
  1) Live track info (artist / track / album) — čteno přes live API
  2) Album art preview (pokud dostupný)
  3) Play/Pause toggle button
  4) Next / Prev buttons
  5) Mute toggle
  6) Note "Nest Hub Max má displej — audio + video (YouTube cast)"

Rozšíření platí pro VŠECHNY speakery kde key === 'speaker_bedroom'.
Kuchyň speaker (Nest Mini) zůstává v jednoduché formě (nemá displej).

Idempotent. Marker: PHASE9_NEST_MAX_ENHANCED_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# Replace existing speaker block s rozšířeným renderem (backward compat pro kitchen)
# ═══════════════════════════════════════════════════════════════════════════
OLD_SPEAKER = """  // Speaker — volume slider + audio controls
  if (d.type === 'speaker' && d.speakerName) {
    const vol = d.volume || 30;
    html += '<div class="dd-card">' +
      '<div class="dd-label">Hlasitost</div>' +
      '<div class="dd-slider-row">' +
        '<div class="dd-sl-icon">🔊</div>' +
        '<input type="range" min="0" max="100" value="' + vol + '"' +
          ' oninput="this.parentElement.querySelector(\\'.dd-sl-val\\').textContent=this.value+\\'%\\'"' +
          ' onchange="setDeviceCap(\\'' + d.speakerName + '\\',\\'volume_set\\',this.value/100)">' +
        '<div class="dd-sl-val">' + vol + '%</div>' +
      '</div>' +
    '</div>';
    html += '<div class="dd-card">' +
      '<div class="dd-label">Ovládání</div>' +
      '<div class="dd-onoff">' +
        '<div class="dd-btn dd-btn-on" onclick="sendReq(\\'sh_audio_request\\',\\'radio_kitchen\\');closeDeviceDetail()">🔊 Rádio</div>' +
        '<div class="dd-btn dd-btn-off" onclick="audioStop();closeDeviceDetail()">⏹ Stop</div>' +
      '</div>' +
    '</div>';
  }"""

NEW_SPEAKER = """  // PHASE9_NEST_MAX_ENHANCED_APPLIED — rozšířený speaker detail
  if (d.type === 'speaker' && d.speakerName) {
    const vol = d.volume || 30;
    const isNestMax = d.key === 'speaker_bedroom' || d.speakerName.toLowerCase().includes('nest max');
    // Album art + track info panel (jen pro Nest Max — má displej)
    if (isNestMax) {
      html += '<div class="dd-card">' +
        '<div class="dd-label">Právě hraje</div>' +
        '<div style="display:flex;gap:12px;align-items:center;">' +
          '<div id="nestmax-albumart" style="width:72px;height:72px;border-radius:10px;background:rgba(255,255,255,.06);display:flex;align-items:center;justify-content:center;font-size:32px;flex-shrink:0;">🎵</div>' +
          '<div style="flex:1;min-width:0;">' +
            '<div id="nestmax-track" style="font-size:14px;font-weight:600;color:var(--tx1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">—</div>' +
            '<div id="nestmax-artist" style="font-size:12px;color:var(--cyan);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px;">—</div>' +
            '<div id="nestmax-album" style="font-size:10px;color:var(--tx3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px;">—</div>' +
          '</div>' +
        '</div>' +
        '<div class="divider"></div>' +
        '<div class="btn-row">' +
          '<div class="btn" onclick="nestMaxPrev()">⏮ Předchozí</div>' +
          '<div class="btn primary" id="nestmax-playpause" onclick="nestMaxPlayPause()">▶/⏸ Play/Pause</div>' +
          '<div class="btn" onclick="nestMaxNext()">⏭ Další</div>' +
        '</div>' +
      '</div>';
    }
    // Volume slider + mute
    html += '<div class="dd-card">' +
      '<div class="dd-label">Hlasitost</div>' +
      '<div class="dd-slider-row">' +
        '<div class="dd-sl-icon" id="nestmax-vol-icon">🔊</div>' +
        '<input type="range" min="0" max="100" value="' + vol + '" id="nestmax-vol-slider"' +
          ' oninput="this.parentElement.querySelector(\\'.dd-sl-val\\').textContent=this.value+\\'%\\'"' +
          ' onchange="setDeviceCap(\\'' + d.speakerName + '\\',\\'volume_set\\',this.value/100)">' +
        '<div class="dd-sl-val">' + vol + '%</div>' +
      '</div>';
    if (isNestMax) {
      html += '<div class="divider"></div>' +
        '<div class="dd-onoff">' +
          '<div class="dd-btn" id="nestmax-mute-btn" onclick="nestMaxToggleMute()">🔇 Mute toggle</div>' +
        '</div>';
    }
    html += '</div>';
    // Quick actions
    html += '<div class="dd-card">' +
      '<div class="dd-label">Rychlé akce</div>' +
      '<div class="dd-onoff">' +
        '<div class="dd-btn dd-btn-on" onclick="sendReq(\\'sh_audio_request\\',\\'radio_kitchen\\');closeDeviceDetail()">🔊 Rádio</div>' +
        '<div class="dd-btn dd-btn-off" onclick="audioStop();closeDeviceDetail()">⏹ Stop všeho</div>' +
      '</div>' +
    '</div>';
    if (isNestMax) {
      html += '<div class="dd-card">' +
        '<div class="dd-label">💡 Tip — Nest Hub Max displej</div>' +
        '<div style="font-size:11px;color:var(--tx3);line-height:1.6;">' +
          'Nest Hub Max má displej — podporuje audio + video cast (YouTube, fotky, briefing). ' +
          'Rádio a TTS jdou přes <code>sh_audio_request</code>. Pro video cast použij Google Home app na mobilu ' +
          '(Cast → Nest Hub Max) nebo Homey flow <em>castVideo</em> action.' +
        '</div>' +
      '</div>';
      setTimeout(refreshNestMaxInfo, 80);
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

    # 1. Replace speaker block
    if 'PHASE9_NEST_MAX_ENHANCED_APPLIED — rozšířený speaker detail' in content:
        changes.append('⏭ Speaker detail (už applied)')
    else:
        old2 = OLD_SPEAKER.replace('\n', '\r\n') if is_crlf else OLD_SPEAKER
        new2 = NEW_SPEAKER.replace('\n', '\r\n') if is_crlf else NEW_SPEAKER
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ Speaker detail enhanced (track info + playback + mute)')
        else:
            changes.append('❌ Speaker anchor nenalezen')

    # 2. Add JS helpers (before closing </script>)
    if 'PHASE9_NEST_MAX_ENHANCED_APPLIED — JS helpers' in content:
        changes.append('⏭ JS helpers (už applied)')
    else:
        nl = '\r\n' if is_crlf else '\n'
        helpers = """// PHASE9_NEST_MAX_ENHANCED_APPLIED — JS helpers
const NESTMAX_NAME = 'nest max Ložnice 2';
async function _findNestMax() {
  if (!varMapLoaded) await loadVarMap();
  if (ALL_DEVICES && ALL_DEVICES[NESTMAX_NAME]) return { name: NESTMAX_NAME, ...ALL_DEVICES[NESTMAX_NAME] };
  if (ALL_DEVICES) {
    for (const [k, v] of Object.entries(ALL_DEVICES)) {
      const kl = k.toLowerCase();
      if (kl.includes('nest max') || (kl.includes('ložnic') && kl.includes('nest'))) return { name: k, ...v };
    }
  }
  try {
    const all = await apiGet('/api/manager/devices/device/');
    for (const [id, d] of Object.entries(all || {})) {
      const n = String(d.name || '');
      if (n.toLowerCase().includes('nest max')) {
        if (ALL_DEVICES) ALL_DEVICES[n] = { id, caps: d.capabilities || [] };
        return { name: n, id, caps: d.capabilities || [] };
      }
    }
  } catch(_){}
  return null;
}

async function refreshNestMaxInfo() {
  try {
    const d = await _findNestMax();
    if (!d) return;
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const co = detail.capabilitiesObj || {};
    const track = co.speaker_track ? (co.speaker_track.value || '') : '';
    const artist = co.speaker_artist ? (co.speaker_artist.value || '') : '';
    const album = co.speaker_album ? (co.speaker_album.value || '') : '';
    const playing = co.speaker_playing ? !!co.speaker_playing.value : false;
    const muted = co.volume_mute ? !!co.volume_mute.value : false;
    const vol = co.volume_set ? Math.round((co.volume_set.value || 0) * 100) : null;

    const set = (id, txt) => { const e = document.getElementById(id); if (e) e.textContent = txt || '—'; };
    set('nestmax-track', track || (playing ? 'Hraje' : 'Idle'));
    set('nestmax-artist', artist);
    set('nestmax-album', album);

    const ppBtn = document.getElementById('nestmax-playpause');
    if (ppBtn) ppBtn.textContent = playing ? '⏸ Pause' : '▶ Play';

    const muteBtn = document.getElementById('nestmax-mute-btn');
    if (muteBtn) muteBtn.textContent = muted ? '🔊 Unmute' : '🔇 Mute';
    const volIcon = document.getElementById('nestmax-vol-icon');
    if (volIcon) volIcon.textContent = muted ? '🔇' : '🔊';

    // Album art — jen pokud existuje URL
    const art = document.getElementById('nestmax-albumart');
    if (art && detail.images && Array.isArray(detail.images)) {
      const imgObj = detail.images.find(i => /albumart|album/i.test(i.type || ''));
      if (imgObj && imgObj.imageObj && imgObj.imageObj.url) {
        art.innerHTML = '<img src="' + imgObj.imageObj.url + '" style="width:100%;height:100%;object-fit:cover;border-radius:10px;" onerror="this.outerHTML=\\'🎵\\'">';
      } else {
        art.innerHTML = '🎵';
      }
    }

    const volSlider = document.getElementById('nestmax-vol-slider');
    if (volSlider && vol !== null) {
      volSlider.value = vol;
      const valEl = volSlider.parentElement.querySelector('.dd-sl-val');
      if (valEl) valEl.textContent = vol + '%';
    }
  } catch(_){}
}

async function nestMaxPlayPause() {
  try {
    const d = await _findNestMax();
    if (!d) { try { flash('⚠ Nest Max nenalezen'); } catch(_){}; return; }
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const playing = detail.capabilitiesObj && detail.capabilitiesObj.speaker_playing ? !!detail.capabilitiesObj.speaker_playing.value : false;
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/speaker_playing', { value: !playing });
    try { flash(!playing ? '▶ Play' : '⏸ Pause'); } catch(_){}
    setTimeout(refreshNestMaxInfo, 400);
  } catch(e) { try { flash('✗ ' + e.message); } catch(_){} }
}

async function nestMaxNext() {
  try {
    const d = await _findNestMax();
    if (!d) return;
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/speaker_next', { value: true });
    try { flash('⏭ Další'); } catch(_){}
    setTimeout(refreshNestMaxInfo, 400);
  } catch(_){}
}

async function nestMaxPrev() {
  try {
    const d = await _findNestMax();
    if (!d) return;
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/speaker_prev', { value: true });
    try { flash('⏮ Předchozí'); } catch(_){}
    setTimeout(refreshNestMaxInfo, 400);
  } catch(_){}
}

async function nestMaxToggleMute() {
  try {
    const d = await _findNestMax();
    if (!d) return;
    const detail = await apiGet('/api/manager/devices/device/' + d.id);
    const muted = detail.capabilitiesObj && detail.capabilitiesObj.volume_mute ? !!detail.capabilitiesObj.volume_mute.value : false;
    await apiPut('/api/manager/devices/device/' + d.id + '/capability/volume_mute', { value: !muted });
    try { flash(muted ? '🔊 Unmute' : '🔇 Mute'); } catch(_){}
    setTimeout(refreshNestMaxInfo, 400);
  } catch(_){}
}

"""
        anchor = '</script>'
        if anchor in content:
            inj = helpers.replace('\n', '\r\n') if is_crlf else helpers
            # insert before last </script>
            idx = content.rfind(anchor)
            if idx >= 0:
                content = content[:idx] + inj + content[idx:]
                changes.append('+ JS helpers (_findNestMax, refreshNestMaxInfo, playPause/next/prev/mute)')
            else:
                changes.append('❌ </script> not found')
        else:
            changes.append('❌ </script> not found')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 9 — Nest Hub Max enhanced detail')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
