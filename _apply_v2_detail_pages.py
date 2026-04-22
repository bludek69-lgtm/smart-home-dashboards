"""
Phase 53+ — v2 detail pages content (nahradí 9 placeholderů).
"""
path = r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\v2\smart_home_modern_v2.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

REPLACEMENTS = []

# ── OSVĚTLENÍ ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="osvetleni">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F4A1 Osvětlení</h1>
          <p>Ovládání světel ve všech místnostech · dimmer, teplota barvy, scény</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\U0001F4A1</div>
        <div class="placeholder-title">Osvětlení — detail</div>
        <div class="placeholder-sub">6 místností s dimmer slider + přepínač on/off.<br>Per-room controls (barva, teplota, efekty).</div>
        <div class="placeholder-phase">\u23F3 Phase 48</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="osvetleni">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F4A1 Osvětlení — všechny místnosti</h1>
          <p>Dimmer, on/off, scény</p>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head">
          <span class="section-title">RYCHLÉ AKCE</span>
        </div>
        <div class="ctrl-grid" style="grid-template-columns: repeat(4, 1fr);">
          <button class="ctrl-btn" onclick="allLights(\\'on\\')">
            <div class="ctrl-ico yellow">\U0001F4A1</div>
            <div class="ctrl-text"><div class="ctrl-title">Vše ON</div><div class="ctrl-sub">Plný jas</div></div>
          </button>
          <button class="ctrl-btn" onclick="allLights(\\'off\\')">
            <div class="ctrl-ico gray">\U0001F4A1</div>
            <div class="ctrl-text"><div class="ctrl-title">Vše OFF</div><div class="ctrl-sub">Zhasnout</div></div>
          </button>
          <button class="ctrl-btn" onclick="sceneRun(\\'comfort\\')">
            <div class="ctrl-ico orange">\u2600</div>
            <div class="ctrl-text"><div class="ctrl-title">Comfort</div><div class="ctrl-sub">Denní scéna</div></div>
          </button>
          <button class="ctrl-btn" onclick="sceneRun(\\'relax\\')">
            <div class="ctrl-ico purple">\U0001F319</div>
            <div class="ctrl-text"><div class="ctrl-title">Relax</div><div class="ctrl-sub">Tlumené</div></div>
          </button>
        </div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head">
          <span class="section-title">MÍSTNOSTI</span>
        </div>
        <div class="lights-grid" id="osvetleni-grid" style="grid-template-columns:repeat(auto-fill,minmax(280px,1fr));">
          <!-- rendered by JS -->
        </div>
      </div>
    </section>'''
))

# ── AUDIO ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="audio">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F50A Audio</h1>
          <p>Multi-room audio · Kuchyň (Spotify) · Ložnice · Koupelna · TTS pipeline</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\U0001F50A</div>
        <div class="placeholder-title">Audio — multi-room</div>
        <div class="placeholder-sub">Kontrola každé zóny zvlášť · play/pause/volume · queue · TTS priority</div>
        <div class="placeholder-phase">\u23F3 Phase 50</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="audio">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F50A Audio</h1>
          <p>Multi-room audio · play/pause · volume · TTS pipeline</p>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head"><span class="section-title">ZÓNY</span></div>
        <div class="audio-list" id="audio-list-full">
          <!-- rendered by JS -->
        </div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">RYCHLÉ AKCE</span></div>
        <div class="ctrl-grid" style="grid-template-columns: repeat(3, 1fr);">
          <button class="ctrl-btn" onclick="audioStop()">
            <div class="ctrl-ico red">\u23F9</div>
            <div class="ctrl-text"><div class="ctrl-title">Stop všude</div><div class="ctrl-sub">Všechny zóny</div></div>
          </button>
          <button class="ctrl-btn" onclick="toast(\\'\U0001F4FB Radio kuchyň\\')">
            <div class="ctrl-ico orange">\U0001F4FB</div>
            <div class="ctrl-text"><div class="ctrl-title">Radio kuchyň</div><div class="ctrl-sub">Classic Hits</div></div>
          </button>
          <button class="ctrl-btn" onclick="toast(\\'\U0001F5E3 TTS test\\')">
            <div class="ctrl-ico blue">\U0001F5E3</div>
            <div class="ctrl-text"><div class="ctrl-title">TTS test</div><div class="ctrl-sub">Hlas pipeline</div></div>
          </button>
        </div>
      </div>
    </section>'''
))

