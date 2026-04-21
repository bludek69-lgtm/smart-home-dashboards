"""
Phase 20 (2026-04-21) — Help panely pro AI page + rozšíření heating helpů

Přidává info helpy pro sekce které je dosud neměly:
  - AI CONTROL CENTER → help-ai-control (Health, Chyby, Výkon, Offline)
  - AI AUTONOMIE → help-ai-autonomy (LOG / SUGGEST / ASK / AUTO)
  - AI MODULY → help-ai-moduly (Meta Brain, Predict, Coordinator)
  - REQUEST PIPELINE → help-ai-pipeline (jak probíhá light/audio/scene/roleta request)
  - TOPENÍ 2 → help-heating2 už existuje (kontrola)
  - Heating hysteresis info → rozšíření help-roleta

Idempotentní — marker help-ai-control.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'help-ai-control'

# ═══════════════════════════════════════════════════════════════════════════
# 1. AI CONTROL CENTER — replace plain heading with help-wrapped version
# ═══════════════════════════════════════════════════════════════════════════
OLD_AI_CONTROL = '<div class="sect" style="color:var(--purple);">🧠 AI CONTROL CENTER</div>'
NEW_AI_CONTROL = (
    '<div class="sect" style="color:var(--purple);">\n'
    '      <span class="help-sect-header">\n'
    '        <span>🧠 AI CONTROL CENTER</span>\n'
    '        <button class="help-btn" data-help-for="help-ai-control" onclick="toggleHelp(\'help-ai-control\')">ℹ</button>\n'
    '      </span>\n'
    '    </div>\n'
    '    <div id="help-ai-control" class="help-panel">\n'
    '      <h4>🧠 Co vidíš v kontrolním centru</h4>\n'
    '      <ul>\n'
    '        <li><strong>💚 Health</strong> — systémový skóre (100 = vše OK, &lt;85 = warning, &lt;70 = kritický)</li>\n'
    '        <li><strong>⚠️ Chyby/30m</strong> — počet error events za posledních 30 min (z Google Sheets)</li>\n'
    '        <li><strong>⚡ Výkon</strong> — aktuální spotřeba (W) ze všech sledovaných zařízení</li>\n'
    '        <li><strong>📡 Offline</strong> — počet zařízení momentálně offline</li>\n'
    '      </ul>\n'
    '      <p>Data se obnovují každých ~5 s z <code>sh_system_health_score</code> a dalších runtime proměnných.</p>\n'
    '    </div>'
)

# ═══════════════════════════════════════════════════════════════════════════
# 2. AI AUTONOMIE
# ═══════════════════════════════════════════════════════════════════════════
OLD_AI_AUTONOMY = '<div class="sect" style="color:var(--purple);">AI AUTONOMIE</div>'
NEW_AI_AUTONOMY = (
    '<div class="sect" style="color:var(--purple);">\n'
    '      <span class="help-sect-header">\n'
    '        <span>AI AUTONOMIE</span>\n'
    '        <button class="help-btn" data-help-for="help-ai-autonomy" onclick="toggleHelp(\'help-ai-autonomy\')">ℹ</button>\n'
    '      </span>\n'
    '    </div>\n'
    '    <div id="help-ai-autonomy" class="help-panel">\n'
    '      <h4>🎚 4 úrovně autonomie AI</h4>\n'
    '      <ul>\n'
    '        <li><strong>1 · LOG</strong> — AI jen loguje události, NIC nezasahuje. Bezpečný monitoring režim.</li>\n'
    '        <li><strong>2 · SUGGEST</strong> — AI navrhuje změny do <code>sh_ai_pending_changes</code>. Ty pak schvaluješ v dashboardu.</li>\n'
    '        <li><strong>3 · ASK</strong> — AI se ptá TTS ("Luďku, chceš spustit večerní scénu?"). Interaktivní.</li>\n'
    '        <li><strong>4 · AUTO</strong> — AI provádí SAFE akce autonomně (dim, comfort scene). Rizikové akce (alarm, topení) vyžadují potvrzení.</li>\n'
    '      </ul>\n'
    '      <p>Aktuální úroveň: <code>sh_ai_autonomy_level</code>. Dvojklik na číslo = detail limit per akce.</p>\n'
    '    </div>'
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. AI MODULY
# ═══════════════════════════════════════════════════════════════════════════
OLD_AI_MODULES = '<div class="sect" style="color:var(--purple);">AI MODULY</div>'
NEW_AI_MODULES = (
    '<div class="sect" style="color:var(--purple);">\n'
    '      <span class="help-sect-header">\n'
    '        <span>AI MODULY</span>\n'
    '        <button class="help-btn" data-help-for="help-ai-moduly" onclick="toggleHelp(\'help-ai-moduly\')">ℹ</button>\n'
    '      </span>\n'
    '    </div>\n'
    '    <div id="help-ai-moduly" class="help-panel">\n'
    '      <h4>🧩 3 AI moduly — každý řeší něco jiného</h4>\n'
    '      <ul>\n'
    '        <li><strong>🧠 Meta Brain</strong> (<code>sh_meta_brain_v1</code>) — mozek na nejvyšší úrovni. Sleduje systémové chyby (stuck states, stale vars), diagnostikuje a navrhuje fixy.</li>\n'
    '        <li><strong>🔮 Predict</strong> (<code>sh_predict_engine_v1</code>) — predikuje tvoje akce. Příklad: "Luděk je ráno v kuchyni 8 min → pravděpodobně si dá kávu → pre-heat ohřívač".</li>\n'
    '        <li><strong>🤝 Coordinator</strong> (<code>sh_coordinator_v1</code>) — koordinuje mezi moduly. Př.: light_router chce zhasnout, ale scene_engine má aktivní kino → Coordinator rozhodne kdo vyhraje.</li>\n'
    '      </ul>\n'
    '      <p>Klik na tile = celý obsah poslední akce. Dvojklik na některé = detailní modal.</p>\n'
    '    </div>'
)

# ═══════════════════════════════════════════════════════════════════════════
# 4. REQUEST PIPELINE
# ═══════════════════════════════════════════════════════════════════════════
OLD_AI_PIPELINE = '<div class="sect" style="color:var(--purple);">REQUEST PIPELINE</div>'
NEW_AI_PIPELINE = (
    '<div class="sect" style="color:var(--purple);">\n'
    '      <span class="help-sect-header">\n'
    '        <span>REQUEST PIPELINE</span>\n'
    '        <button class="help-btn" data-help-for="help-ai-pipeline" onclick="toggleHelp(\'help-ai-pipeline\')">ℹ</button>\n'
    '      </span>\n'
    '    </div>\n'
    '    <div id="help-ai-pipeline" class="help-panel">\n'
    '      <h4>🔄 Jak prochází request systémem</h4>\n'
    '      <p><strong>Princip "Request-first"</strong>: místo toho aby skript přímo ovládal zařízení, zapíše <em>request</em> do proměnné. Router ho pak přečte a provede. Výhoda: lze blokovat, logovat, priority.</p>\n'
    '      <ul>\n'
    '        <li><strong>💡 Light</strong> — <code>sh_light_request</code> → <code>sh_light_router_v1</code> → konkrétní žárovky</li>\n'
    '        <li><strong>🔊 Audio</strong> — <code>sh_audio_request</code> → <code>sh_audio_brain_v2</code> → <code>sh_speaker_router_v1</code> → Chromecast</li>\n'
    '        <li><strong>🎬 Scene</strong> — <code>sh_scene_active_request</code> → <code>sh_scene_engine_v1</code> → kompletní scéna (light + audio)</li>\n'
    '        <li><strong>▬ Roleta</strong> — <code>sh_jidelna_roleta_trigger</code> → <code>sh_jidelna_roleta_router_v2</code> → motor</li>\n'
    '      </ul>\n'
    '      <p>Hodnoty v tiles = poslední aktivní request. <code>idle</code> = žádná aktivita.</p>\n'
    '    </div>'
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
    for old, new, label in [
        (OLD_AI_CONTROL, NEW_AI_CONTROL, 'AI CONTROL'),
        (OLD_AI_AUTONOMY, NEW_AI_AUTONOMY, 'AI AUTONOMY'),
        (OLD_AI_MODULES, NEW_AI_MODULES, 'AI MODULES'),
        (OLD_AI_PIPELINE, NEW_AI_PIPELINE, 'AI PIPELINE'),
    ]:
        if old in html:
            html = html.replace(old, new, 1)
            changes += 1
        else:
            print(f'    ⚠ {label} anchor nenalezen')

    if changes == 0:
        print(f'  ✗ 0 changes: {os.path.basename(path)}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(path)} ({len(html)-orig_len:+d} bytes, {changes}/4 sections)')
    return True


def main():
    print('Phase 20: Help panels for AI page')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
