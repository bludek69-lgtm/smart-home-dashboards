# Visual Reference Pack — Persistent Context
**Provided by user**: 2026-04-25 noc
**Status**: 🎯 **STYLE ANCHORS — use during every iteration of Phase 3, 4**

> ⚠ Tyto reference jsou design language inspirace, **NE** přesné kopie.
> Při každém CSS commit / screenshot / critique → porovnat výsledek s referencí.

---

## Reference Image #1 — Overview / Home (PRIMARY ANCHOR)

**Title**: "Dobrý večer, Luděk 👋"
**Subtitle**: "Vše je v pořádku. Dům je v režimu Domov."

### Klíčové prvky
- **Sidebar nav** (220px wide): Přehled (active green) / Osvětlení / Audio / Klimatizace / Bezpečnost / Kamery / Scény / Energie / Systém / Historie. User profile bottom + system health card "100%".
- **Top header**: greeting (large) + clock 21:42 + temp 16.8°C polojasno + "Režim Domov" dropdown
- **6 status tiles** horizontal row:
  - REŽIM DOMU (green house icon, "Domov", "Aktivní od 18:30")
  - PŘÍTOMNOST (people icon green, "Doma", "2 osoby")
  - DENNÍ FÁZE (sun amber icon, "Večer", "21:00 – 22:00")
  - VENKOVNÍ TEPLOTA (thermometer blue, "16.8 °C", "Polojasno")
  - SPOTŘEBA DNES (lightning purple, "12.4 kWh", "↓ 8% vs včera")
  - SYSTÉM (shield green, "Vše v pořádku", "Online")
- **3-col grid below**:
  - Left: "OSVĚTLENÍ – MÍSTNOSTI" with 6 cards (Kuchyně+Jídelna ON 65% / Obývací pokoj ON 40% / Ložnice 1 OFF 0% / Ložnice 2 ON 35% / Koupelna OFF 0% / Chodba ON 20%) — slider per card
  - Center: "Rychlé scény" 5 cards (Večerní pohoda / Film / Dobré ráno / Noc / Odchod z domu) — icon + ▶ button
  - Right: "KAMERY – ŽIVÝ NÁHLED" (4 cams: Vchod / Zahrada / Garáž / Kuchyně) + "Otevřít všechny kamery" button
- **Bottom row** (4 panels):
  - Audio – Zóny: Kuchyně Spotify 45% playing / Ložnice 2 Pozastaveno
  - Klima – Přehled: 22.0°C aktuálně 21.8 / 21.5°C aktuálně 21.3 + fan controls
  - Aktivity – Poslední události: timeline (Večerní pohoda 21:30 / Kuchyně světla změna jasu na 65% 21:28 / TTS oznámení Kuchyně 21:15 / Odchod z domu 17:45 / Dobré ráno 07:15)
  - Základní ovládání: 6 quick buttons (Všechny světla ON/OFF / Audio stop / Žaluzie / Teplota ECO / Režim pryč)
- **Bottom status row**: "Poslední synchronizace: 21:41:58" + "Homey Pro 2026 | Verze 1.2.6" + "Všechny systémy online"

### Aesthetic notes
- Gradient backgrounds on hero tiles (subtle)
- Green glow on active status icons
- Rounded ~14px corners
- Generous spacing (16-24px gaps)
- Type hierarchy clear

---

## Reference Image #2 — Multi-section Overview + Device variants

**Title**: "PŘEHLED DOMU"

