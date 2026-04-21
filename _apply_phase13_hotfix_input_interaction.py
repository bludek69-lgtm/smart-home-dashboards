"""
PHASE 13 HOTFIX — inputs neberou vstup

Root cause: `user-select: none` na body + `touch-action: manipulation` na *
se dědí na inputs → v některých browserech (zvláště Chromium kiosk mode)
blokuje psaní do inputs.

FIX: explicit override pro input / textarea / select — force interactive.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD = """html,body{overflow:hidden;overflow-x:hidden;background:linear-gradient(135deg,#1a0a2e 0%,#2d1b4e 25%,#4a2066 50%,#6b2fa0 75%,#8b3fa0 100%);color:var(--tx1);font-family:var(--sans);-webkit-font-smoothing:antialiased;user-select:none;height:100vh;width:100vw;}"""

NEW = """html,body{overflow:hidden;overflow-x:hidden;background:linear-gradient(135deg,#1a0a2e 0%,#2d1b4e 25%,#4a2066 50%,#6b2fa0 75%,#8b3fa0 100%);color:var(--tx1);font-family:var(--sans);-webkit-font-smoothing:antialiased;user-select:none;height:100vh;width:100vw;}
/* PHASE13_HOTFIX_INPUT_INTERACTION — inputs musí být interaktivní bez ohledu na user-select:none */
input,textarea,select{user-select:text !important;-webkit-user-select:text !important;-moz-user-select:text !important;touch-action:auto !important;pointer-events:auto !important;cursor:text;}
input[type=range]{cursor:pointer;}
input[type=checkbox],input[type=radio]{cursor:pointer;}"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    is_crlf = '\r\n' in c[:4096]
    if 'PHASE13_HOTFIX_INPUT_INTERACTION' in c:
        print(f'  ⏭️  {os.path.basename(fp)} (už applied)')
        return
    o = OLD if not is_crlf else OLD
    n = NEW.replace('\n','\r\n') if is_crlf else NEW
    if o in c:
        c2 = c.replace(o, n, 1)
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c2)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⚠️  {os.path.basename(fp)} anchor missing')


if __name__ == '__main__':
    print('PHASE 13 HOTFIX — input interaction override')
    for f in FILES:
        patch(f)
