"""
Phase 29 (2026-04-21) — Mass tooltips na klikatelné elementy

Phase 23 přidala title na tabs. Phase 29 rozšíří na všechny <div>/<button>/<span>
s onclick="..." bez title. Mapování podle fn volání.

Strategie:
  - Priority 1: custom mapping pro známé akce (setHeatingMode, audioStop, ...)
  - Priority 2: auto-generovat z onclick args (runScript, goZone, tvDigit)
  - Skipped: toggleHelp (self-explanatory ℹ), switchPage (tabs už mají), otvíratelné detail modály

Idempotentní marker PHASE29_TOOLTIPS_MASS.
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE29_TOOLTIPS_MASS'

# Custom mapping — exact arg patterns → title text
CUSTOM_TITLES = {
    # Heating mode/preset
    "setHeatingMode('auto')":    'Auto režim — scheduler + AI vrstvy (pokud zapnuté)',
    "setHeatingMode('manual')":  'Manuální režim — jen schedule, žádné AI',
    "setHeatingMode('off')":     'Vypnout topení — target všech zón = 7°C',
    "setHeatingPreset('home')":  'Preset Doma — standardní schedule',
    "setHeatingPreset('away')":  'Preset Pryč — všechny zóny 16°C',
    "setHeatingBoost(30)":       'Boost +2°C na 30 min (všechny zóny)',
    "setHeatingPreset('home'); setHeatingNightAll()": 'Nastavit noční teploty do rána',
    # Audio
    "audioStop()":               'Zastavit přehrávání',
    "audioStop('kuchyn')":       'Zastavit přehrávání v kuchyni',
    "audioStop('loznice')":      'Zastavit přehrávání v ložnici',
    "audioStop('koupelna')":     'Zastavit přehrávání v koupelně',
    # Common helpers
    "refreshAll()":              'Obnovit všechna data',
    "clearCache()":              'Vyčistit cache',
}

# Function → title template (when no exact custom match)
FN_TEMPLATES = {
    # runScript('script_name', arg?) → "Spustit script_name(arg)"
    'runScript':      lambda args: f'Spustit skript {args[0]}' + (f' ({args[1]})' if len(args)>1 else ''),
    'goZone':         lambda args: f'Otevřít detail zóny {args[0]}',
    'tvDigit':        lambda args: f'TV kanál {args[0]}',
    'openDeviceDetail': lambda args: f'Detail zařízení {args[0]}' if args else 'Detail zařízení',
    'sendReq':        lambda args: f'Požadavek {args[0]}' if args else 'Odeslat požadavek',
    'setScene':       lambda args: f'Aktivovat scénu {args[0]}' if args else 'Aktivovat scénu',
    'ttsTest':        lambda args: 'TTS test',
    'setAudio':       lambda args: f'Audio: {args[0]}' if args else 'Audio ovládání',
    'setLights':      lambda args: f'Světla: {args[0]}' if args else 'Ovládání světel',
    'setVolume':      lambda args: f'Hlasitost: {args[0]}' if args else 'Hlasitost',
}

# Skip these fn names (already ok or self-explanatory)
SKIP_FNS = {
    'toggleHelp', 'switchPage', 'toggleVar',  # mají vlastní label, nebo sekce help-btn
    'closeModal', 'openModal',
}

# Match clickable element: <tag ...onclick="FN(args)"... > (no title in attrs)
# We capture: full_open_tag, attrs_before, fn_call, attrs_after
CLICKABLE_RE = re.compile(
    r'<(?P<tag>div|button|span|a)\s+(?P<attrs>[^>]*?onclick="(?P<fncall>[^"]*)"[^>]*?)>',
    re.IGNORECASE | re.DOTALL
)

TITLE_CHECK = re.compile(r'\btitle\s*=\s*["\']')

# Parse fn call — "fnName('arg1', 'arg2')" or "fnName()"
CALL_RE = re.compile(r'^\s*(\w+)\s*\((.*)\)\s*;?\s*$', re.DOTALL)

def parse_args(arg_str):
    """Simple string-literal arg parser. Handles 'x', "x", and numbers."""
    args = []
    # Match quoted strings or bare tokens separated by commas
    for m in re.finditer(r"'([^']*)'|\"([^\"]*)\"|([^,]+)", arg_str):
        v = m.group(1) if m.group(1) is not None else (m.group(2) if m.group(2) is not None else m.group(3))
        if v is not None:
            args.append(v.strip())
    return args


def gen_title(fncall):
    fncall = fncall.strip()
    if not fncall or fncall.startswith('//'):
        return None
    # Check custom exact match (normalized whitespace)
    norm = re.sub(r'\s+', ' ', fncall).strip().rstrip(';')
    if norm in CUSTOM_TITLES:
        return CUSTOM_TITLES[norm]
    # Parse
    m = CALL_RE.match(fncall)
    if not m:
        return None
    fn = m.group(1)
    if fn in SKIP_FNS:
        return None
    args_str = m.group(2) or ''
    args = parse_args(args_str)
    tpl = FN_TEMPLATES.get(fn)
    if tpl:
        try:
            return tpl(args)
        except Exception:
            return None
    return None  # no mapping → skip


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

    added = 0
    skipped = 0

    def repl(match):
        nonlocal added, skipped
        tag = match.group('tag')
        attrs = match.group('attrs')
        fncall = match.group('fncall')

        if TITLE_CHECK.search(attrs):
            return match.group(0)  # už má title

        title = gen_title(fncall)
        if not title:
            skipped += 1
            return match.group(0)

        # Escape quotes in title for HTML attr
        title_esc = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

        # Insert title after onclick="..."
        new_attrs = re.sub(
            r'(onclick="[^"]*")',
            lambda m: f'{m.group(1)} title="{title_esc}"',
            attrs,
            count=1
        )
        added += 1
        return f'<{tag} {new_attrs}>'

    new_html = CLICKABLE_RE.sub(repl, html)

    if added == 0:
        print(f'  - no changes: {name}')
        return False

    new_html = new_html.replace('</body>', f'<!-- {MARKER} -->\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK patched: {name} (+{added} titles, {skipped} skipped-no-mapping)')
    return True


def main():
    print('Phase 29: Mass tooltips (batch title= on interactive elements)')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