# ── KLIMA ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="klima">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F321 Klimatizace</h1>
          <p>Topení (Protherm 9kW + 3× TRV) · Čistička · Zvlhčovač · Ventilátor</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\U0001F321</div>
        <div class="placeholder-title">Heating + klima</div>
        <div class="placeholder-sub">Per-zone target · boost · AI vrstvy toggle · týdenní plán · kWh graf</div>
        <div class="placeholder-phase">\u23F3 Phase 50</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="klima">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F321 Klimatizace</h1>
          <p>Heating (Protherm 9 kW + TRV) · Čistička · Zvlhčovač</p>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head">
          <span class="section-title">TOPENÍ — ZÓNY</span>
          <span class="section-action" id="heating-master-status">mode: — · boiler: —</span>
        </div>
        <div id="klima-list-full" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;">
          <!-- rendered by JS -->
        </div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">PRESETY</span></div>
        <div class="ctrl-grid" style="grid-template-columns:repeat(4,1fr);">
          <button class="ctrl-btn" onclick="toast(\\'\U0001F3E0 Preset: Doma\\')"><div class="ctrl-ico green">\U0001F3E0</div><div class="ctrl-text"><div class="ctrl-title">Doma</div><div class="ctrl-sub">Standardní</div></div></button>
          <button class="ctrl-btn" onclick="toast(\\'\U0001F697 Preset: Pryč\\')"><div class="ctrl-ico orange">\U0001F697</div><div class="ctrl-text"><div class="ctrl-title">Pryč</div><div class="ctrl-sub">16 °C</div></div></button>
          <button class="ctrl-btn" onclick="toast(\\'\U0001F525 Preset: Boost\\')"><div class="ctrl-ico red">\U0001F525</div><div class="ctrl-text"><div class="ctrl-title">Boost</div><div class="ctrl-sub">+2 °C / 30 min</div></div></button>
          <button class="ctrl-btn" onclick="toast(\\'\u23F8 Heating OFF\\')"><div class="ctrl-ico gray">\u23F8</div><div class="ctrl-text"><div class="ctrl-title">Vše OFF</div><div class="ctrl-sub">Anti-freeze</div></div></button>
        </div>
      </div>
    </section>'''
))

# ── BEZPEČNOST ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="bezpecnost">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F6E1 Bezpečnost</h1>
          <p>Door/window sensors · Presence · Privacy guard · Režim pryč</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\U0001F6E1</div>
        <div class="placeholder-title">Security dashboard</div>
        <div class="placeholder-sub">Sensor status · history events · auto-lock rules</div>
        <div class="placeholder-phase">\u23F3 budoucí</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="bezpecnost">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F6E1 Bezpečnost</h1>
          <p>Senzory · Presence · Privacy guard · Režim pryč</p>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head"><span class="section-title">SENZORY</span></div>
        <div class="activity-list">
          <div class="activity-row"><div class="activity-ico green">\U0001F6AA</div><div class="activity-info"><div class="activity-title">Vchodové dveře</div><div class="activity-sub">Zavřeno</div></div><div class="activity-time">OK</div></div>
          <div class="activity-row"><div class="activity-ico green">\U0001FA9F</div><div class="activity-info"><div class="activity-title">Okno jídelna</div><div class="activity-sub">Zavřeno</div></div><div class="activity-time">OK</div></div>
          <div class="activity-row"><div class="activity-ico blue">\U0001F464</div><div class="activity-info"><div class="activity-title">Presence</div><div class="activity-sub" id="sec-presence-sub">Doma</div></div><div class="activity-time" id="sec-presence-time">aktivní</div></div>
          <div class="activity-row"><div class="activity-ico purple">\U0001F512</div><div class="activity-info"><div class="activity-title">Privacy guard</div><div class="activity-sub">Roleta nahoře → open space OFF</div></div><div class="activity-time">ON</div></div>
        </div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">REŽIM</span></div>
        <div class="ctrl-grid" style="grid-template-columns:repeat(3,1fr);">
          <button class="ctrl-btn" onclick="setMode(\\'home\\')"><div class="ctrl-ico green">\U0001F3E0</div><div class="ctrl-text"><div class="ctrl-title">Doma</div><div class="ctrl-sub">Aktivovat</div></div></button>
          <button class="ctrl-btn" onclick="setMode(\\'away\\')"><div class="ctrl-ico orange">\U0001F697</div><div class="ctrl-text"><div class="ctrl-title">Pryč</div><div class="ctrl-sub">Vše off + alerty</div></div></button>
          <button class="ctrl-btn" onclick="setMode(\\'sleep\\')"><div class="ctrl-ico purple">\U0001F319</div><div class="ctrl-text"><div class="ctrl-title">Spánek</div><div class="ctrl-sub">Tichý režim</div></div></button>
        </div>
      </div>
    </section>'''
))