### Distinctive elements
- **Top status pills** (5): HOME MODE / SECURITY DISARMED / ALARM OK / AI STATUS ACTIVE / WEATHER 12°C
- **7 mode buttons** strip: DOMA (active green) / VENKU / SPÁT / KINO / RELAX / VAŘENÍ / NÁVŠTĚVA
- **Health gauge** SVG: 94/100 VÝBORNÉ + 4 metrics (Sítě 100% / Zařízení 96% / Skripty 93% / Výkon 90%)
- **Alerts feed**: timestamps + colored bullets (info/warn/ok)
- **Lighting cards** with TOGGLE switches (not just sliders): Obývák / Kuchyň / Ložnice / Koupelna / Chodba — bulb icon glows yellow when on
- **Audio "Now playing"**: large album art (Daft Punk Get Lucky), progress bar, play controls
- **Energy panel**: 4 metrics + multi-line chart (00:00–24:00) with peak highlight
- **AI predictions**: 3 recommendation cards (Predikce úspory / Komfort / Bezpečnost)
- **Bottom section** showcases 3 device variants:
  - **Tablet/Touch panel 1024×600**: simplified layout, larger touch targets, side icons
  - **Mobile**: stacked cards, bottom nav (4 tabs)
  - **Desktop**: full layout

### Anchor uses
- Take TILE TOGGLE pattern (not just sliders) for lighting cards
- Use HEALTH GAUGE design for system health page
- Mode pill row pattern for top of home

---

## Reference Image #3 — Energy Cockpit / Diagnostics / Scenes / Analytics

**4 sub-sections shown:**

### A) ENERGY COCKPIT (top-left)
- Title: "ENERGY COCKPIT" + "Přehled spotřeby a výroby v reálném čase"
- 4 hero tiles: AKTUÁLNÍ SPOTŘEBA 2.45 kW / VÝROBA SOLÁR 4.32 kW / BATERIE 78% / AUTOPILOT AKTIVNÍ
- **Sankey flow diagram**: Solární panely 4.32 kW → 7.47 kW CELKEM → Dům 5.12 kW / Baterie 1.25 kW / Přebytky 1.10 kW
- **Daily balance** bar chart 24 stunden colored
- **Tarify** panel: aktuální 2.35 Kč/kWh nízký, do změny 01:14
- **Predikce zítra** chart: spotřeba 98 / výroba 110 / úspora 12.5 kWh
- **TOP spotřebiče dnes**: Tepelné čerpadlo 24.1 kWh (25%) / Ohřev vody 18.7 kWh (19%) / ...

### B) DIAGNOSTICS — MISSION CONTROL (top-right)
- Title: "DIAGNOSTICS · MISSION CONTROL" + "Stav systému, zařízení a automatizací"
- 5 hero tiles: HEALTH SCORE 94/100 / ZAŘÍZENÍ 74 (Online 71, Offline 3) / AUTOMATIZACE 156 (Aktivní 149) / SCRIPTS 80 (Běžící 4) / UPTIME 15 dní 99.7%
- **OFFLINE ZAŘÍZENÍ list** (3 items): Light Sensor Okno Jídelna 0% baterie / SNZB-06P Koupelna žluté oznámení / Zigbee Bridge Ložnice nedostupný
- **ROUTER LATENCY**: 4 entries with color-coded latency bars (12ms / 8ms / 15ms / 11ms)
- **CHYBY A VAROVÁNÍ**: 3 entries (sh_jidelna_roleta_router_v2 / sh_audio_router_v1 / sh_cube_controller_v1)
- **SELF-HEALING SYSTEM**: Aktivní + 4 metrics (Samoopravy 7 / Zablokované konflikty 23 / Restarty 2 / Zabránené chyby 15)
- **EVENT BUS** chart (60s): 156 events, 2.6/min average
- **HEARTBEAT**: All systems OK, 4 mini ECG-like waveforms
- Bottom row: Last backup / Google Sheets connected / Homey Backup auto / System version 12.1.0

### C) SCENES ORCHESTRATOR (bottom-left)
- Rich scene cards with **photo backgrounds**: Romantická večeře (Open Space) / Večerní relax (Obývák) / Dobré ráno (Celý dům) / Práce z domu (Pracovna) / Odchod z domu (Celý dům) / Noční režim (Ložnice)
- Each card has icon overlay + ▶ button + name + zone label
- **Aktivní scéna sidebar**: Večerní relax (started 22:14) + breakdown (Osvětlení 7 zařízení / Audio 2 zóny / Topení 3 zóny / Rolety 5 zařízení / AI Asistent 7 zón) + "Upravit scénu" button + "Zastavit scénu" red CTA
- **HISTORIE (DNES)** feed: 22:14 Večerní relax / 20:35 Dobré ráno / 18:42 Odchod z domu / 07:15 Noční režim
- Bottom: Spuštění scény 4 trigger types (Manuálně / Plán / Událost / AI Doporučení)

