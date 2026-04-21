"""
Phase 21 (2026-04-21) — Roleta config: reálné hodnoty + cross-field validation (sanity check)

Zjištění z Lux Monitor sheet (týden dat):
  - Top 5 reálných hodnot: 29,812 · 22,589 · 24,154 · 21,872 · 18,075 lux
  - Median top15: 15,360 lux
  - Typické slunce v jídelně: 20,000–30,000 lux při přímém slunci

Co Phase 21 dělá:
  1. Update popisků reálnými hodnotami (ze Sheets data)
  2. Přidá "sanity check" panel v roleta card — živá validace mezi proměnnými
  3. Do editRoletaCfgInline přidá pre-save validaci (varování před uložením nesmyslů)
  4. Cross-field checks:
     - shade > open (jinak shade nikdy nezafunguje)
     - shade > evening_close × 10 (logický rozdíl mezi day/night thresholds)
     - hysteresis > 0 AND hysteresis < shade/2
     - 0 < safety < 1
     - 0 <= shade_position <= 1
     - morning < open
"""
import os, re, sys

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'validateRoletaCfg'

# ═══════════════════════════════════════════════════════════════════════════
# 1. Update popisku pro shade_lux (Phase 19 měl doporučení, teď přesnější)
# ═══════════════════════════════════════════════════════════════════════════
OLD_SHADE_EXAMPLE = 'Příklad: 8000 lux. <span style="color:var(--orange);">⚠️ Pokud je hodnota příliš nízká, roleta se bude často pohybovat. Doporučeno 5000–15000 + hysterezis 2000–3000.</span>'
NEW_SHADE_EXAMPLE = 'Na základě tvých reálných dat (týden): max 29,812 · top5 ≥ 18,000 · median top15 = 15,360 lux. <strong>Doporučeno 15,000–25,000</strong> + hysterezis 2000–3000. Výš (30,000+) znamená že se shade spustí jen při extrémním slunci.'

# ═══════════════════════════════════════════════════════════════════════════
# 2. Nový sanity check panel — vkládá se pod roletaCfgCard
# ═══════════════════════════════════════════════════════════════════════════
SANITY_PANEL = '''    <div id="roletaSanityPanel" style="margin-bottom:10px;font-size:11px;padding:8px 12px;border-radius:var(--r2);border:1px solid rgba(100,244,216,.2);background:rgba(100,244,216,.05);">
      <div style="font-weight:600;color:var(--cyan);margin-bottom:4px;">🔍 Kontrola konzistence (sanity check)</div>
      <div id="roletaSanityList" style="color:var(--tx2);line-height:1.5;">—</div>
    </div>
'''

# Insert after roletaCfgCard close
INSERT_ANCHOR_SANITY = re.compile(
    r'(    </div>\s*\n\s*<!-- Config: 2 columns)',
    re.DOTALL
)