# ── KAMERY ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="kamery">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F4F9 Kamery</h1>
          <p>Vchod · Zahrada · Garáž · Kuchyně · Ložnice indoor</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\U0001F4F9</div>
        <div class="placeholder-title">Camera grid</div>
        <div class="placeholder-sub">Live náhled všech kamer · motion snapshots archiv · timeline</div>
        <div class="placeholder-phase">\u23F3 Phase 49</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="kamery">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F4F9 Kamery</h1>
          <p>Živý náhled · motion snapshots</p>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head"><span class="section-title">ŽIVÉ KAMERY</span></div>
        <div id="cams-grid-full" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;">
          <!-- rendered by JS (velké tiles) -->
        </div>
      </div>
    </section>'''
))

# ── SCÉNY ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="sceny">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F3AC Scény</h1>
          <p>Večerní pohoda · Film · Dobré ráno · Noc · Odchod z domu · Vaření</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\U0001F3AC</div>
        <div class="placeholder-title">Scény editor</div>
        <div class="placeholder-sub">Quick-play všechny scény · create/edit/duplicate · schedule</div>
        <div class="placeholder-phase">\u23F3 Phase 49</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="sceny">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F3AC Scény</h1>
          <p>Rychlé aktivování atmosfér · světla, audio, klima v jednom kliku</p>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head">
          <span class="section-title">VŠECHNY SCÉNY</span>
          <span class="section-action" id="scene-active-lbl">Aktivní: —</span>
        </div>
        <div id="sceny-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;">
          <!-- rendered by JS -->
        </div>
      </div>
    </section>'''
))

