"""
PHASE 8 — Logy page compact layout + Bedroom Nest Max speaker

USER FEEDBACK:
  1) Logy stránku taky upravit bez scrollu
  2) V ložnici musí být audio abych mohl ovládat nest max Ložnice 2

CHANGES:

A) Bedroom:
   - Přidat tile 🔊 "Nest Hub Max" do unified grid (mezi Zvlhčovač a TV remote)
   - Kliknutí otevře existující speaker detail overlay (volume slider + audio controls)
   - Odstranit starý inline audio note (nahradit jednoduchou zmínkou u TTS routing)

B) Logy page:
   - Zkrátit verbose help panel
   - AI Tasks + AI Pending → 2-sloupcový grid (úspora výšky)
   - Kompaktnější event log summary
   - Tightened padding

Idempotent. Marker: PHASE8_LOGY_BEDROOM_SPEAKER_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: Extend bedroom unified grid — add Nest Max speaker tile
# Anchor: TV remote tile injection (existing PHASE7 block)
# ═══════════════════════════════════════════════════════════════════════════
OLD_BEDROOM_GRID = """    // TV remote tile (in same grid)
    html += '<div class="dev-tile" id="bed-tv-tile" onclick="openTvRemote()">' +
      '<div class="tile-icon">📺</div>' +
      '<div class="tile-name">TV remote</div>' +
      '<div class="tile-state off" id="bed-tv-state">—</div>' +
    '</div>';
    html += '</div>';
    setTimeout(refreshTvTile, 120);
    // Small audio note (no standalone card)
    html += '<div style="font-size:10px;color:var(--tx3);padding:6px 10px;text-align:center;background:rgba(255,255,255,.03);border-radius:8px;margin-top:4px;">🔊 Audio (TTS, briefing, rádio) → přes reproduktor Kuchyň</div>';
  }"""

NEW_BEDROOM_GRID = """    // TV remote tile (in same grid)
    html += '<div class="dev-tile" id="bed-tv-tile" onclick="openTvRemote()">' +
      '<div class="tile-icon">📺</div>' +
      '<div class="tile-name">TV remote</div>' +
      '<div class="tile-state off" id="bed-tv-state">—</div>' +
    '</div>';
    // PHASE8_LOGY_BEDROOM_SPEAKER_APPLIED — Nest Hub Max speaker tile
    (function() {
      const a = DATA?.audio || {};
      const activeSpk = String(a.speaker || '').toLowerCase();
      const isNestPlaying = activeSpk.includes('ložnic') || activeSpk.includes('loznic') || activeSpk.includes('nest max');
      const spkPlaying = a.playing === 'yes' && isNestPlaying;
      const tIdx = _tileData.length;
      _tileData.push({key:'speaker_bedroom', name:'nest max Ložnice 2', rawName:'nest max Ložnice 2',
        icon:'🔊', type:'speaker', on:spkPlaying,
        dim:null, hasDim:false, hasTemp:false, temp:null, power:null, plugTemp:null,
        speakerName:'nest max Ložnice 2', volume:30});
      html += '<div class="dev-tile' + (spkPlaying ? ' tile-on' : '') + '" onclick="openDeviceDetail(_tileData[' + tIdx + '])">' +
        '<div class="tile-icon">🔊</div>' +
        '<div class="tile-name">Nest Hub Max</div>' +
        '<div class="tile-state ' + (spkPlaying ? 'on' : 'off') + '">' + (spkPlaying ? 'hraje' : 'idle') + '</div>' +
      '</div>';
    })();
    html += '</div>';
    setTimeout(refreshTvTile, 120);
    // Small note — TTS routing
    html += '<div style="font-size:10px;color:var(--tx3);padding:6px 10px;text-align:center;background:rgba(255,255,255,.03);border-radius:8px;margin-top:4px;">🔔 TTS / briefing primárně → Kuchyň (policy v6.0). Nest Hub Max = opt-in pro manuální audio.</div>';
  }"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH B: Logy page — compact 2-column layout for AI Tasks + Pending
# ═══════════════════════════════════════════════════════════════════════════
OLD_LOGY_LAYOUT = """    <div id="help-logy" class="help-panel">
      <h4>📊 Co je na této stránce</h4>
      <ul>
        <li><strong>AI Tasks</strong> — otevřené úkoly z Google Sheets</li>
        <li><strong>AI Pending Changes</strong> — změny čekající na schválení</li>
        <li><strong>Event Log</strong> — posledních 24h událostí</li>
      </ul>
    </div>

    <div class="sect" style="color:var(--purple);">AI TASKS (GOOGLE SHEETS)</div>
    <div class="card">
      <div class="card-row"><span class="card-icon">📋</span><span class="card-lbl">Otevřené úkoly</span><div class="btn cyan" onclick="loadAITasks()" style="padding:4px 10px;font-size:10px;">⟳ Načíst</div></div>
      <div id="aiTasksList" style="margin-top:8px;font-family:var(--mono);font-size:10px;color:var(--tx3);">Klikni ⟳ pro načtení</div>
    </div>

    <div class="sect" style="color:var(--purple);">AI PENDING CHANGES</div>
    <div class="card">
      <div class="card-row"><span class="card-icon">⏳</span><span class="card-lbl">Čekající změny (48h okno)</span></div>
      <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);">—</div>
    </div>

    <div class="sect" style="color:var(--purple);">EVENT LOG · DIAGNOSTIKA</div>"""

