"""
PHASE 13b — Nuclear input fix

Předchozí user-select:text nestačí. User pořád nemůže psát.
Přidám maximálně defenzivní CSS + tabindex + explicit read-write.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

OLD = """/* PHASE13_HOTFIX_INPUT_INTERACTION — inputs musí být interaktivní bez ohledu na user-select:none */
input,textarea,select{user-select:text !important;-webkit-user-select:text !important;-moz-user-select:text !important;touch-action:auto !important;pointer-events:auto !important;cursor:text;}
input[type=range]{cursor:pointer;}
input[type=checkbox],input[type=radio]{cursor:pointer;}"""

NEW = """/* PHASE13B_NUCLEAR — aggressive input interactivity override */
input, textarea, select {
  user-select: text !important;
  -webkit-user-select: text !important;
  -moz-user-select: text !important;
  -ms-user-select: text !important;
  touch-action: auto !important;
  pointer-events: auto !important;
  -webkit-user-modify: read-write !important;
  user-modify: read-write !important;
  caret-color: var(--cyan) !important;
  cursor: text !important;
}
input[type=range] { cursor: pointer !important; }
input[type=checkbox], input[type=radio], input[type=button], input[type=submit] { cursor: pointer !important; }
input[readonly], input[disabled], textarea[readonly], textarea[disabled] {
  cursor: not-allowed !important;
}
/* Ensure no element covers inputs in overlays / config pages */
.dev-detail-overlay input, #page-settings input, .cfg-row input {
  position: relative !important;
  z-index: 1 !important;
}
/* Force Chromium to accept typing even in kiosk mode */
input:focus, textarea:focus {
  -webkit-user-modify: read-write-plaintext-only !important;
  outline: 2px solid var(--cyan) !important;
  outline-offset: 1px !important;
}"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    is_crlf = '\r\n' in c[:4096]
    if 'PHASE13B_NUCLEAR' in c:
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
    print('PHASE 13b — Nuclear input fix')
    for f in FILES:
        patch(f)
