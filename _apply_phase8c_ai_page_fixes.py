"""
PHASE 8c — AI page fixy (orphan sect headers + Predict AI text wrapping)

PROBLEMS from user screenshot:
  1) "PŘEPISY (OVERRIDES)" label je orphan v levém sloupci, karta toggles
     v pravém sloupci (column break rozdělil sect+card pair)
  2) AI MODULY "Predict" tile má moc dlouhý text (sh_predict_last_action) →
     wrap ničí layout, tile má 5+ řádků textu

FIXES:
  1) CSS: #page-ai .sect { break-after: avoid-column } — sect header
     zůstane vždy se svým card
  2) JS: truncate ai-predict / ai-meta / ai-coord values na max ~40 znaků

Idempotent. Marker: PHASE8C_AI_PAGE_FIXES_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE8C_AI_PAGE_FIXES_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: CSS — keep sect header with next element (no orphan)
# Anchor: existing #page-ai column rules
# ═══════════════════════════════════════════════════════════════════════════
OLD_CSS = """#page-ai.active{
  columns:2;column-gap:12px;
}
#page-ai>*{break-inside:avoid;}"""

NEW_CSS = """#page-ai.active{
  columns:2;column-gap:12px;
}
#page-ai>*{break-inside:avoid;}
/* PHASE8C_AI_PAGE_FIXES_APPLIED — sect header stays with next element (no orphan) */
#page-ai .sect{break-after:avoid-column;break-inside:avoid;page-break-after:avoid;}
#page-ai .help-panel{break-before:avoid-column;}
/* Long AI values truncated s ellipsis (Predict AI atd.) */
#page-ai .tile .t-val{overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;max-height:52px;line-height:1.25;font-size:10px;word-break:break-word;}"""

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: Truncate JS-set values pro AI moduly (ai-predict, ai-meta, ai-coord)
# Anchor: findable by "sh_predict_last_action" or "ai-predict" assignment
# ═══════════════════════════════════════════════════════════════════════════
# Find JS that populates these. Likely in updateAI() or similar
# Search patterns:
#   document.getElementById('ai-predict').textContent = ...
# Add truncation helper wrapping.

OLD_JS_HELPER_ANCHOR = "function setText(id, val) {"

INJECT_JS_HELPER = """// PHASE8C_AI_PAGE_FIXES_APPLIED — truncate long AI module values
function setTextTrunc(id, val, maxLen) {
  const el = document.getElementById(id);
  if (!el) return;
  const s = String(val == null ? '—' : val);
  if (s.length <= (maxLen || 60)) { el.textContent = s; el.title = s; return; }
  el.textContent = s.substring(0, maxLen || 60) + '…';
  el.title = s;  // full text on hover
}

"""


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

    # 1. CSS fix
    replace(OLD_CSS, NEW_CSS, 'CSS: break-after:avoid-column + truncate t-val',
            marker='PHASE8C_AI_PAGE_FIXES_APPLIED — sect header stays')

    # 2. JS truncation helper
    if 'PHASE8C_AI_PAGE_FIXES_APPLIED — truncate long AI module values' in content:
        changes.append('⏭ JS helper (už applied)')
    elif OLD_JS_HELPER_ANCHOR in content:
        inj = INJECT_JS_HELPER.replace('\n', '\r\n') if is_crlf else INJECT_JS_HELPER
        content = content.replace(OLD_JS_HELPER_ANCHOR, inj + OLD_JS_HELPER_ANCHOR, 1)
        changes.append('+ JS helper setTextTrunc()')
    else:
        changes.append('⏭ JS helper anchor missing')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 8c — AI page orphan + text wrap fixy')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