# ── ENERGIE ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="energie">
      <div class="page-header">
        <div class="greeting">
          <h1>\u26A1 Energie</h1>
          <p>Spotřeba dnes · měsíc · TOP 10 spotřebičů · VT/NT · Kč/kWh</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\u26A1</div>
        <div class="placeholder-title">Energy dashboard</div>
        <div class="placeholder-sub">Graf spotřeby 24h · TOP 10 · VT/NT breakdown · měsíční projekce Kč</div>
        <div class="placeholder-phase">\u23F3 budoucí</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="energie">
      <div class="page-header">
        <div class="greeting">
          <h1>\u26A1 Energie</h1>
          <p>Spotřeba · kWh · VT/NT · heating odhad</p>
        </div>
      </div>
      <div class="stat-grid" style="grid-template-columns:repeat(4,1fr);">
        <div class="stat-tile"><div class="stat-label">AKTUÁLNĚ W</div><div class="stat-ico purple">\u26A1</div><div class="stat-value" id="en-now-val">—</div><div class="stat-sub">Live spotřeba</div></div>
        <div class="stat-tile"><div class="stat-label">DNES kWh</div><div class="stat-ico blue">\U0001F4C5</div><div class="stat-value" id="en-today-val">—</div><div class="stat-sub">Heating odhad</div></div>
        <div class="stat-tile"><div class="stat-label">VČERA kWh</div><div class="stat-ico orange">\U0001F4C6</div><div class="stat-value" id="en-yest-val">—</div><div class="stat-sub">Heating odhad</div></div>
        <div class="stat-tile"><div class="stat-label">DELTA vs VČERA</div><div class="stat-ico green">\U0001F4CA</div><div class="stat-value" id="en-delta-val">—</div><div class="stat-sub">Meziroční změna</div></div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">TARIF</span></div>
        <div class="activity-list">
          <div class="activity-row"><div class="activity-ico yellow">\u2600</div><div class="activity-info"><div class="activity-title">VT (vysoký tarif)</div><div class="activity-sub">5.48 Kč/kWh</div></div><div class="activity-time">D57d</div></div>
          <div class="activity-row"><div class="activity-ico blue">\U0001F319</div><div class="activity-info"><div class="activity-title">NT (nízký tarif)</div><div class="activity-sub">4.76 Kč/kWh</div></div><div class="activity-time">D57d</div></div>
          <div class="activity-row"><div class="activity-ico purple">\U0001F4CB</div><div class="activity-info"><div class="activity-title">Fixní poplatek</div><div class="activity-sub">735 Kč/měsíc · 3×25A</div></div><div class="activity-time">—</div></div>
        </div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">GRAF 24H</span></div>
        <div style="min-height:160px;display:grid;place-items:center;color:var(--tx-3);font-size:13px;border:1px dashed var(--border-med);border-radius:var(--r-md);padding:20px;">
          \U0001F4CA Graf power_snapshot history — coming soon (Phase 60+)
        </div>
      </div>
    </section>'''
))

# ── SYSTÉM ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="system">
      <div class="page-header">
        <div class="greeting">
          <h1>\u2699\uFE0F Systém</h1>
          <p>Health · AI vrstvy · Diagnostika · Logy · Config · Advanced</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\u2699\uFE0F</div>
        <div class="placeholder-title">System & AI</div>
        <div class="placeholder-sub">AI control center · diagnostické akce · manuální akce · log snapshots</div>
        <div class="placeholder-phase">\u23F3 budoucí (převzít z v1)</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="system">
      <div class="page-header">
        <div class="greeting">
          <h1>\u2699\uFE0F Systém</h1>
          <p>Health · AI vrstvy · Diagnostika · Odkaz na v1 pro detailní akce</p>
        </div>
      </div>
      <div class="stat-grid" style="grid-template-columns:repeat(4,1fr);">
        <div class="stat-tile"><div class="stat-label">HEALTH SCORE</div><div class="stat-ico green">\U0001F6E1</div><div class="stat-value" id="sys-health-val">—</div><div class="stat-sub">System zdraví</div></div>
        <div class="stat-tile"><div class="stat-label">DEMAND ZÓNY</div><div class="stat-ico orange">\U0001F525</div><div class="stat-value" id="sys-demand-val">—</div><div class="stat-sub">Heating</div></div>
        <div class="stat-tile"><div class="stat-label">OFFLINE DEVICES</div><div class="stat-ico blue">\U0001F4E1</div><div class="stat-value" id="sys-offline-val">—</div><div class="stat-sub">Nedostupné</div></div>
        <div class="stat-tile"><div class="stat-label">CELKEM DEVICES</div><div class="stat-ico purple">\U0001F522</div><div class="stat-value" id="sys-total-val">—</div><div class="stat-sub">V Homey</div></div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">RYCHLÉ AKCE</span></div>
        <div class="ctrl-grid" style="grid-template-columns:repeat(3,1fr);">
          <button class="ctrl-btn" onclick="toast(\\'\U0001F3E5 Health check triggered\\')"><div class="ctrl-ico green">\U0001F3E5</div><div class="ctrl-text"><div class="ctrl-title">Health check</div><div class="ctrl-sub">sh_system_health_v1</div></div></button>
          <button class="ctrl-btn" onclick="toast(\\'\U0001F504 Self-heal triggered\\')"><div class="ctrl-ico blue">\U0001F504</div><div class="ctrl-text"><div class="ctrl-title">Self-heal</div><div class="ctrl-sub">Fix orphans</div></div></button>
          <button class="ctrl-btn" onclick="toast(\\'\U0001F9E0 Meta Brain triggered\\')"><div class="ctrl-ico purple">\U0001F9E0</div><div class="ctrl-text"><div class="ctrl-title">Meta Brain</div><div class="ctrl-sub">Full scan</div></div></button>
        </div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">DETAILNÍ OVLÁDÁNÍ</span></div>
        <p style="color:var(--tx-3);font-size:13px;margin-bottom:12px;">Pro plnou AI kontrolu (PŘEPISY, DIAGNOSTICKÉ AKCE, MANUÁLNÍ AKCE, LOG SNAPSHOTS, GEMINI DIAGNOSTIKA) použij v1 dashboard:</p>
        <a href="../smart_home_1920x1080.html" class="cam-btn-all" style="text-decoration:none;">\u2192 Otevřít v1 AI page</a>
      </div>
    </section>'''
))