# ═══════════════════════════════════════════════════════════════════════════
# 3. Nové JS funkce: validateRoletaCfg + renderer
# ═══════════════════════════════════════════════════════════════════════════
NEW_JS = '''

// ═════════ Phase 21 — Roleta sanity check ═════════
function validateRoletaCfg(overrides) {
  // overrides: { varName: value } — pro pre-save preview
  const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
  const get = (name) => {
    if (overrides && name in overrides) return Number(overrides[name]);
    const v = av[name]?.value;
    return v != null ? Number(v) : NaN;
  };

  const safety   = get('sh_cfg_blind_safety_threshold');
  const shadePos = get('sh_cfg_blind_shade_position');
  const morning  = get('sh_cfg_lux_roleta_morning');
  const open     = get('sh_cfg_lux_roleta_open');
  const shade    = get('sh_cfg_lux_roleta_shade');
  const evening  = get('sh_cfg_lux_roleta_evening_close');
  const hyst     = get('sh_cfg_lux_roleta_hysteresis');

  const issues = [];
  const ok = [];

  // Safety threshold — pozice 0-1
  if (!Number.isFinite(safety) || safety < 0 || safety > 1) {
    issues.push({ sev: 'err', msg: 'Safety threshold mimo rozsah 0–1 (nyní: ' + safety + ')' });
  } else if (safety > 0.5) {
    issues.push({ sev: 'warn', msg: 'Safety threshold ' + safety + ' je vysoký — max 50% zavření při otevřeném okně' });
  } else {
    ok.push('Safety threshold ' + safety + ' OK');
  }

  // Shade position
  if (!Number.isFinite(shadePos) || shadePos < 0 || shadePos > 1) {
    issues.push({ sev: 'err', msg: 'Shade position mimo rozsah 0–1 (nyní: ' + shadePos + ')' });
  } else {
    ok.push('Shade position ' + shadePos + ' OK');
  }

  // Morning < Open — ranní práh musí být nižší než denní
  if (Number.isFinite(morning) && Number.isFinite(open) && morning >= open) {
    issues.push({ sev: 'warn', msg: 'Ranní práh (' + morning + ') ≥ denní práh (' + open + ') — ráno se bude brát za "už světlo" hned' });
  } else if (Number.isFinite(morning) && Number.isFinite(open)) {
    ok.push('Morning ' + morning + ' < Open ' + open + ' OK');
  }

  // Shade > Open — shade musí být výrazně nad open (jinak shade nikdy nezafunguje nebo splyne)
  if (Number.isFinite(open) && Number.isFinite(shade) && shade <= open) {
    issues.push({ sev: 'err', msg: '🚨 Shade (' + shade + ') ≤ Open (' + open + ') — STÁHNOUT PRÁH MUSÍ BÝT VYŠŠÍ NEŽ VYTÁHNOUT PRÁH!' });
  } else if (Number.isFinite(open) && Number.isFinite(shade) && shade < open * 10) {
    issues.push({ sev: 'warn', msg: 'Shade (' + shade + ') je jen ' + Math.round(shade/open) + '× větší než Open (' + open + ') — typicky 20–100×' });
  } else if (Number.isFinite(shade)) {
    ok.push('Shade ' + shade + ' > Open ' + open + ' OK');
  }

  // Shade reasonable value (based on real data)
  if (Number.isFinite(shade)) {
    if (shade < 5000) {
      issues.push({ sev: 'warn', msg: 'Shade ' + shade + ' je nízký — roleta se bude stahovat i při oblačnosti (typické lux ' + Math.round(shade) + '+)' });
    } else if (shade > 50000) {
      issues.push({ sev: 'warn', msg: 'Shade ' + shade + ' je extrémně vysoký — shade se nikdy nespustí (max reálný lux ~30,000)' });
    }
  }

  // Evening close — má být nízký (pár stovek lux = večer/noc)
  if (Number.isFinite(evening) && evening > 1000) {
    issues.push({ sev: 'warn', msg: 'Večerní zavření ' + evening + ' lux je vysoké — roleta bude zavírat i za soumraku' });
  }

  // Hysteresis
  if (Number.isFinite(hyst)) {
    if (hyst <= 0) {
      issues.push({ sev: 'err', msg: 'Hysterezis musí být > 0 (nyní: ' + hyst + ') — jinak nebude fungovat anti-yo-yo' });
    } else if (Number.isFinite(shade) && hyst >= shade / 2) {
      issues.push({ sev: 'warn', msg: 'Hysterezis (' + hyst + ') je ≥ polovina shade (' + shade + ') — shade by se málem nikdy nevracel' });
    } else if (Number.isFinite(shade) && hyst < shade * 0.1) {
      issues.push({ sev: 'warn', msg: 'Hysterezis (' + hyst + ') je velmi malý (<10% shade) — yo-yo může přetrvávat' });
    } else {
      ok.push('Hysterezis ' + hyst + ' OK (doporučeno 15–25% shade)');
    }
  } else {
    issues.push({ sev: 'info', msg: 'Hysterezis proměnná neexistuje — vytvoř sh_cfg_lux_roleta_hysteresis (number, default 3000)' });
  }

  return { issues, ok };
}

function renderRoletaSanity() {
  const box = document.getElementById('roletaSanityList');
  if (!box) return;
  const { issues, ok } = validateRoletaCfg();
  if (issues.length === 0) {
    box.innerHTML = '<span style="color:var(--green);">✅ Všechna nastavení dávají smysl (' + ok.length + ' kontrol)</span>';
    const pnl = document.getElementById('roletaSanityPanel');
    if (pnl) {
      pnl.style.borderColor = 'rgba(100,244,216,.3)';
      pnl.style.background  = 'rgba(100,244,216,.05)';
    }
    return;
  }
  const items = issues.map(i => {
    const color = i.sev === 'err' ? 'var(--red)' : i.sev === 'warn' ? 'var(--orange)' : 'var(--cyan)';
    const icon = i.sev === 'err' ? '🚨' : i.sev === 'warn' ? '⚠️' : 'ℹ️';
    return '<div style="color:' + color + ';">' + icon + ' ' + i.msg + '</div>';
  }).join('');
  box.innerHTML = items;
  const pnl = document.getElementById('roletaSanityPanel');
  if (pnl) {
    const hasErr = issues.some(i => i.sev === 'err');
    pnl.style.borderColor = hasErr ? 'rgba(255,70,90,.4)' : 'rgba(255,165,0,.4)';
    pnl.style.background  = hasErr ? 'rgba(255,70,90,.08)' : 'rgba(255,165,0,.06)';
  }
}

// Hook do renderRoletaCfg (volá se po každém refreshi)
(function() {
  const _orig = window.renderRoletaCfg || function(){};
  window.renderRoletaCfg = function() {
    _orig.apply(this, arguments);
    try { renderRoletaSanity(); } catch(_){}
  };
})();

// Hook do editRoletaCfgInline — pre-save warning pokud nesmysl
(function() {
  const _orig = window.editRoletaCfgInline;
  if (!_orig) return;
  window.editRoletaCfgInline = function(span) {
    const name = span && span.getAttribute ? span.getAttribute('data-varname') : null;
    const result = _orig.apply(this, arguments);

    // After edit input created, attach blur hook
    setTimeout(() => {
      const input = span.querySelector('input');
      if (!input) return;

      const validateBeforeSave = () => {
        const raw = input.value;
        const num = Number(raw);
        if (!Number.isFinite(num)) return;
        const preview = {};
        preview[name] = num;
        const { issues } = validateRoletaCfg(preview);
        const crit = issues.filter(i => i.sev === 'err');
        if (crit.length > 0) {
          try {
            flash('⚠️ Sanity: ' + crit[0].msg);
          } catch(_){}
        }
      };
      input.addEventListener('blur', validateBeforeSave, { once: true });
    }, 50);

    return result;
  };
})();

// Refresh sanity panel při každém var map reload
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => { try { renderRoletaSanity(); } catch(_){} }, 2000);
});
// ═════════ /Phase 21 ═════════
'''

