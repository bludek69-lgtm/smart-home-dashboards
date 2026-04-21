"""
PHASE 13d — Roleta cfg read-only → klikací pro editaci

CONTEXT:
  Sekce "A JÍDELNA — DETAILNÍ NASTAVENÍ" (roletaCfgCard) má <span class="roleta-cfg-val">
  READ-ONLY ZOBRAZENÍ hodnot. Nejde do nich psát protože NEJSOU input pole.

FIX:
  1) Klik na span otevře inline input
  2) Enter nebo blur → save přes writeVar
  3) Esc → cancel
  4) Visual feedback (zelený border po save)

Idempotent. Marker: PHASE13D_ROLETA_EDITABLE_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: renderRoletaCfg — add onclick + title na spans
# ═══════════════════════════════════════════════════════════════════════════
OLD = """function renderRoletaCfg() {
  const mapping = [
    ['rcfg-safety',  'sh_cfg_blind_safety_threshold', ''],
    ['rcfg-shade',   'sh_cfg_blind_shade_position',   ''],
    ['rcfg-morning', 'sh_cfg_lux_roleta_morning',     ' lux'],
    ['rcfg-open',    'sh_cfg_lux_roleta_open',        ' lux'],
    ['rcfg-shade-lux','sh_cfg_lux_roleta_shade',      ' lux'],
    ['rcfg-evening', 'sh_cfg_lux_roleta_evening_close',' lux'],
  ];
  for (const [id, name, suffix] of mapping) {
    const el = document.getElementById(id);
    if (!el) continue;
    const val = ALL_VARS[name]?.value;
    el.textContent = (val !== undefined && val !== null) ? String(val) + suffix : '—';
  }
}"""

NEW = """// PHASE13D_ROLETA_EDITABLE_APPLIED — spans jsou teď klikací pro inline edit
function renderRoletaCfg() {
  const mapping = [
    ['rcfg-safety',   'sh_cfg_blind_safety_threshold', '',     'float'],
    ['rcfg-shade',    'sh_cfg_blind_shade_position',   '',     'float'],
    ['rcfg-morning',  'sh_cfg_lux_roleta_morning',     ' lux', 'int'],
    ['rcfg-open',     'sh_cfg_lux_roleta_open',        ' lux', 'int'],
    ['rcfg-shade-lux','sh_cfg_lux_roleta_shade',       ' lux', 'int'],
    ['rcfg-evening',  'sh_cfg_lux_roleta_evening_close',' lux','int'],
  ];
  for (const [id, name, suffix, type] of mapping) {
    const el = document.getElementById(id);
    if (!el) continue;
    const val = ALL_VARS[name]?.value;
    el.textContent = (val !== undefined && val !== null) ? String(val) + suffix : '—';
    el.setAttribute('data-varname', name);
    el.setAttribute('data-suffix', suffix);
    el.setAttribute('data-vartype', type);
    el.style.cursor = 'pointer';
    el.title = 'Klikni pro úpravu (' + name + ')';
    el.onclick = function() { editRoletaCfgInline(el); };
  }
}

// PHASE13D — inline edit helper
function editRoletaCfgInline(span) {
  if (!span || span.dataset.editing === '1') return;
  const name = span.getAttribute('data-varname');
  const suffix = span.getAttribute('data-suffix') || '';
  const type = span.getAttribute('data-vartype') || 'int';
  const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
  const curVal = (av[name] && av[name].value != null) ? av[name].value : '';
  span.dataset.editing = '1';
  const origText = span.textContent;

  // Create input overlaying the span
  const input = document.createElement('input');
  input.type = 'number';
  input.step = type === 'float' ? '0.05' : '1';
  input.value = curVal;
  input.style.width = '80px';
  input.style.padding = '4px 8px';
  input.style.background = 'var(--bg3)';
  input.style.border = '1px solid var(--cyan)';
  input.style.borderRadius = 'var(--r)';
  input.style.color = 'var(--tx1)';
  input.style.fontFamily = 'var(--mono)';
  input.style.fontSize = '12px';
  input.style.textAlign = 'center';
  input.style.outline = 'none';

  // Replace span content with input
  span.textContent = '';
  span.appendChild(input);
  span.style.cursor = 'default';
  input.focus();
  input.select();

  let saved = false;
  const cleanup = (newText, statusColor) => {
    if (saved) return;
    saved = true;
    span.textContent = newText;
    span.dataset.editing = '0';
    span.style.cursor = 'pointer';
    if (statusColor) {
      span.style.transition = 'color .3s';
      span.style.color = statusColor;
      setTimeout(() => { span.style.color = ''; }, 2000);
    }
  };

  const saveValue = async () => {
    const raw = input.value;
    const num = type === 'float' ? parseFloat(raw) : parseInt(raw, 10);
    if (isNaN(num)) {
      cleanup(origText);
      try { flash('✗ Neplatné číslo'); } catch(_){}
      return;
    }
    if (String(num) === String(curVal)) {
      cleanup(origText);
      return;
    }
    try {
      const ok = await writeVar(name, num);
      if (ok) {
        cleanup(String(num) + suffix, 'var(--green)');
        try { flash('✓ ' + name + ' = ' + num); } catch(_){}
      } else {
        cleanup(origText);
        try { flash('✗ Nelze uložit ' + name); } catch(_){}
      }
    } catch(e) {
      cleanup(origText);
      try { flash('✗ ' + e.message); } catch(_){}
    }
  };

  input.addEventListener('blur', saveValue);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
    if (e.key === 'Escape') { saved = true; cleanup(origText); span.dataset.editing = '0'; }
  });
}"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    is_crlf = '\r\n' in c[:4096]
    if 'PHASE13D_ROLETA_EDITABLE_APPLIED' in c:
        print(f'  ⏭️  {os.path.basename(fp)} (už applied)')
        return
    o = OLD.replace('\n','\r\n') if is_crlf else OLD
    n = NEW.replace('\n','\r\n') if is_crlf else NEW
    if o in c:
        c2 = c.replace(o, n, 1)
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c2)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⚠️  {os.path.basename(fp)} anchor missing')


if __name__ == '__main__':
    print('PHASE 13d — Roleta cfg spans → editable inline')
    for f in FILES:
        patch(f)