NEW_LOGY_LAYOUT = """    <div id="help-logy" class="help-panel">
      <p style="margin:0;font-size:11px;line-height:1.5;"><strong>AI Tasks</strong> · otevřené úkoly ze Sheets · <strong>AI Pending</strong> · čekající změny · <strong>Event Log</strong> · posledních 24h · <strong>Grafy</strong> · Lux/Battery · <strong>AI Tune</strong> · morning routine doporučení</p>
    </div>

    <!-- PHASE8_LOGY_BEDROOM_SPEAKER_APPLIED — 2-col compact layout -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI TASKS</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">📋</span><span class="card-lbl">Otevřené</span><div class="btn cyan" onclick="loadAITasks()" style="padding:3px 8px;font-size:10px;">⟳</div></div>
          <div id="aiTasksList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:140px;overflow-y:auto;scrollbar-width:thin;">Klikni ⟳</div>
        </div>
      </div>
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI PENDING</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">⏳</span><span class="card-lbl">Čekající (48h)</span></div>
          <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:140px;overflow-y:auto;scrollbar-width:thin;">—</div>
        </div>
      </div>
    </div>

    <div class="sect" style="color:var(--purple);">EVENT LOG · DIAGNOSTIKA</div>"""

# Compact event log section — reduce max-height + inline stats
OLD_EVENT_LOG = """    <div class="card" id="eventlog-stats" style="font-family:var(--mono);font-size:11px;color:var(--tx2);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="color:var(--purple);font-weight:600;">📊 Posledních 24h</span>
        <div class="btn" onclick="fetchEventLog()" style="padding:3px 8px;font-size:9px;">↻ Obnovit</div>
      </div>
      <div id="el-summary" style="color:var(--tx3);">Klikni ↻ pro načtení...</div>
    </div>
    <div class="card" id="eventlog-recent" style="font-family:var(--mono);font-size:10px;display:none;max-height:400px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--bg4) transparent;">
      <div style="color:var(--purple);font-weight:600;margin-bottom:4px;">📋 Poslední události</div>
      <div id="el-rows"></div>
    </div>"""

NEW_EVENT_LOG = """    <div class="card" id="eventlog-stats" style="font-family:var(--mono);font-size:11px;color:var(--tx2);padding:10px 12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <span style="color:var(--purple);font-weight:600;">📊 24h</span>
        <div class="btn" onclick="fetchEventLog()" style="padding:3px 8px;font-size:9px;">↻</div>
      </div>
      <div id="el-summary" style="color:var(--tx3);">Klikni ↻</div>
    </div>
    <div class="card" id="eventlog-recent" style="font-family:var(--mono);font-size:10px;display:none;max-height:200px;overflow-y:auto;scrollbar-width:thin;scrollbar-color:var(--bg4) transparent;padding:10px 12px;">
      <div style="color:var(--purple);font-weight:600;margin-bottom:4px;">📋 Poslední</div>
      <div id="el-rows"></div>
    </div>"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH C: Compact AI Tune panel + charts tighter
# ═══════════════════════════════════════════════════════════════════════════
OLD_TUNE = """    <div class="sect" style="color:var(--purple);margin-top:8px;">📊 AI TUNE</div>
    <div class="card" id="morningTuneCard" style="padding:8px;min-height:80px;">
      <div style="color:var(--tx3);text-align:center;padding:16px 0;">⟳</div>
    </div>
    <div style="display:flex;gap:6px;margin-top:6px;">
      <div class="btn" style="flex:1;text-align:center;font-size:10px;" onclick="loadMorningTune()">⟳ Show</div>
      <div class="btn" style="flex:1;text-align:center;font-size:10px;border-color:var(--purple);color:var(--purple);" onclick="runMorningTune()">🧠 Gemini</div>
    </div>

    <div style="height:10px;"></div>
  </div>"""

NEW_TUNE = """    <div class="sect" style="color:var(--purple);margin-top:8px;">📊 AI TUNE (MORNING)</div>
    <div style="display:grid;grid-template-columns:1fr auto auto;gap:6px;align-items:start;">
      <div class="card" id="morningTuneCard" style="padding:8px 10px;min-height:60px;">
        <div style="color:var(--tx3);text-align:center;padding:10px 0;">⟳</div>
      </div>
      <div class="btn" style="text-align:center;font-size:10px;align-self:stretch;display:flex;align-items:center;padding:0 14px;" onclick="loadMorningTune()">⟳ Show</div>
      <div class="btn" style="text-align:center;font-size:10px;border-color:var(--purple);color:var(--purple);align-self:stretch;display:flex;align-items:center;padding:0 14px;" onclick="runMorningTune()">🧠 Gemini</div>
    </div>

    <div style="height:6px;"></div>
  </div>"""


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

    # A: Bedroom speaker
    replace(OLD_BEDROOM_GRID, NEW_BEDROOM_GRID, 'Bedroom Nest Max speaker tile',
            marker='PHASE8_LOGY_BEDROOM_SPEAKER_APPLIED — Nest Hub Max speaker tile')

    # B: Logy layout
    replace(OLD_LOGY_LAYOUT, NEW_LOGY_LAYOUT, 'Logy: 2-col AI Tasks + Pending',
            marker='PHASE8_LOGY_BEDROOM_SPEAKER_APPLIED — 2-col compact layout')

    # Event log compact
    replace(OLD_EVENT_LOG, NEW_EVENT_LOG, 'Logy: compact Event Log')

    # AI Tune compact
    replace(OLD_TUNE, NEW_TUNE, 'Logy: compact AI Tune')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 8 — Logy compact + Bedroom speaker')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
