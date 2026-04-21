"""
Phase 25 (2026-04-21) — Unified roleta popisky ve všech 3 rozlišeních

Problém: Phase 19 + 21 pattern match selhal v 1920/2880 (mírně jiný text)
→ desktop stále vidí starý popis "Doporučeno 5000-15000" a nadpis "Stínění při silném slunci"

Phase 25 dělá jeden-pass rewrite:
  1. Nadpis "🥵 Stínění při silném slunci" → "🥵 STÁHNOUT KDYŽ (silné slunce)"
  2. Popis celý přepsaný — reálná data z Lux Monitor (29,812 max, top5 ≥ 18k)
  3. Hystereze popis přepsaný aby byl srozumitelný
  4. Upravit staré "Doporučení: 5000-15000" → "Doporučeno 15,000-25,000"

Idempotentní — marker PHASE25_ROLETA_TEXT_UNIFIED.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE25_ROLETA_TEXT_UNIFIED'

# ═══════════════════════════════════════════════════════════════════════════
# Regex patterns pro robustní replace napříč všemi 3 variantami
# ═══════════════════════════════════════════════════════════════════════════

# 1. Nadpis shade-lux — všechny varianty ("🥵 Stínění při silném slunci" / "🥵 STÁHNOUT KDYŽ" / "Stínění při silném slunci")
NAME_PATTERN = re.compile(
    r'<span class="roleta-cfg-name">🥵 [^<]*</span>\s*\n\s*'
    r'<span class="roleta-cfg-val" id="rcfg-shade-lux">'
)
NAME_REPLACEMENT = (
    '<span class="roleta-cfg-name">🥵 STÁHNOUT KDYŽ (silné slunce)</span>\n'
    '          <span class="roleta-cfg-val" id="rcfg-shade-lux">'
)

# 2. Description celého shade-lux řádku (between desc opening and example close)
SHADE_DESC_PATTERN = re.compile(
    r'(<span class="roleta-cfg-val" id="rcfg-shade-lux">—</span>\s*\n\s*</div>\s*\n)'
    r'\s*<div class="roleta-cfg-desc">[^<]*(?:<strong>[^<]*</strong>[^<]*)*</div>\s*\n'
    r'\s*<div class="roleta-cfg-example">[^<]*(?:<[^>]+>[^<]*</[^>]+>[^<]*|<br>[^<]*)*</div>',
    re.DOTALL
)
SHADE_DESC_REPLACEMENT = (
    r'\1'
    '        <div class="roleta-cfg-desc"><strong>Co to dělá:</strong> NAD touto hodnotou lux = přímé slunce → roleta sjede na <strong>shade pozici</strong> (stínění místnosti).</div>\n'
    '        <div class="roleta-cfg-example"><strong>Reálná data z tvých senzorů</strong> (týden): max <strong>29,812 lux</strong> · top5 ≥ 18,000 · median top15 = 15,360. '
    '<span style="color:var(--cyan);">📊 Doporučeno <strong>15,000–25,000</strong></span> + hysteresis 2000–3000. '
    '<br>Výš než 30,000 = shade se téměř nikdy nespustí (max reálný lux). Níž než 5000 = shade i při oblačnosti.</div>'
)

# 3. Hystereze — přepsat popis aby byl pochopitelnější + příklad
HYST_DESC_PATTERN = re.compile(
    r'(<span class="roleta-cfg-val" id="rcfg-hyst">—</span>\s*\n\s*</div>\s*\n)'
    r'\s*<div class="roleta-cfg-desc">[^<]*(?:<strong>[^<]*</strong>[^<]*)*</div>\s*\n'
    r'\s*<div class="roleta-cfg-example">[^<]*(?:<[^>]+>[^<]*</[^>]+>[^<]*|&lt;[^<]*)*</div>',
    re.DOTALL
)
HYST_DESC_REPLACEMENT = (
    r'\1'
    '        <div class="roleta-cfg-desc"><strong>Co to dělá:</strong> ZABRÁNÍ oscilaci (yo-yo). Když je roleta ve shade módu, vrátí se do otevřené pozice až když lux <strong>klesne pod (shade − hysteresis)</strong>. Bez hystereze by se přepínala tam a zpět.</div>\n'
    '        <div class="roleta-cfg-example"><strong>Příklad</strong>: shade = 20,000 · hysteresis = 3,000 → stáhne při 20,000+ lux, vrátí do open až při &lt;17,000. '
    '<span style="color:var(--cyan);">📊 Doporučeno <strong>2000–3000</strong></span> (cca 15 % ze shade hodnoty).</div>'
)

# 4. Prune staré "Doporučení: 5000-15000" zmínky i v jiných textech (jistota)
OLD_RECOMMENDATION_PATTERN = re.compile(
    r'<span style="color:var\(--red\);">⚠️[^<]*?Doporučení: 5000[-–]15000\.?</span>'
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

    # 1. Nadpis
    new_html, n1 = NAME_PATTERN.subn(NAME_REPLACEMENT, html)
    if n1 > 0:
        html = new_html
        changes += n1

    # 2. Shade description
    new_html, n2 = SHADE_DESC_PATTERN.subn(SHADE_DESC_REPLACEMENT, html)
    if n2 > 0:
        html = new_html
        changes += n2

    # 3. Hysteresis description
    new_html, n3 = HYST_DESC_PATTERN.subn(HYST_DESC_REPLACEMENT, html)
    if n3 > 0:
        html = new_html
        changes += n3

    # 4. Prune old warning text
    new_html, n4 = OLD_RECOMMENDATION_PATTERN.subn('', html)
    if n4 > 0:
        html = new_html
        changes += n4

    # Add marker
    if MARKER not in html:
        html = html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)

    if changes == 0:
        print(f'  ✗ 0 changes: {os.path.basename(path)}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(path)} ({len(html)-orig_len:+d} bytes, {changes} changes: nadpis={n1} shade_desc={n2} hyst_desc={n3} prune={n4})')
    return True


def main():
    print('Phase 25: Unified roleta popisky (3 rozlišení)')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
