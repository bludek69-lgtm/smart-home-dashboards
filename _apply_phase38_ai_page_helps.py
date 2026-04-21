"""
Phase 38 (2026-04-21) — AI page tooltips + MANUÁLNÍ AKCE help panel

User pož: doplnit helpy na AI page — neví co znamenají tlačítka ("treba
manualní akce").

Obsahuje:
  1. Mapping fn → title pro všechna akce (DIAGNOSTICKÉ + MANUÁLNÍ + bottom buttons)
  2. Přidá help panel do MANUÁLNÍ AKCE sekce (která help dosud neměla)

Idempotentní marker PHASE38_AI_PAGE_HELPS.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE38_AI_PAGE_HELPS'

# fn call → title text (Czech, stručné)
TOOLTIP_MAP = {
    # DIAGNOSTICKÉ AKCE
    "runScript('sh_system_health_v1')": 'Spustí Health check · aktualizuje sh_system_health_score',
    "runScript('sh_self_healing_v4')": 'Self-heal · detekuje a opraví orphan / stuck proměnné',
    "runScript('sh_critical_devices_v1')": 'Check kritických zařízení (PC zásuvka, kotel, kamera)',
    "runScript('sh_anomaly_detector_v1')": 'Anomaly detector · najde odchylky v senzorech (PM2.5, temp, vlhkost)',
    "wakeUp()": 'Probudit · vypne sh_spim, resetuje morning vars, trigger ranní rutinu',
    "runScript('sh_time_sync_guard_v1')": 'Ověří a případně opraví čas / timezone',
    "runScript('sh_conflict_guard_v1')": 'Detekce konfliktů mezi skripty (duplicate writes)',
    "runScript('sh_morning_audit_v1')": 'Audit ranní rutiny · % dokončení + timing',
    "runScript('sh_meta_brain_v1')": 'Meta Brain · centrální rozhodovací engine (full scan)',
    "runScript('sh_system_reconcile_v1')": 'Reconcile · sjednotí state napříč skripty, vyčistí stuck',
    "runScript('sh_autofix_engine_v1')": 'AutoFix · automaticky opraví známé config issues (shade, PM2.5)',
    "sendReq('sh_emergency_reset','trigger')": '⚠ EMERGENCY RESET · nouzově vypne všechna světla, audio, scény',
    # MANUÁLNÍ AKCE
    "sendReq('sh_scene_active_request','relax')": 'Relax scéna · tlumené světlo, ambient audio',
    "roletaRecheck()": 'Roleta recheck · re-evaluace roleta routeru s aktuálním lux',
    "forceMorningFallback()": 'Vynutit ranní rutinu (fallback trigger) · test bez alarmu',
    "runScript('sh_evening_auto_v1')": 'Evening test · simulace večerní automatiky (relax scéna)',
    # Gemini Diagnostika
    "runScript('sh_state_engine_v1')": 'State engine · refresh system state proměnných',
    "runScript('sh_error_tracker_v1')": 'Error tracker · sumář chyb z posledních hodin',
    "runScript('sh_diag_analyzer_v1')": 'Diag analyzer · hlubší analýza logů + hledání patterns',
    "runScript('sh_gemini_diagnostic_v1')": 'Gemini AI diagnostika · full system analysis přes LLM (trvá ~30 s)',
    "explainLastAction()": 'Nech AI vysvětlit poslední rozhodnutí (Gemini)',
    "openGeminiDiagFullReport()": 'Otevřít plný Gemini diagnostický report',
    # Toggles
    "toggleVar('sh_manual_override_light',this)": 'Ruční override světel · AI nezasahuje',
    "toggleVar('sh_privacy_guard_enabled',this)": 'Privacy guard · roleta nahoře ⇒ open space světla VYPNUTA',
    "toggleVar('sh_simulation_mode',this)": 'Simulace · skripty jen loguje, žádné skutečné akce',
    "toggleVar('sh_predict_enabled',this)": 'AI predikce · Predict modul aktivní',
    "toggleVar('sh_morning_skip_tomorrow',this)": 'Skip zítřejší ranní rutiny (tichý start)',
    "toggleVar('sh_cfg_auto_scene_enabled',this)": 'Auto-scény · večerní relax automaticky dle času',
    "togglePurifierGuard(this)": 'Čistička guard · sledovat PM2.5 a aktivovat čističku',
}


def patch_file(path):
    name = os.path.basename(path)
    if not os.path.exists(path):
        print(f'  X NOT FOUND: {name}')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    if MARKER in html:
        print(f'  OK already patched: {name}')
        return True

    # Only patch within page-ai
    m = re.search(r'(<div class="page[^"]*"\s+id="page-ai">)(.*?)(<div class="page[^"]*"\s+id="page-)', html, re.DOTALL)
    if not m:
        print(f'  X page-ai NOT FOUND: {name}')
        return False

    ai_block = m.group(2)
    orig_ai = ai_block

    # Apply tooltips
    tooltip_added = 0
    for fn, title in TOOLTIP_MAP.items():
        # Escape for regex + replacement
        fn_re = re.escape(fn)
        title_esc = title.replace('"', '&quot;')
        # Pattern: onclick="EXACT_FN"(... no title ...)>
        pattern = re.compile(
            r'(onclick="' + fn_re + r'")((?:(?!title=)[^>])*)>',
            re.DOTALL
        )
        def repl(match):
            nonlocal tooltip_added
            # Check if already has title (safety)
            full = match.group(0)
            if 'title=' in full:
                return full
            tooltip_added += 1
            return match.group(1) + ' title="' + title_esc + '"' + match.group(2) + '>'
        ai_block = pattern.sub(repl, ai_block)

    # Add help panel to MANUÁLNÍ AKCE section
    MA_OLD = '<div class="sect" style="color:var(--cyan);">MANUÁLNÍ AKCE</div>'
    MA_NEW = (
        '<div class="sect" style="color:var(--cyan);">\n'
        '        <span class="help-sect-header">\n'
        '          <span>MANUÁLNÍ AKCE</span>\n'
        '          <button class="help-btn" data-help-for="help-ai-manual" onclick="toggleHelp(\'help-ai-manual\')">ℹ</button>\n'
        '        </span>\n'
        '      </div>\n'
        '      <div id="help-ai-manual" class="help-panel">\n'
        '        <h4>🎛 Manuální akce</h4>\n'
        '        <p>Ruční spuštění akcí bez čekání na auto/cron trigger. Užitečné pro testování nebo okamžité reakce.</p>\n'
        '        <ul>\n'
        '          <li><strong>Relax scéna</strong> · aktivuje relax scénu (tlumené světlo, ambient)</li>\n'
        '          <li><strong>Roleta recheck</strong> · re-evaluace roleta routeru s aktuálním lux (např. po manuálním přesunu)</li>\n'
        '          <li><strong>Force ranní</strong> · vynutí ranní rutinu (fallback trigger) — test bez alarmu</li>\n'
        '          <li><strong>Evening test</strong> · simulace večerní automatiky (relax scéna + audio)</li>\n'
        '        </ul>\n'
        '        <p style="color:var(--tx3);font-size:10px;">Tyto akce neovlivní historii morning/evening — jen spustí logiku.</p>\n'
        '      </div>'
    )
    help_added = False
    if MA_OLD in ai_block and 'help-ai-manual' not in ai_block:
        ai_block = ai_block.replace(MA_OLD, MA_NEW, 1)
        help_added = True

    if tooltip_added == 0 and not help_added:
        print(f'  - no changes: {name}')
        return False

    new_html = html[:m.start(2)] + ai_block + html[m.end(2):]
    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK patched: {name} (tooltips={tooltip_added}, help_panel={help_added})')
    return True


def main():
    print('Phase 38: AI page tooltips + MANUÁLNÍ AKCE help panel')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
