"""
Apply shade threshold 10000 → 20000 + AutoFix log panel to remaining dashboards.
Idempotent: skips if already patched.
"""
import os, re

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\rasberi\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\1\smart_home_rpi.html',
]

# Patch 1: shade > 10000 → > 20000 in issue check
P1_OLD = "if (shade > 10000) issues.push({sev:'H', msg:'shade='+shade+' >10000'});"
P1_NEW = ("// FIX 2026-04-20: max 20000 (bylo 10000) — letní slunce měří přes 10k lux\n"
          "    if (shade > 20000) issues.push({sev:'H', msg:'shade='+shade+' >20000'});")

# Patch 2: safeShade fallback range
P2_OLD = "const safeShade = (cfg.shade < 500 || cfg.shade > 10000) ? 3000 : cfg.shade;"
P2_NEW = "const safeShade = (cfg.shade < 500 || cfg.shade > 20000) ? 3000 : cfg.shade;  // FIX 2026-04-20: max 20000"

# Patch 3: sanity panel — add AutoFix log display
P3_OLD = """    if (issues.length === 0) html += '<div style="text-align:center;padding:8px;color:var(--green);">✅ OK</div>';
    else {
      html += '<div style="font-size:9px;color:var(--tx2);">'+issues.length+': 🔴'+H+' 🟡'+M+' 🟢'+L+'</div>';
      for (const i of issues.slice(0,4)) {
        const b = i.sev==='H'?'🔴':i.sev==='M'?'🟡':'🟢';
        html += '<div>'+b+' '+i.msg+'</div>';
      }
    }
    el.innerHTML = html;"""

P3_NEW = """    if (issues.length === 0) html += '<div style="text-align:center;padding:8px;color:var(--green);">✅ OK</div>';
    else {
      html += '<div style="font-size:9px;color:var(--tx2);">'+issues.length+': 🔴'+H+' 🟡'+M+' 🟢'+L+'</div>';
      for (const i of issues.slice(0,4)) {
        const b = i.sev==='H'?'🔴':i.sev==='M'?'🟡':'🟢';
        html += '<div>'+b+' '+i.msg+'</div>';
      }
    }
    // FIX 2026-04-20: poslední AutoFix akce — co bylo opraveno
    const lastFix = String(_getVar('sh_autofix_last') || '').trim();
    if (lastFix && lastFix.length > 5) {
      html += '<div style="margin-top:6px;padding-top:4px;border-top:1px solid var(--bd);font-size:9px;color:var(--cyan);">🩹 Poslední AutoFix:</div>';
      html += '<div style="font-size:9px;color:var(--tx2);line-height:1.4;white-space:pre-wrap;">'
            + lastFix.substring(0,400).replace(/</g,'&lt;') + '</div>';
    }
    el.innerHTML = html;"""

def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP: {fp}")
        return
    with open(fp,'r',encoding='utf-8',newline='') as f:
        c = f.read()
    orig = c
    changed = []
    # idempotence
    if '20000' in c and '🩹 Poslední AutoFix' in c:
        print(f"  ⏭️  ALREADY PATCHED: {os.path.basename(fp)}")
        return
    # Patch 1
    if P1_OLD in c:
        c = c.replace(P1_OLD, P1_NEW, 1); changed.append('shade>20000')
    else:
        crlf = P1_OLD.replace('\n','\r\n')
        if crlf in c:
            c = c.replace(crlf, P1_NEW.replace('\n','\r\n'), 1); changed.append('shade>20000(CRLF)')
    # Patch 2
    if P2_OLD in c:
        c = c.replace(P2_OLD, P2_NEW, 1); changed.append('safeShade max20k')
    else:
        crlf = P2_OLD.replace('\n','\r\n')
        if crlf in c:
            c = c.replace(crlf, P2_NEW.replace('\n','\r\n'), 1); changed.append('safeShade max20k(CRLF)')
    # Patch 3
    if P3_OLD in c:
        c = c.replace(P3_OLD, P3_NEW, 1); changed.append('AutoFix panel')
    else:
        crlf = P3_OLD.replace('\n','\r\n')
        new_crlf = P3_NEW.replace('\n','\r\n')
        if crlf in c:
            c = c.replace(crlf, new_crlf, 1); changed.append('AutoFix panel(CRLF)')
    if c != orig:
        with open(fp,'w',encoding='utf-8',newline='') as f: f.write(c)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
        for ch in changed: print(f"     + {ch}")
    else:
        print(f"  ⚠️  NO CHANGES: {os.path.basename(fp)}")

for f in FILES:
    print(f"Processing: {f}")
    patch(f)
    print()
print('Hotovo.')