# ── HISTORIE ──
REPLACEMENTS.append((
    '''    <section class="page" data-page="historie">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F550 Historie</h1>
          <p>Event log · Morning routine history · Daily reports · AI rozhodnutí</p>
        </div>
      </div>
      <div class="page-placeholder">
        <div class="placeholder-ico">\U0001F550</div>
        <div class="placeholder-title">Activity history</div>
        <div class="placeholder-sub">Filterable event log · timeline · export · search</div>
        <div class="placeholder-phase">\u23F3 budoucí</div>
      </div>
    </section>''',
    '''    <section class="page" data-page="historie">
      <div class="page-header">
        <div class="greeting">
          <h1>\U0001F550 Historie</h1>
          <p>Poslední události · zdroje dat</p>
        </div>
      </div>
      <div class="section-card">
        <div class="section-head"><span class="section-title">POSLEDNÍ UDÁLOSTI</span></div>
        <div class="activity-list" id="historie-list">
          <!-- rendered by JS -->
        </div>
      </div>
      <div class="section-card" style="margin-top:16px;">
        <div class="section-head"><span class="section-title">ZDROJE DAT</span></div>
        <div class="activity-list">
          <div class="activity-row"><div class="activity-ico green">\U0001F4CA</div><div class="activity-info"><div class="activity-title">Google Sheets EventLog</div><div class="activity-sub">10k řádků · filter by script/event/hours</div></div><div class="activity-time">web</div></div>
          <div class="activity-row"><div class="activity-ico blue">\U0001F305</div><div class="activity-info"><div class="activity-title">Ranní rutina</div><div class="activity-sub">Morning timeline · 3:15 / 5:15 alarm</div></div><div class="activity-time">daily</div></div>
          <div class="activity-row"><div class="activity-ico orange">\U0001F50B</div><div class="activity-info"><div class="activity-title">Battery History</div><div class="activity-sub">30-denní trend per zařízení</div></div><div class="activity-time">daily</div></div>
          <div class="activity-row"><div class="activity-ico purple">\U0001F9E0</div><div class="activity-info"><div class="activity-title">Daily Report</div><div class="activity-sub">Gemini AI souhrn dne</div></div><div class="activity-time">22:00</div></div>
        </div>
      </div>
    </section>'''
))

# Apply replacements — unescape \' back to literal '
count = 0
for old, new in REPLACEMENTS:
    old_u = old.replace("\\'", "'")
    new_u = new.replace("\\'", "'")
    if old_u in text:
        text = text.replace(old_u, new_u, 1)
        count += 1

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print(f'Applied {count}/{len(REPLACEMENTS)} replacements')
print(f'Lines: {text.count(chr(10))+1}')
b_open = text.count('{'); b_close = text.count('}')
print(f'braces: {b_open} / {b_close}  diff {b_open-b_close}')
