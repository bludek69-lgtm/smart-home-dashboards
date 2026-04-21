"""
Phase 43 (2026-04-21) — LOG SNAPSHOTS full-width (column-span:all)

Předchozí fixy (g4→g2) nezabraly — tile jsou stále overflow v pravém sloupci.
Řešení: vyhodit celou sekci z CSS column layoutu přes `column-span:all`.
Sekce se rozprostře přes oba sloupce a tiles bude 6 v řadě.

Idempotentní marker PHASE43_LOG_SNAPSHOTS_FULLWIDTH.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE43_LOG_SNAPSHOTS_FULLWIDTH'


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

    # Find LOG SNAPSHOTS section opening sect div
    start_pat = re.compile(
        r'(    <div class="sect"[^>]*>\s*<span class="help-sect-header">\s*<span>📦 LOG SNAPSHOTS</span>[^<]*</span>[^<]*<button[^>]*>ℹ</button>\s*</span>\s*</div>)',
        re.DOTALL
    )
    m_start = start_pat.search(html)
    if not m_start:
        # Try simpler
        start_pat2 = re.compile(r'(<div class="sect"[^>]*>)(\s*<span class="help-sect-header">\s*<span>📦 LOG SNAPSHOTS)', re.DOTALL)
        m = start_pat2.search(html)
        if not m:
            print(f'  X LOG SNAPSHOTS start NOT FOUND: {name}')
            return False
        # Add wrapper before sect, column-span on all siblings until GEMINI
        end_pat = re.compile(r'<div class="sect"[^>]*>\s*<span class="help-sect-header">\s*<span>🤖 GEMINI DIAGNOSTIKA')
        m_end = end_pat.search(html, m.start())
        if not m_end:
            print(f'  X GEMINI end NOT FOUND: {name}')
            return False
        # Insert wrapper div that spans all columns
        before = html[:m.start()]
        wrapped = html[m.start():m_end.start()]
        after = html[m_end.start():]
        # Wrap with column-span:all container
        new_html = before + '<div style="column-span:all;break-before:column;">' + wrapped + '</div>' + after
        new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f'  OK patched (wrapper): {name}')
        return True

    print(f'  X unexpected flow: {name}')
    return False


def main():
    print('Phase 43: LOG SNAPSHOTS full-width')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
