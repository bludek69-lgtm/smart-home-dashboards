"""
Phase 22 (2026-04-21) — Missing helps + refactor staré

Cíl: přidat helpy pro 8 kritických sekcí + opravit help-logy (byl staršího formátu).

Sekce které dostanou help:
  - TTS PIPELINE → help-tts-pipeline
  - 🤖 GEMINI DIAGNOSTIKA → help-gemini-diag
  - AI PENDING → help-ai-pending
  - OFFLINE ZAŘÍZENÍ → help-offline
  - 📦 LOG SNAPSHOTS → help-log-snapshots
  - 💡 LUX 24h → help-lux24
  - EVENT LOG · DIAGNOSTIKA → help-eventlog
  - 🔋 BATTERY → help-battery
  - PŘEDPOVĚĎ · 3 DNY → help-weather3d
  - 📊 AI TUNE (MORNING) → help-ai-tune

Refactor:
  - help-logy — přidat h4 + ul strukturu (konzistence)

Idempotentní — marker help-tts-pipeline.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'help-tts-pipeline'

# ═══════════════════════════════════════════════════════════════════════════
# Helper: wrap plain <div class="sect">TEXT</div> with help header + panel
# ═══════════════════════════════════════════════════════════════════════════
def wrap_sect(old_sect_text, help_id, panel_html):
    """Vytvoří replacement: plain sect → sect s help-btn + panel."""
    new = (
        f'<div class="sect" style="color:var(--orange);">\n'
        f'      <span class="help-sect-header">\n'
        f'        <span>{old_sect_text}</span>\n'
        f'        <button class="help-btn" data-help-for="{help_id}" onclick="toggleHelp(\'{help_id}\')">ℹ</button>\n'
        f'      </span>\n'
        f'    </div>\n'
        f'    <div id="{help_id}" class="help-panel">{panel_html}</div>'
    )
    return new


HELPS = [
    # (sect_text_to_find, help_id, panel_content)
    ('TTS PIPELINE', 'help-tts-pipeline',
     '<h4>🗣 TTS pipeline — jak se tvoří mluvený hlas</h4>'
     '<ul>'
     '<li><strong>1. Žádost</strong>: skript zapíše text do <code>sh_tts_text</code> + speaker do <code>sh_tts_speaker</code></li>'
     '<li><strong>2. Priorita</strong>: <code>sh_audio_brain_v2</code> rozhodne kdo má přednost (morning_briefing=90, kitchen_alert=55, radio=50)</li>'
     '<li><strong>3. Cast</strong>: Flow volá Google Cast na Kuchyň speaker</li>'
     '<li><strong>Limit</strong>: 200 znaků per utterance (Google Cast TTS SDK). Delší text = split (briefing/briefing2)</li>'
     '<li><strong>Sleep guard</strong>: pokud <code>sh_spim=yes</code>, TTS je blokovaný (mimo morning_briefing)</li>'
     '</ul>'),

    ('🤖 GEMINI DIAGNOSTIKA', 'help-gemini-diag',
     '<h4>🤖 Gemini AI diagnostika</h4>'
     '<ul>'
     '<li><strong>Co to dělá</strong>: Gemini API analyzuje stav systému → generuje diagnostický souhrn česky</li>'
     '<li><strong>Proměnné</strong>: <code>sh_gemini_diag_text</code> (report), <code>sh_gemini_diag_priority</code> (high/medium/low), <code>sh_gemini_diag_fix</code> (navrhovaný zásah)</li>'
     '<li><strong>Spouští</strong>: <code>sh_gemini_brain_v1</code> s mode=diagnose (manuálně nebo scheduled)</li>'
     '<li><strong>Příklad</strong>: "Ranní rutina selhává → Wake trigger | Sunrise chain"</li>'
     '</ul>'),

    ('AI PENDING', 'help-ai-pending',
     '<h4>⏳ AI Pending Changes</h4>'
     '<ul>'
     '<li><strong>Co to je</strong>: AI v autonomy level 2 (SUGGEST) zapisuje navrhované změny do <code>sh_ai_pending_changes</code> (JSON)</li>'
     '<li><strong>Schvalování</strong>: user klikne "Apply" nebo "Reject" → zapíše do odpovídajícího requestu</li>'
     '<li><strong>Level 3 (ASK)</strong>: AI se zeptá přes TTS místo silent pending</li>'
     '<li><strong>Level 4 (AUTO)</strong>: AI provádí safe akce sama (dim, comfort scene)</li>'
     '</ul>'),

    ('OFFLINE ZAŘÍZENÍ', 'help-offline',
     '<h4>📡 Offline zařízení monitor</h4>'
     '<ul>'
     '<li><strong>Co to dělá</strong>: <code>sh_device_availability_v1</code> každých 5 min kontroluje všech 73 zařízení</li>'
     '<li><strong>Offline</strong>: zařízení které v Homey hlásí <code>available=false</code> (Z-Wave ztratilo signál, Zigbee battery=0, WiFi down)</li>'
     '<li><strong>Log</strong>: transitions se zapisují do Sheets "Device Availability" sheet</li>'
     '<li><strong>Alert</strong>: pokud offline > 24h → notifikace</li>'
     '</ul>'),

    ('📦 LOG SNAPSHOTS', 'help-log-snapshots',
     '<h4>📦 Log snapshots — 12 diagnostic tiles</h4>'
     '<ul>'
     '<li><strong>Co to je</strong>: každý tile = jedna stavová proměnná se stručným preview</li>'
     '<li><strong>Klik</strong>: otevře modal s celým obsahem JSON (pokud je to JSON)</li>'
     '<li><strong>Příklady</strong>: sh_meta_decision_log, sh_diag_last_report, sh_self_heal_last_action, sh_autofix_last</li>'
     '<li><strong>Formát</strong>: pretty-printed JSON + syntax highlighting</li>'
     '</ul>'),

    ('💡 LUX 24h', 'help-lux24',
     '<h4>💡 Lux 24-hodinový graf</h4>'
     '<ul>'
     '<li><strong>Data</strong>: z Google Sheets "Lux Monitor" sheet (vzorky po 10 min z 6 senzorů)</li>'
     '<li><strong>Senzory</strong>: Xiaomi PC setup, Fibaro kuchyň, Jídelna okno, Ložnice, Koupelna, Venek</li>'
     '<li><strong>Y-osa</strong>: logaritmická (1 → 100,000 lux) kvůli velkému rozsahu</li>'
     '<li><strong>Použití</strong>: viditelný pattern východ slunce / mráčky / přímé slunce pro kalibraci rolety</li>'
     '</ul>'),

    ('EVENT LOG · DIAGNOSTIKA', 'help-eventlog',
     '<h4>📋 Event log z Google Sheets</h4>'
     '<ul>'
     '<li><strong>Zdroj</strong>: všechny HomeyScripty logují eventy do EventLog sheetu (10k rows max)</li>'
     '<li><strong>Columns</strong>: timestamp · script · event · trigger · zone · params · result · error · priority</li>'
     '<li><strong>Filter</strong>: klik na řádek otevře modal s celým params JSON</li>'
     '<li><strong>Query</strong>: <code>?mode=events&hours=3&script=sh_X</code> přes WebFetch</li>'
     '</ul>'),

    ('🔋 BATTERY', 'help-battery',
     '<h4>🔋 Monitoring baterií</h4>'
     '<ul>'
     '<li><strong>Zařízení s bat</strong>: Xiaomi senzory, Fyrtur roleta, Cube, Button, TRV</li>'
     '<li><strong>Low threshold</strong>: default 20% → warning, 10% → alert</li>'
     '<li><strong>Snapshot</strong>: <code>sh_system_health_v1</code> denně ukládá do Sheets "Battery History"</li>'
     '<li><strong>Graf</strong>: 7denní trend — pokud klesá rychle = čas vyměnit</li>'
     '</ul>'),

    ('PŘEDPOVĚĎ · 3 DNY', 'help-weather3d',
     '<h4>☁️ Předpověď počasí (3 dny)</h4>'
     '<ul>'
     '<li><strong>API</strong>: OpenWeatherMap (klíč v <code>sh_owm_api_key</code>)</li>'
     '<li><strong>Lokace</strong>: Semily (pevně)</li>'
     '<li><strong>Obsah</strong>: min/max teplota, srážky pravděpodobnost, ikona stavu</li>'
     '<li><strong>Použití</strong>: AI layer PREDICT (topení) → pokud zítra −5°C, dnes večer pre-heat</li>'
     '</ul>'),

    ('📊 AI TUNE (MORNING)', 'help-ai-tune',
     '<h4>📊 AI Morning Tune</h4>'
     '<ul>'
     '<li><strong>Co to dělá</strong>: analyzuje 7 dní ranních rutin → navrhuje tuning (wake time, preset, sunrise intensity)</li>'
     '<li><strong>Proměnná</strong>: <code>sh_morning_tune_recommendation</code></li>'
     '<li><strong>Příklad</strong>: "User vstává průměrně 4:02, nastav alarm na 3:45 pro komfortní wake"</li>'
     '<li><strong>Zdroj</strong>: <code>sh_morning_audit_v1</code> (týdenní), patterns z <code>sh_habit_data</code></li>'
     '</ul>'),
]

# ═══════════════════════════════════════════════════════════════════════════
# Also refactor help-logy to consistent format
# ═══════════════════════════════════════════════════════════════════════════
OLD_LOGY = re.compile(
    r'<div id="help-logy" class="help-panel">.*?</div>(?=\s*<)',
    re.DOTALL
)
NEW_LOGY = (
    '<div id="help-logy" class="help-panel">'
    '<h4>📊 Logy page — přehled</h4>'
    '<ul>'
    '<li><strong>Event log</strong> — realtime události z HomeyScript → Sheets</li>'
    '<li><strong>Log snapshots</strong> — 12 diagnostic tiles (meta brain, self-heal, autofix, atd.)</li>'
    '<li><strong>Offline zařízení</strong> — devices které jsou momentálně unavailable</li>'
    '<li><strong>Battery</strong> — monitoring baterií + 7denní trend</li>'
    '<li><strong>AI tune</strong> — doporučení pro ranní rutinu</li>'
    '<li><strong>Gemini diagnostika</strong> — AI analýza systémového stavu</li>'
    '</ul>'
    '<p>Klik na řádek/tile = detail modal. Klik na <strong>ℹ</strong> u sekcí = kontextová nápověda.</p>'
    '</div>'
)


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
    changes = 0

    # Helper: find + replace plain sect div → wrapped
    for sect_text, help_id, panel_content in HELPS:
        # Pattern pro exact plain sect (bez help wrapperu)
        escaped = re.escape(sect_text)
        # Match <div class="sect" ...>TEXT</div> (plain, without span wrapper)
        pattern = re.compile(
            r'<div class="sect"[^>]*>\s*' + escaped + r'\s*</div>',
            re.IGNORECASE
        )
        m = pattern.search(html)
        if not m:
            continue
        # Skip pokud za ním už je help-panel se shodným id
        ahead = html[m.end():m.end()+200]
        if f'id="{help_id}"' in ahead:
            continue

        # Extract original color/style ze sect
        sect_match = re.search(
            r'<div class="sect"([^>]*)>\s*' + escaped + r'\s*</div>',
            html, re.IGNORECASE
        )
        style_attr = sect_match.group(1) if sect_match else ''

        replacement = (
            f'<div class="sect"{style_attr}>\n'
            f'      <span class="help-sect-header">\n'
            f'        <span>{sect_text}</span>\n'
            f'        <button class="help-btn" data-help-for="{help_id}" onclick="toggleHelp(\'{help_id}\')">ℹ</button>\n'
            f'      </span>\n'
            f'    </div>\n'
            f'    <div id="{help_id}" class="help-panel">{panel_content}</div>'
        )
        html, n = pattern.subn(replacement, html, count=1)
        if n > 0:
            changes += 1

    # Refactor help-logy
    if '<h4>📊 Logy page — přehled</h4>' not in html:
        html, n = OLD_LOGY.subn(NEW_LOGY, html, count=1)
        if n > 0:
            changes += 1

    if changes == 0:
        print(f'  ✗ 0 changes: {os.path.basename(path)}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(path)} ({len(html)-orig_len:+d} bytes, {changes} changes)')
    return True


def main():
    print('Phase 22: Missing helps + logy refactor')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
