"""
PHASE 14 — AI Autonomy level tile tooltips + klik → modal s popisem

Přidá title= tooltip + klik mimo setAutoLevel (stačí double-click) otevře
modal s vysvětlením co každá úroveň znamená. Tak user vidí co "LEVEL 4"
skutečně dělá.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# Pattern common to all variants
OLD = """      <div class="auto-lv" onclick="setAutoLevel(1)"><div class="lv-num">1</div><div class="lv-lbl">LOG</div></div>
      <div class="auto-lv" onclick="setAutoLevel(2)"><div class="lv-num">2</div><div class="lv-lbl">SUGGEST</div></div>
      <div class="auto-lv" onclick="setAutoLevel(3)"><div class="lv-num">3</div><div class="lv-lbl">ASK</div></div>"""

NEW = """      <div class="auto-lv" onclick="setAutoLevel(1)" title="LEVEL 1: AI jen loguje události, nezasahuje. Bezpečný režim pro monitoring." ondblclick="openAiAutonomyModal()"><div class="lv-num">1</div><div class="lv-lbl">LOG</div></div>
      <div class="auto-lv" onclick="setAutoLevel(2)" title="LEVEL 2: AI navrhuje přes sh_ai_pending_changes. User musí schválit." ondblclick="openAiAutonomyModal()"><div class="lv-num">2</div><div class="lv-lbl">SUGGEST</div></div>
      <div class="auto-lv" onclick="setAutoLevel(3)" title="LEVEL 3: AI se ptá TTS ('Chceš X?'). Interaktivní režim." ondblclick="openAiAutonomyModal()"><div class="lv-num">3</div><div class="lv-lbl">ASK</div></div>"""

OLD_AUTO = """      <div class="auto-lv" onclick="setAutoLevel(4)"><div class="lv-num">4</div><div class="lv-lbl">AUTO</div></div>"""

NEW_AUTO = """      <div class="auto-lv" onclick="setAutoLevel(4)" title="LEVEL 4: AI může provést SAFE akce (dim, comfort scene). Aktivní teď. Dvojklik = detail." ondblclick="openAiAutonomyModal()"><div class="lv-num">4</div><div class="lv-lbl">AUTO</div></div>"""

# JS helper before </script>
JS_HELPER = """
// PHASE14_AI_AUTONOMY_MODAL_APPLIED — vysvětlení AI Autonomy levels
function openAiAutonomyModal() {
  try {
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const cur = Number((av['sh_ai_autonomy_level'] && av['sh_ai_autonomy_level'].value) || 1);
    const levels = [
      {n:1, lbl:'LOG',     icon:'📝', color:'var(--tx2)',    desc:'AI jen loguje události. <strong>Nezasahuje</strong> do systému. Bezpečný monitoring režim.', actions:'Čistě pozorovací. Žádné akce.'},
      {n:2, lbl:'SUGGEST', icon:'💡', color:'var(--cyan)',   desc:'AI generuje návrhy do <code>sh_ai_pending_changes</code>. User musí ručně schválit v dashboardu.', actions:'Návrhy v "AI Pending Changes" kartě na Logy stránce.'},
      {n:3, lbl:'ASK',     icon:'❓', color:'var(--orange)', desc:'Pokud confidence > threshold, AI pošle TTS otázku (např. "Luďku, chceš spustit relax scénu?").', actions:'Interaktivní dialog přes reproduktor.'},
      {n:4, lbl:'AUTO',    icon:'🤖', color:'var(--purple)', desc:'AI může provést <strong>SAFE akce</strong> bez potvrzení (dim, comfort scene, morning prep). <strong>Kritické akce zůstávají blokované.</strong>', actions:'Auto: dim ± 10%, scéna comfort/relax, pre-morning prep, reset event proměnných.'},
    ];
    let html = '<div style="padding:12px;background:rgba(176,133,255,.08);border:1px solid var(--bda);border-radius:8px;margin-bottom:14px;font-size:13px;line-height:1.6;">';
    html += '<strong>Aktuální úroveň: <span style="color:' + (levels[cur-1]||{}).color + ';font-size:18px;">' + cur + ' · ' + ((levels[cur-1]||{}).lbl || '—') + '</span></strong>';
    html += '</div>';
    levels.forEach(l => {
      const isCur = l.n === cur;
      const bg = isCur ? 'rgba(176,133,255,.12)' : 'rgba(255,255,255,.03)';
      const border = isCur ? 'border:2px solid var(--purple);' : 'border:1px solid var(--bd);';
      html += '<div style="padding:12px 14px;background:' + bg + ';' + border + 'border-radius:8px;margin-bottom:8px;">';
      html += '<div style="font-size:14px;font-weight:600;color:' + l.color + ';margin-bottom:4px;">' + l.icon + ' Level ' + l.n + ' — ' + l.lbl + (isCur ? ' <span style="font-size:10px;color:var(--tx3);">· aktivní</span>' : '') + '</div>';
      html += '<div style="font-size:12px;color:var(--tx2);margin-bottom:6px;">' + l.desc + '</div>';
      html += '<div style="font-size:11px;color:var(--tx3);font-style:italic;">' + l.actions + '</div>';
      html += '</div>';
    });
    // FORBIDDEN actions reminder
    html += '<div style="margin-top:10px;padding:10px 12px;background:rgba(255,107,107,.08);border:1px solid rgba(255,107,107,.3);border-radius:8px;">';
    html += '<div style="font-size:11px;color:var(--red);font-weight:600;margin-bottom:4px;">🔴 AI NIKDY nesmí (i v AUTO):</div>';
    html += '<div style="font-size:11px;color:var(--tx2);line-height:1.5;">Přepsat sh_spim, sh_rezim_doma, DOVOLENA · Ovládat kameru/alarm · Vypnout kritické plugs (PC, FRIDGE, BOILER) · Dveřní zámek</div>';
    html += '</div>';
    html += '<div style="margin-top:10px;font-size:10px;color:var(--tx3);">💡 Klik na číslo = změna úrovně. Dvojklik = tento popup.</div>';
    openInfoModal('🤖 AI Autonomy — vysvětlení úrovní', html, { icon: '🤖', html: true });
  } catch(e) {
    openInfoModal('AI Autonomy', 'Chyba: ' + e.message, { icon: '⚠' });
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
    changes = []

    def do(old, new, label):
        nonlocal c
        old2 = old.replace('\n','\r\n') if is_crlf else old
        new2 = new.replace('\n','\r\n') if is_crlf else new
        if old2 in c:
            c = c.replace(old2, new2, 1)
            changes.append('+ ' + label)
        elif 'PHASE14_AI_AUTONOMY_MODAL_APPLIED' in c or 'openAiAutonomyModal' in c:
            changes.append('⏭ ' + label + ' (už applied)')
        else:
            changes.append('⏭ ' + label + ' (anchor missing)')

    do(OLD, NEW, 'Levels 1-3 tooltips + dblclick')
    do(OLD_AUTO, NEW_AUTO, 'Level 4 tooltip + dblclick')

    if 'PHASE14_AI_AUTONOMY_MODAL_APPLIED' in c:
        changes.append('⏭ JS helper (už applied)')
    else:
        idx = c.rfind('</script>')
        if idx >= 0:
            inj = JS_HELPER.replace('\n','\r\n') if is_crlf else JS_HELPER
            c = c[:idx] + inj + c[idx:]
            changes.append('+ JS helper openAiAutonomyModal')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    for ch in changes:
        print(f'     {ch}')


if __name__ == '__main__':
    print('PHASE 14 — AI Autonomy tooltips + modal')
    print('='*60)
    for f in FILES:
        patch(f)
