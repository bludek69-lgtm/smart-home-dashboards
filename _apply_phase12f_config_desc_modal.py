"""
PHASE 12f — Config hint descriptions → modal pro dlouhé popisky

Config stránka (a device detail overlay) renderuje pro každou config row:
  <div class="cfg-hint">...desc text...</div>

Některé desc jsou dlouhé 200+ znaků → scroll.

FIX:
  - Desc > 120 znaků: truncate + "📖 klik pro celý"
  - Click na cfg-hint → modal s plným desc + current variable value
  - Desc <= 120: beze změny

Idempotent. Marker: PHASE12F_CONFIG_DESC_MODAL_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# Device cfg hint (openDeviceDetail)
OLD_DEVICE = """      if (v.desc) {
        html += '<div class="cfg-hint">' + v.desc + '</div>';
      }"""

NEW_DEVICE = """      if (v.desc) {
        // PHASE12F_CONFIG_DESC_MODAL_APPLIED — truncate + klik → modal
        const _isTrunc = v.desc.length > 120;
        const _short = _isTrunc ? v.desc.substring(0, 120).replace(/\\s+\\S*$/, '') + '…' : v.desc;
        const _attrs = _isTrunc
          ? ' onclick="openCfgDescModal(this)" style="cursor:pointer;" data-fulldesc="' + v.desc.replace(/"/g,'&quot;') + '" data-varname="' + v.name + '" data-varlabel="' + (v.label||'').replace(/"/g,'&quot;') + '"'
          : '';
        html += '<div class="cfg-hint"' + _attrs + '>' + _short + (_isTrunc ? ' <span style="color:var(--cyan);font-weight:600;">📖</span>' : '') + '</div>';
      }"""

# Zone cfg hint (renderSettingsForms)
OLD_ZONE = """        (v.desc ? '<div class="cfg-hint">' + v.desc + '</div>' : '');"""

NEW_ZONE = """        (v.desc ? (function(){
          // PHASE12F_CONFIG_DESC_MODAL_APPLIED — truncate + klik → modal
          const _isTrunc = v.desc.length > 120;
          const _short = _isTrunc ? v.desc.substring(0, 120).replace(/\\s+\\S*$/, '') + '…' : v.desc;
          const _attrs = _isTrunc
            ? ' onclick="openCfgDescModal(this)" style="cursor:pointer;" data-fulldesc="' + v.desc.replace(/"/g,'&quot;') + '" data-varname="' + v.name + '" data-varlabel="' + (v.label||'').replace(/"/g,'&quot;') + '"'
            : '';
          return '<div class="cfg-hint"' + _attrs + '>' + _short + (_isTrunc ? ' <span style="color:var(--cyan);font-weight:600;">📖</span>' : '') + '</div>';
        })() : '');"""

JS_HELPER = """
// PHASE12F_CONFIG_DESC_MODAL_APPLIED — config desc modal
function openCfgDescModal(el) {
  try {
    const desc = el.getAttribute('data-fulldesc') || el.textContent || '';
    const varName = el.getAttribute('data-varname') || '';
    const label = el.getAttribute('data-varlabel') || varName;
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const cur = (av[varName] && av[varName].value != null) ? av[varName].value : '(nenastaveno)';
    const esc = s => String(s).replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
    let html = '<div class="im-kv" style="margin-bottom:14px;">';
    html += '<div class="k">Proměnná</div><div class="v" style="font-family:var(--mono);">' + esc(varName) + '</div>';
    html += '<div class="k">Aktuální hodnota</div><div class="v"><strong style="color:var(--green);">' + esc(cur) + '</strong></div>';
    html += '</div>';
    html += '<div style="padding:10px 12px;background:rgba(255,255,255,.03);border-radius:8px;line-height:1.7;">' + esc(desc) + '</div>';
    html += '<div style="font-size:10px;color:var(--tx3);margin-top:10px;line-height:1.5;">💡 Tip: Hodnotu můžeš upravit v CONFIG stránce v input poli vedle popisku.</div>';
    openInfoModal('⚙ ' + (label || varName), html, { icon: '⚙', html: true });
  } catch(e) {
    openInfoModal('Config', 'Chyba: ' + e.message, { icon: '⚠' });
  }
}
"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    orig = c
    is_crlf = '\r\n' in c[:4096]
    marker = 'PHASE12F_CONFIG_DESC_MODAL_APPLIED'
    changes = []

    def do(old, new, label):
        nonlocal c
        old2 = old.replace('\n','\r\n') if is_crlf else old
        new2 = new.replace('\n','\r\n') if is_crlf else new
        if old2 in c:
            c = c.replace(old2, new2, 1)
            changes.append('+ ' + label)
        elif marker in c:
            changes.append('⏭ ' + label + ' (už applied)')
        else:
            changes.append('⏭ ' + label + ' (anchor missing)')

    do(OLD_DEVICE, NEW_DEVICE, 'Device cfg hint (openDeviceDetail)')
    do(OLD_ZONE, NEW_ZONE, 'Zone cfg hint (renderSettingsForms)')

    if marker + ' — config desc modal' in c:
        changes.append('⏭ JS helper (už applied)')
    else:
        idx = c.rfind('</script>')
        if idx >= 0:
            inj = JS_HELPER.replace('\n','\r\n') if is_crlf else JS_HELPER
            c = c[:idx] + inj + c[idx:]
            changes.append('+ JS helper openCfgDescModal')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    for ch in changes:
        print(f'     {ch}')


if __name__ == '__main__':
    print('PHASE 12f — Config hint desc → modal')
    print('='*60)
    for f in FILES:
        patch(f)
