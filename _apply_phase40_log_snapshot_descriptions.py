"""
Phase 40 (2026-04-21) — Log snapshot tiles inline descriptions

User: 3 dlaždice v LOG SNAPSHOTS sekci "koukají malinko" — popisek je jen
v title (hover), ale user chce vidět trvale co tile dělá.

Fix: ke každému tile přidat inline `<span class="t-desc">Krátký popis</span>`
pod t-lbl. Plus zvětšit min-height z 50px na 68px.

Idempotentní marker PHASE40_LOG_SNAPSHOT_DESC.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE40_LOG_SNAPSHOT_DESC'

# 12 tile mapping — varName → (label, description)
TILES = [
    ('sh_ai_learn_last_report',   'Gemini doporučení'),
    ('sh_daily_report',           'Denní souhrn'),
    ('sh_weekly_report',          'Týdenní souhrn'),
    ('sh_gemini_daily_briefing',  'Ranní briefing'),
    ('sh_debug_last_report',      'Dump systému'),
    ('sh_diag_last_report',       'Diag engine'),
    ('sh_self_heal_last_action',  'Samooprava'),
    ('sh_autofix_last',           'Autofix'),
    ('sh_anomaly_last',           'Neobvyklost'),
    ('sh_last_decision',          'Rozhodnutí'),
    ('sh_learning_summary',       'Learning metrics'),
    ('sh_predict_last_action',    'Predikce'),
]

DESC_STYLE = 'font-size:9px;color:var(--tx3);display:block;line-height:1.1;margin-top:2px;'


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

    changes = 0
    for var_name, desc in TILES:
        # Match the tile's t-info close BEFORE </div></div>
        # Pattern: onclick="openLogSnapshot('VAR_NAME',..."...<span class="t-lbl">LBL</span></div></div></div>
        # We want to insert <span class="t-desc">DESC</span> after </span class="t-lbl">LBL</span>
        pattern = re.compile(
            r'(<div class="tile" onclick="openLogSnapshot\(\'' + re.escape(var_name) + r'\',[^)]*\)"[^>]*min-height:)50px(;[^>]*>)'
            r'(<div class="t-top"><span class="t-icon">[^<]+</span><div class="t-info"><span class="t-lbl">[^<]+</span>)'
            r'(</div></div></div>)'
        )

        def repl(m):
            nonlocal changes
            changes += 1
            return (m.group(1) + '68px' + m.group(2) +
                    m.group(3) +
                    f'<span class="t-desc" style="{DESC_STYLE}">{desc}</span>' +
                    m.group(4))

        html = pattern.sub(repl, html, count=1)

    if changes == 0:
        print(f'  X no matches: {name}')
        return False

    html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK patched: {name} (tiles={changes}/{len(TILES)})')
    return True


def main():
    print('Phase 40: Log snapshot tiles inline descriptions')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
