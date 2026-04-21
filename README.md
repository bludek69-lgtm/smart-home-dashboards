# 📊 Smart Home Dashboards

3 HTML dashboardy pro [Smart Home Homey Pro 2026 projekt](../../Claude_code_SMART_HOME/).

## 📁 Soubory

- **smart_home_1920x1080.html** · Desktop 1080p
- **smart_home_2880x1800.html** · Desktop 4K / MacBook Pro
- **smart_home_rpi.html** · Raspberry Pi touchscreen (7" / 10")

Všechny 3 soubory sdílejí strukturu (13 stránek, stejný JS, ~200 kB každý).

## 🎨 Stránky (13)

home · zones · topení · plán · audio · ai · logy · počasí · kamera · config · advanced · finance · burza

## 🛠 Vývoj — Phase skripty

Každá změna dashboardu = idempotentní Python phase skript s markerem:

```
_apply_phaseNN_popis.py
```

Skripty:
- Aplikují regex search/replace na všechny 3 HTML
- Přidají `<!-- PHASE_NN_MARKER -->` před `</body>` (idempotence)
- Lze spustit vícekrát bez duplikace

### Aktuální stav: Phase 44 deployed

| Phase | Co |
|---|---|
| 16-18 | TOPENÍ page + heating2 editor |
| 19-21 | Roleta hystereze + popisky |
| 22-23 | Missing helpy + tooltips |
| 25 | Roleta unified text (20k-25k lux) |
| 26 | AI toggle (Fáze C opt-in) |
| 27 | Yesterday heating runtime tile |
| 28 | Heating KONFIGURACE sekce (9 inputů) |
| 29 | Mass tooltips (+56 title attrs) |
| 30 | Zone indicators (fixed via bridge v1.8) |
| 31 | Finance TOP 5 → 10 |
| 32 | Washer plug home page |
| 33 | Washer tile zone detail |
| 34 | Pradelna merge washer |
| 35 | Washer icon 🧺 → 🫧 |
| 36 | Shade range 20k-50k lux |
| 37 | Roleta simulator range fix |
| 38 | AI page tooltips + MANUÁLNÍ AKCE help |
| 39 | TOPENÍ page compact (collapse KONFIGURACE + PROGRAM) |
| 40 | LOG SNAPSHOTS tile descriptions |
| 41 | PŘEPISY compact |
| 42 | LOG SNAPSHOTS g4 → g2 |
| 43 | LOG SNAPSHOTS full-width |
| 44 | AI page allow vertical scroll |

## 🔌 Data source

Dashboardy fetchují `sh_dashboard_data` přes Homey Web API (každých 10s). Proměnná je build by [sh_dashboard_bridge_v1](../../Claude_code_SMART_HOME/21_4/opravene_scripty/sh_dashboard_bridge_v1_v1.9.js) (1 min cron).

## 📦 Rollback

```bash
git log --oneline
git revert HEAD           # vrátí poslední phase
# nebo
git checkout <commit>     # vrátí se na konkrétní stav
```