### D) HISTORY & ANALYTICS (bottom-right)
- Title: "HISTORIE & ANALYTICS" + "Trendy, statistiky a analýzy systému"
- Time range pills: Dnes / 7 dní / 30 dní (active) / 90 dní
- 4 hero stat cards: Celková spotřeba 96.7 kWh / Průměrná teplota 21.4°C / AI Predikce úspora 12.5 kWh / Automatizace 1,247 (each with mini sparkline + delta)
- **SPOTŘEBA PODLE ZÓN** donut: Open Space 30% / Kuchyně 19% / Ložnice 13% / Koupelna 9% / Technická 16% / Ostatní 13%
- **UDÁLOSTI V ČASE** scatter plot: dots colored by category (Osvětlení / Topení / Audio / Bezpečnost / AI), 00:00-24:00
- **NEJAKTIVNĚJŠÍ ZAŘÍZENÍ** ranked list: Tepelné čerpadlo 247 / Philips Hue Hub 198 / Sonos Beam 156 / Zigbee Bridge 134 / Homey Pro 126
- **AI INSIGHTS**: 3-card row with mini icons + insight text + "Více insights →"

---

## Reference Image #4 — Multi-page composite (Lighting / Heating / Cameras / AI / Settings + mobile)

### A) Overview (top-left)
- Sidebar + greeting "SEMILY"
- "PŘEHLED DOMU" + status pills row + health 94 gauge + alerts feed
- 6 mode buttons (DOMA active / VENKU / NOC / RELAX / KINO / NÁVŠTĚVA)
- Lighting hlavní místnosti (5 cards: Obývák/Kuchyně/Ložnice/Koupelna/Chodna with toggle + dim%)
- Klima current state cards
- Footer: Homey Pro 2026 ONLINE

### B) Lighting page (top-right)
- Title: "OSVĚTLENÍ" + sub-tabs: MÍSTNOSTI (active) / SKUPINY / SCÉNY / AUTOMATIZACE
- **Místnosti grid**: 5 large cards with toggle switches (Obývák 100% / Kuchyně 80% / Ložnice 20% / Koupelna 30% / Jídelna 50%) — sliders below
- **Rychlé scény** right column: Jasno / Večer / Noc / Relax / Kino / Úklid
- **Skupiny**: Přízemí 6 svetel ON / 1. Patro 8 ON / Venkovní 4 ON

### C) Audio page (middle-left)
- Title: "AUDIO" + sub-tabs: PŘEHRÁVÁNÍ (active) / ZÓNY / OBLÍBENÉ / NASTAVENÍ
- "NYNÍ HRAJE - OBÝVÁK" with album art + Daft Punk Get Lucky + 1:23/4:07 + controls
- **ZÓNY** right column: Obývák 66% / Kuchyně 30% (Chill Playlist) / Ložnice 2 30% (Sleep Music) / Koupelna 20% (Radio Relax) — each with volume slider + speaker icon
- **RYCHLÉ OVLÁDÁNÍ**: Pozastavit vše / Ztlumit vše / Oblíbené / Přehrát na vše

### D) Heating page (middle-center)
- Title: "TOPENÍ" + sub-tabs: PŘEHLED / MÍSTNOSTI / PROGRAM / NASTAVENÍ
- "AKTUÁLNÍ STAV" 6 room cards: Obývák 22.5°C target 21.0 AUTO / Ložnice 20.0°C / Dětský pokoj 21.5°C / Kuchyně 21.0°C / Koupelna 23.0°C / Chodba 19.0°C
- **PROGRAM TOPENÍ** sidebar: Komfort 17:00-21:00 21.0°C / Útlum 22:00-05:00 18.0°C / Dovolena Neaktivní + "Upravit program" button
- **SPOTŘEBA TOPENÍ** chart: Dnes 18.7 / Týden 112.3 + bars per day

