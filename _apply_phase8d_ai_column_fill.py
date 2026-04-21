"""
PHASE 8d — AI page column-fill fix

Problem ze screenshotu:
  - Pravý sloupec začíná VÝŠ než levý (pod top navem je clipped "Jak to funguje" tlačítko)
  - PŘEPISY (OVERRIDES) label je za horním barem (neviditelný)
  - Auto-balance rozdělí obsah tak, že pravý sloupec má TOP content za frame

Příčina: CSS `columns:2` s default `column-fill: balance` + top spacer `column-span:all`
se nechová deterministicky na všech prohlížečích.

Fix (zachovává VEŠKERÝ obsah):
  1) column-fill: auto — levý sloupec se naplní nejdřív, přebytek do pravého
  2) Explicitní padding-top na #page-ai 28px (stejně jako logy/advanced/finance/burza)
  3) Explicitní spacer na začátku stránky s jistotou že zabere celou šířku

Idempotent. Marker: PHASE8D_AI_COLUMN_FILL_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD_CSS = """#page-ai.active{
  columns:2;column-gap:12px;
}
#page-ai>*{break-inside:avoid;}"""

NEW_CSS = """#page-ai.active{
  columns:2;column-gap:12px;
  column-fill:auto;  /* PHASE8D — levý sloupec napred, pravý dostane overflow */
  padding-top:28px !important;  /* PHASE8D — stejné jako logy/advanced/finance */
  height:calc(100vh - 120px);  /* výška columns container = pravý sloupec získá dolní část levého */
}
#page-ai>*{break-inside:avoid;}"""

# Also add top spacer to #page-logy style rule — already has padding-top 28
# Ensure page-ai has it too
OLD_PADDING_RULE = """#page-logy, #page-advanced, #page-finance, #page-burza { padding-top: 28px !important; }"""
NEW_PADDING_RULE = """#page-logy, #page-advanced, #page-finance, #page-burza, #page-ai { padding-top: 28px !important; }"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    orig = content
    changes = []
    is_crlf = '\r\n' in content[:4096]

    marker = 'PHASE8D_AI_COLUMN_FILL_APPLIED'
    if marker in content or 'column-fill:auto' in content:
        changes.append('⏭ CSS (už applied)')
    else:
        old2 = OLD_CSS.replace('\n', '\r\n') if is_crlf else OLD_CSS
        new2 = NEW_CSS.replace('\n', '\r\n') if is_crlf else NEW_CSS
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ CSS: column-fill:auto + padding-top 28 + height calc')
        else:
            changes.append('⏭ CSS anchor missing')

    # Add page-ai to padding rule (defensive — even if main fix applied first)
    if '#page-ai ' in content and NEW_PADDING_RULE not in content:
        if OLD_PADDING_RULE in content:
            content = content.replace(OLD_PADDING_RULE, NEW_PADDING_RULE, 1)
            changes.append('+ Padding-top rule extended to #page-ai')
        else:
            changes.append('⏭ Padding rule anchor missing')

    if content != orig:
        # Add marker comment
        content = content.replace('column-fill:auto;  /* PHASE8D',
                                  '/* ' + marker + ' */\n  column-fill:auto;  /* PHASE8D', 1)
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 8d — AI page column-fill fix')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
