"""
PHASE 8b — Logy compact layout pro desktop varianty (1920/2880)

Desktop HTMLs mají odlišný help panel + AI Tune formát než RPi, takže
phase 8 neaplikoval kompletně. Tento patch to dodělá.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# Desktop má samostatné AI TASKS + AI PENDING bloky. Přebalíme do 2-col gridu.
OLD_TASKS_PENDING = """    <div class="sect" style="color:var(--purple);">AI TASKS (GOOGLE SHEETS)</div>
    <div class="card">
      <div class="card-row"><span class="card-icon">📋</span><span class="card-lbl">Otevřené úkoly</span><div class="btn cyan" onclick="loadAITasks()" style="padding:4px 10px;font-size:10px;">⟳ Načíst</div></div>
      <div id="aiTasksList" style="margin-top:8px;font-family:var(--mono);font-size:10px;color:var(--tx3);">Klikni ⟳ pro načtení</div>
    </div>

    <div class="sect" style="color:var(--purple);">AI PENDING CHANGES</div>
    <div class="card">
      <div class="card-row"><span class="card-icon">⏳</span><span class="card-lbl">Čekající změny (48h okno)</span></div>
      <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);">—</div>
    </div>"""

NEW_TASKS_PENDING = """    <!-- PHASE8B_DESKTOP_APPLIED — 2-col AI Tasks + Pending -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px;">
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI TASKS (GOOGLE SHEETS)</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">📋</span><span class="card-lbl">Otevřené úkoly</span><div class="btn cyan" onclick="loadAITasks()" style="padding:3px 8px;font-size:10px;">⟳ Načíst</div></div>
          <div id="aiTasksList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:150px;overflow-y:auto;scrollbar-width:thin;">Klikni ⟳ pro načtení</div>
        </div>
      </div>
      <div>
        <div class="sect" style="color:var(--purple);margin-top:0;">AI PENDING CHANGES</div>
        <div class="card" style="padding:10px 12px;">
          <div class="card-row"><span class="card-icon">⏳</span><span class="card-lbl">Čekající změny (48h okno)</span></div>
          <div id="aiPendingList" style="margin-top:6px;font-family:var(--mono);font-size:10px;color:var(--tx3);max-height:150px;overflow-y:auto;scrollbar-width:thin;">—</div>
        </div>
      </div>
    </div>"""

# AI Tune na desktop — compact horizontal layout
OLD_TUNE = """    <div class="sect" style="color:var(--purple);margin-top:10px;">📊 AI AUTO-TUNE RANNÍ RUTINY</div>
    <div class="card" id="morningTuneCard" style="padding:14px;min-height:100px;">
      <div style="color:var(--tx3);text-align:center;padding:20px 0;">Klikni ⟳ Analyzovat</div>
    </div>
    <div style="display:flex;gap:10px;margin-top:6px;">
      <div class="btn" style="flex:0 0 auto;text-align:center;" onclick="loadMorningTune()">⟳ Zobrazit doporučení</div>
      <div class="btn" style="flex:0 0 auto;text-align:center;border-color:var(--purple);color:var(--purple);" onclick="runMorningTune()">🧠 Spustit analýzu (Gemini)</div>
    </div>"""

NEW_TUNE = """    <!-- PHASE8B_DESKTOP_APPLIED — compact AI Tune layout -->
    <div class="sect" style="color:var(--purple);margin-top:10px;">📊 AI AUTO-TUNE RANNÍ RUTINY</div>
    <div style="display:grid;grid-template-columns:1fr auto auto;gap:8px;align-items:stretch;">
      <div class="card" id="morningTuneCard" style="padding:10px 14px;min-height:70px;">
        <div style="color:var(--tx3);text-align:center;padding:14px 0;">Klikni ⟳ Zobrazit doporučení</div>
      </div>
      <div class="btn" style="text-align:center;display:flex;align-items:center;padding:0 18px;white-space:nowrap;" onclick="loadMorningTune()">⟳ Zobrazit</div>
      <div class="btn" style="text-align:center;border-color:var(--purple);color:var(--purple);display:flex;align-items:center;padding:0 18px;white-space:nowrap;" onclick="runMorningTune()">🧠 Gemini</div>
    </div>"""


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

    replace(OLD_TASKS_PENDING, NEW_TASKS_PENDING, 'Desktop: 2-col AI Tasks + Pending',
            marker='PHASE8B_DESKTOP_APPLIED — 2-col AI Tasks')
    replace(OLD_TUNE, NEW_TUNE, 'Desktop: compact AI Tune',
            marker='PHASE8B_DESKTOP_APPLIED — compact AI Tune layout')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE: {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 8b — Logy desktop varianty')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