### E) Cameras (bottom-left)
- Title: "KAMERY" + sub-tabs: NÁHLED / NAHRÁVKY / NASTAVENÍ + "4 ONLINE"
- 4 cameras grid with green online dots: Přední vstup / Zahrada / Garáž / Obývák
- Bottom: Všechny záznamy / Detekce pohybu ON / Noční režim AUTO

### F) AI Asistent (middle-right)
- Title: "AI ASISTENT" + sub-tabs: PŘEHLED / PREDIKCE / AUTOMATIZACE / DENÍK
- AI STATUS large brain icon "ACTIVE" with "Systém v pořádku"
- **DOPORUČENÍ**: 3 entries (Optimalizace topení / Úspora energie / Komfortní zóna) with "Použít" buttons
- **PREDIKCE** stats: Počasí zítra 14°C/6°C / Spotřeba 21.5 kWh +5% / Solární výroba 8.2 kWh +30% / Vytápění 18.3 kWh -12%
- **UDÁLOSTI** timeline: Optimalizace topení / Predikce úspory aktualizace / Scéna Večer aktivována / Upozornění na vysokou spotřebu

### G) Settings (bottom-center)
- Title: "NASTAVENÍ" + sub-tabs: SYSTÉM / ZAŘÍZENÍ / AUTOMATIZACE / UŽIVATELE / ZÁLOHY
- **SYSTÉMOVÉ NASTAVENÍ**: form rows (Název systému / Lokalita / Časové pásmo / Jazyk / Jednotky teploty / Motiv / Automatické aktualizace toggle)
- **INFORMACE O SYSTÉMU**: Verze 3.2.1 / Homey Pro 2026 / Paměť 42% / CPU 18% / Úložiště 67% + "Zálohovat systém" CTA

### H) Mobile zobrazení (bottom-right)
- 4 phone mockups showing: Přehled (94 score) / Osvětlení / Audio / AI Asistent
- Bottom tab nav (4 icons)
- Stacked cards optimized for narrow viewport

---

## Reference Image #5 — AI Brain + Governance Console (PREMIUM ENTERPRISE)

### A) AI BRAIN / INTENT CENTER (top)
- Title: "AI BRAIN / INTENT CENTER" + "Context awareness · Predictions · Natural language · Decisions"
- Top status pills: AI Engine ONLINE / Context ACTIVE / Confidence 92%
- Sub-tabs: INTENT (active) / PREDICTIONS / RECOMMENDATIONS / CONVERSATIONS / LEARNING
- **CURRENT INTENT** card: "Evening Relax" + Confidence 92% + "Detekováno: 23:45" + "Zdroj: Chování domácnosti + čas + přítomnost" + Priority Engine HOUSE MODE / State ACTIVE
- **CONTEXT SNAPSHOT** with brain visualization: animated brain icon center, 7 connected nodes around (Přítomnost / Fáze dne / Lux Kitchen / Teplota Indoor / Hluk Living / Režim domu / Aktivita)
- **TOP PREDICTIONS** list: 5 predictions with confidence bars (Přehrát relax hudbu 95% / Ztlumit světla 87% / Stáhnout rolety 76% / Zvýšit teplotu 62% / Spustit čističku 48%) + "Zobrazit všechny predikce →"
- **AI RECOMMENDATIONS** sidebar: 4 cards (Optimální osvětlení / Teplota komfort / Kvalita vzduchu / Hudební scéna) each with "Použít" button
- **QUICK ACTIONS** row: 6 mode buttons (Relax Mode / Good Night / Good Morning / Focus Mode / Away Mode / Dinner Time)
- **NATURAL LANGUAGE** input: voice waveform + text field + send arrow + 4 quick command pills (Ztlumit světla / Pusť relax hudbu / Tepleji / Dobrou noc)
- **LEARNING & ADAPTATION**: stats (Naučené vzorce 128 / Úspěšnost predikcí 91% / Zpětná vazba 3) + 30-day chart
- **AI HEALTH**: Model Status OK / Response Time 420ms / API Quota 68% / Memory Usage 54% + "Všechny systémy běží normálně" green status

