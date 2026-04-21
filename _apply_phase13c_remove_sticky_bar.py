"""
PHASE 13c — Remove sticky save bar (blokuje kliknutí na inputy)

Root cause: phase 13 přidala `position:sticky;bottom:0;z-index:10` na .cfg-bottom.
Sticky bar má z-index 10, inputy jen z-index 1 → bar překrývá spodní inputy
v kliknutelné vrstvě i když nejsou vizuálně za ním.

FIX:
  - Remove sticky positioning (vrátit na static)
  - Ponechat overflow-y:auto na page-settings (scroll funguje)
  - Save button je přirozeně na konci, user scrolluje
  - Add padding-bottom pro komfort
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD = """#page-settings.active{display:flex !important;flex-direction:column;overflow-y:auto !important;overflow-x:hidden;scrollbar-width:thin;scrollbar-color:var(--bg4) transparent;}
/* PHASE13_CONFIG_SAVE_FIX_APPLIED — sticky save bar at bottom */
#page-settings .cfg-bottom{position:sticky;bottom:0;background:linear-gradient(180deg,transparent 0%,var(--bg1) 20%,var(--bg1) 100%);padding-top:10px;z-index:10;}
#page-settings .cfg-row input.cfg-saved{border-color:var(--green) !important;box-shadow:0 0 8px rgba(94,232,160,.25);transition:border-color .3s;}"""

NEW = """#page-settings.active{display:flex !important;flex-direction:column;overflow-y:auto !important;overflow-x:hidden;padding-bottom:40px;scrollbar-width:thin;scrollbar-color:var(--bg4) transparent;}
/* PHASE13C — sticky REMOVED (blokovala kliknutí na inputs). Save button na konci, user scrolluje. */
#page-settings .cfg-bottom{background:transparent;padding-top:10px;}
#page-settings .cfg-row input.cfg-saved{border-color:var(--green) !important;box-shadow:0 0 8px rgba(94,232,160,.25);transition:border-color .3s;}"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    is_crlf = '\r\n' in c[:4096]
    if 'PHASE13C — sticky REMOVED' in c:
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
    print('PHASE 13c — Remove sticky save bar')
    for f in FILES:
        patch(f)
