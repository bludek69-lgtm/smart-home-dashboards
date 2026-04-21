"""
PHASE 5 — TTS diakritika fix + rozšíření ZONE_HELP o nové features
Idempotent. Marker: PHASE5_TTS_HELPS_APPLIED.

FIXES:
  1) TTS Pomodoro chyběla diakritika (v6.0 porušení "čeština s plnou diakritikou")
     'Pauza pet minut' → 'Pauza pět minut'
     'Pauza skoncila. Pokracujeme v praci' → 'Pauza skončila. Pokračujeme v práci'
  2) ZONE_HELP chyběla zmínka o nových features z Phase 1-4:
     - pracovna: Xiaomi button + Pomodoro
     - bedroom: TV remote + Zvlhčovač
     - bathroom: Giuseppe vysavač
     - kitchen: Lednice spotřeba graf
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: TTS diakritika
# ═══════════════════════════════════════════════════════════════════════════
REPLACEMENTS = [
    (
        "sendReq('sh_tts_text', 'Pomodoro hotovo. Pauza pet minut.')",
        "sendReq('sh_tts_text', 'Pomodoro hotovo. Pauza pět minut.')",
        "TTS: Pauza pet minut → Pauza pět minut"
    ),
    (
        "sendReq('sh_tts_text', 'Pauza skoncila. Pokracujeme v praci.')",
        "sendReq('sh_tts_text', 'Pauza skončila. Pokračujeme v práci.')",
        "TTS: Pauza skoncila → Pauza skončila, Pokracujeme v praci → Pokračujeme v práci"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: ZONE_HELP — rozšířit o nové features
# ═══════════════════════════════════════════════════════════════════════════
ZONE_HELP_UPDATES = [
    # Pracovna — přidat Xiaomi + Pomodoro
    (
        """  pracovna: {
    title: '💻 Pracovna',
    items: [
      '<strong>Zasuvka pracovna</strong> — KRITICKÁ',
      '<strong>Světlo</strong> — manuál'
    ],
    flow: 'Kritická ochrana — drží ON.'
  },""",
        """  pracovna: {
    title: '💻 Pracovna',
    items: [
      '<strong>Zasuvka pracovna</strong> — KRITICKÁ',
      '<strong>Světlo</strong> — manuál',
      '<strong>🎮 Xiaomi button</strong> (Pc Setup) — 6 gest: 1× světlo · 2× PC · 3× kávovar · 4× scéna WORK · long = konec práce',
      '<strong>🍅 Pomodoro</strong> — 25/5 min cykly, TTS do kuchyně na přechodu, persistence v prohlížeči'
    ],
    flow: 'Kritická ochrana — drží ON. Xiaomi button + Pomodoro tiles v sekci Pc Setup.'
  },"""
    ),
    # Bedroom — přidat TV remote + Zvlhčovač
    (
        """  bedroom: {
    title: '🛏 Ložnice',
    items: [
      '<strong>Zarovka Loznice</strong> — hlavní + sunrise 6 kroků',
      '<strong>Led pasek postel</strong> — noční orientace',
      '<strong>Nest Hub Max</strong> — briefing',
      '<strong>Motion senzor</strong> — probuzení/WC'
    ],
    flow: 'Motion < 3:00 = WC. 3:00+ 2× do 3 min = wake. Alarm → sunrise.'
  },""",
        """  bedroom: {
    title: '🛏 Ložnice',
    items: [
      '<strong>Zarovka Loznice</strong> — hlavní + sunrise 6 kroků',
      '<strong>Led pasek postel</strong> — noční orientace',
      '<strong>Nest Hub Max</strong> — briefing',
      '<strong>Motion senzor</strong> — probuzení/WC',
      '<strong>📺 TV remote</strong> — Power, Vol, Play, Channel, D-pad, Home/Back, numpad 0-9 (native capabilities)',
      '<strong>💧 Zvlhčovač1</strong> — auto zap pod sh_cfg_humidity_low (default 30%), vyp nad sh_cfg_humidity_high (default 45%)'
    ],
    flow: 'Motion < 3:00 = WC. 3:00+ 2× do 3 min = wake. Alarm → sunrise. TV + Zvlhčovač manuálně v tiles.'
  },"""
    ),
    # Bathroom — přidat Giuseppe
    (
        """  bathroom: {
    title: '🚿 Koupelna',
    items: [
      '<strong>svetlo Koupelna</strong> — auto ON',
      '<strong>Speaker koupelna</strong> — rádio Italia 80',
      '<strong>2× PIR</strong>',
      '<strong>Teploměr</strong>'
    ],
    flow: 'Motion → světlo + radio. Cluster s toaletou.'
  },""",
        """  bathroom: {
    title: '🚿 Koupelna',
    items: [
      '<strong>svetlo Koupelna</strong> — auto ON',
      '<strong>Speaker koupelna</strong> — rádio Italia 80',
      '<strong>2× PIR</strong>',
      '<strong>Teploměr</strong>',
      '<strong>🤖 Giuseppe</strong> — robotický vysavač (start/stop + battery)'
    ],
    flow: 'Motion → světlo + radio. Cluster s toaletou. Giuseppe manuálně v tile.'
  },"""
    ),
    # Kitchen — přidat Lednice graf
    (
        """  kitchen: {
    title: '🍳 Kuchyně',
    items: [
      '<strong>Kuchyňská světla</strong> — auto ON při pohybu',
      '<strong>Reproduktor Kuchyn</strong> — TTS + rádio',
      '<strong>PIR + SNZB-06P</strong> — Kitchen AI',
      '<strong>Zasuvka Kaffe</strong> — ráno po 2 min'
    ],
    flow: 'Motion → Kitchen AI → světla + rádio. Ráno briefing + kávovar.'
  },""",
        """  kitchen: {
    title: '🍳 Kuchyně',
    items: [
      '<strong>Kuchyňská světla</strong> — auto ON při pohybu',
      '<strong>Reproduktor Kuchyn</strong> — TTS + rádio',
      '<strong>PIR + SNZB-06P</strong> — Kitchen AI',
      '<strong>Zasuvka Kaffe</strong> — ráno po 2 min',
      '<strong>🧊 Lednice</strong> — live power (W) + sparkline graf (120 vzorků, ~10 min historie)'
    ],
    flow: 'Motion → Kitchen AI → světla + rádio. Ráno briefing + kávovar. Lednice graf ve scrollu.'
  },"""
    ),
]


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP (not found): {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    orig = content
    changes = []
    is_crlf = '\r\n' in content[:4096]

    def do_replace(old, new, label):
        nonlocal content
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if old2 in content:
            content = content.replace(old2, new2, 1)
            changes.append('+ ' + label)
            return True
        return False

    # TTS
    for old, new, label in REPLACEMENTS:
        if not do_replace(old, new, label):
            changes.append('⏭ ' + label + ' (už applied)')

    # ZONE_HELP
    for old, new in ZONE_HELP_UPDATES:
        zone = old.split(':')[0].strip()
        label = 'ZONE_HELP ' + zone
        if not do_replace(old, new, label):
            changes.append('⏭ ' + label + ' (už applied)')

    if content != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
    else:
        print(f"  ⏭️  NO CHANGE (all already applied): {os.path.basename(fp)}")
    for c in changes:
        print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 5 — TTS diakritika + ZONE_HELP rozšíření')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