### B) GOVERNANCE / CONFIG CONSOLE (bottom)
- Title: "GOVERNANCE / CONFIG CONSOLE" + "System configuration · Rules · Priorities · Backups · Access"
- Top status: System Health 94/100 / Config Version v6.2.1 / Last Backup 10.04.2026 02:14
- Sub-tabs: SYSTEM (active) / PRIORITIES / OVERRIDES / AUTOMATIONS / INTEGRATIONS / BACKUP & RESTORE / ACCESS CONTROL / LOGS
- **SYSTEM OVERVIEW**: Homey Pro 2026 v12.3.0 / Uptime 15 dní 4h / RAM 42% / CPU 18% / Storage 67% / Active Flows 155 / Active Scripts 80 / Devices 74 / Variables 210
- **PRIORITY ENGINE** with hierarchical numbered list: 1 SAFETY Aktivní / 2 MANUAL OVERRIDE Aktivní / 3 HOUSE MODE evening / 4 ROOM EVENT idle + "Aktuální rozhodnutí: HOUSE MODE" + "Upravit pravidla priority" CTA
- **OVERRIDES** list: Osvětlení Open Space ruční jas 75% / Audio Kitchen hlasitost 55% / Climate Bedroom teplota 22.5°C / Roleta Jídelna pozice 40% + "Zobrazit všechny přepisy →"
- **AUTOMATION RULES**: 7 toggleable rules (Morning Routine / Night Routine / Energy Save / Air Quality Boost / Security Alert / Při poplachu) + "Správa automatizací →"
- **INTEGRATIONS**: 5 service rows with chevron expand (Google Sheets / Gemini AI / Weather API / TTS Service / Spotify) — all "Připojeno"
- **CONFIG PROFILES**: 4 profile types (Light Profiles 23 / Audio Profiles 12 / Climate Profiles 8 / Scene Profiles 15) + "Správa profilů"
- **BACKUP & RESTORE**: Last backup info + Auto Zapnuto + Storage Google Drive + Size 128 MB + "Vytvořit zálohu" + "Obnovit ze zálohy"
- **ACCESS CONTROL**: 3 user rows with role icons (Luděk Owner Plný přístup / Klára Standardní / Guest Pouze zobrazení) + "Správa uživatelů"
- **SYSTEM LOGS**: timeline of events (AI Intent detected / Lights Open Space / Energy Autopilot / Backup completed / Camera motion detected) + "Zobrazit všechny logy"
- **SYSTEM ACTIONS** sidebar: 5 maintenance buttons (Restart systému / Vyčistit cache / Kontrola integrity / Optimalizace databáze) + RED "Nouzový režim" CTA

### Aesthetic notes specific to image 5
- Cards have subtle vertical dividers in feeds
- Icons have brand-color tinting (not pure white)
- Hierarchical lists use number badges (1, 2, 3, 4) with status colors
- Toggle switches throughout (very iOS/macOS settings vibe)

---

## 🎯 How to use these references

### During Phase 2C (design system refinement)
- Cross-reference DESIGN_SYSTEM.md tokens against these images
- Refine color palette to exactly match what we observe

### During Phase 3 (CSS patch)
- Open this file alongside CSS work
- For each page redesign, check "Anchor uses" / "Mapping references" section
- Match: spacing, hierarchy, glass effects, typography

### During Phase 4 (QA loop)
- Take screenshot at each iteration
- Side-by-side mental compare with reference
- Question: "Does this look like vendor-grade or hobby?"
- If hobby → identify specific element, fix CSS, retake

### During Phase 5 (docs)
- Cite which reference image inspired each pattern
- Include before/after pairs in handbook

---

## ⛔ Anti-copy reminder

User's directive: "Nejsou to nové dashboardy, které máš kopírovat 1:1."

- **OUR features stay** (TV remote, validator, roleta sim, V4 sub-tabs, etc.)
- **OUR Homey integration stays** (runScript, writeVar, setDeviceCap)
- **THEIR visual language adapts**: spacing, colors, hierarchy, glass, motion