# Insert JS před Phase 20 marker nebo </script></body>
JS_ANCHOR = re.compile(
    r'(// ═+ /Phase 20 ═+|// ═+ /Phase 19 ═+|// ═+ /Phase 18 ═+|</script>\s*</body>)',
    re.IGNORECASE
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

    # 1. Update shade example desc
    if OLD_SHADE_EXAMPLE in html:
        html = html.replace(OLD_SHADE_EXAMPLE, NEW_SHADE_EXAMPLE, 1)
        changes += 1
    else:
        print(f'    ⚠ shade example nenalezen (možná jiné rozlišení): {os.path.basename(path)}')

    # 2. Insert sanity panel
    m = INSERT_ANCHOR_SANITY.search(html)
    if m:
        html = html[:m.start()] + '    </div>\n\n' + SANITY_PANEL + '\n    <!-- Config: 2 columns' + html[m.end():]
        # Remove extra line we added duplicate
        html = html.replace('    </div>\n\n    <div id="roletaSanityPanel"', '    </div>\n\n' + SANITY_PANEL.rstrip() + '\n    <!-- placeholder-removed -->')
        # Actually simpler: use group replacement
    # Simpler approach: direct substitute
    html_simple = html
    old_boundary = '    </div>\n\n    <!-- Config: 2 columns'
    new_boundary = '    </div>\n\n' + SANITY_PANEL + '    <!-- Config: 2 columns'
    if old_boundary in html_simple and 'id="roletaSanityPanel"' not in html_simple:
        html_simple = html_simple.replace(old_boundary, new_boundary, 1)
        html = html_simple
        changes += 1
    elif 'id="roletaSanityPanel"' in html:
        # already inserted by earlier failed attempt
        pass
    else:
        print(f'    ⚠ sanity panel anchor nenalezen: {os.path.basename(path)}')

    # 3. Insert JS code
    m = JS_ANCHOR.search(html)
    if m and MARKER not in html:
        html = html[:m.start()] + NEW_JS + '\n\n' + m.group(0) + html[m.end():]
        changes += 1
    elif MARKER in html:
        pass  # already inserted

    if changes == 0:
        print(f'  ✗ no changes: {os.path.basename(path)}')
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✓ patched: {os.path.basename(path)} ({len(html)-orig_len:+d} bytes, {changes} changes)')
    return True


def main():
    print('Phase 21: Roleta sanity check + real data thresholds')
    ok = 0
    for p in FILES:
        if patch_file(p):
            ok += 1
    print(f'\nDone: {ok}/{len(FILES)} files patched')
    return 0 if ok == len(FILES) else 1


if __name__ == '__main__':
    sys.exit(main())
