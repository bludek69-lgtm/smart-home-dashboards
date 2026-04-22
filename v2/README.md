# 🎨 Dashboard v2 — Modern Redesign

Greenfield redesign inspirovaný user mockupem (2026-04-22).

**Status**: Phase 45 (design tokens + skeleton) · Work in progress

## 🎯 Goals

- **Left sidebar** místo bottom tabs
- **Glow accents** na ikonkách (barevné kruhy s box-shadow)
- **Stat tiles** row v headeru (6 boxes)
- **Gradient backgrounds** + rounded cards s blur
- **Responsive** (desktop / tablet / mobile)
- **Inter font** + system fallback
- **Data source**: stále `sh_dashboard_data` (bridge v1.9) → zero scripts/flows change

## 📁 Soubory

```
v2/
├── smart_home_modern_v2.html   # greenfield prototype
└── README.md                   # this
```

## 🗺 Roadmap

| Phase | Co | Stav |
|---|---|---|
| **45** | Design tokens + CSS theme + skeleton | ✅ done |
| **46** | Navigation routing (klik na sidebar item + URL hash) | ✅ done |
| **47** | Stat tiles + header chips wire (demo + API stub) | ✅ done |
| **48** | OSVĚTLENÍ — 6 rooms s dimmer sliders + interakcí | ✅ done |
| **49** | Rychlé scény (5) + Kamery grid (4 živé) | ✅ done |
| **50** | Audio zóny (play/vol controls) + Klima přehled (2 rooms) | ✅ done |
| **51** | Aktivity feed (5 events) + Základní ovládání (6 buttons) | ✅ done |
| **52** | Responsive polish — 4 breakpointy (1600/1400/1024/768) | ✅ done |
| **47b** | Real Homey API integration (bearer auth + config overlay + bridge transform) | ✅ done |

## 🎨 Design tokens (Phase 45)

### Colors
- **Backgrounds**: `#0a0f1c` → `#1a2236` (dark gradient)
- **Surface**: rgba s backdrop-blur
- **Accents**: green · blue · purple · orange · yellow · red · pink · cyan

### Typography
- **Font**: Inter → system-ui fallback
- **Sizes**: 11 / 13 / 15 / 17 / 20 / 28 / 36 px

### Layout
- Sidebar: 240px (collapses to 72px @ 1024px, hides @ 768px)
- Content max: 1600px
- Radii: 8/12/16/20 px

### Glows
- box-shadow 0 0 24px rgba(accent, 0.4) pro icon circles

## 🧪 Jak vyzkoušet

Otevři ve browseru:
```
file:///C:/HOMEY%20PRO%202026/dasboardy_CLAUDE/v2/smart_home_modern_v2.html
```

### Demo režim (default)
Dashboard běží se statickými demo daty — vidíš kompletní layout, všechny interakce fungují (dimmer slider, scene click, audio play, klima adjust). Badge v headeru: **DEMO**.

### Live režim
Klikni na **⚙ Config** v headeru → otevře overlay:
1. **Homey IP / Host** — např. `http://192.168.1.142`
2. **Bearer Token** — zkopíruj z v1 dashboardu (Config → Token input)
3. **Interval** — default 10 s
4. Klik **💾 Uložit** — test connection, pokud OK → dashboard přepne na LIVE

Token uložen v localStorage pod klíčem `sh_v2_cfg`. Badge změní na **LIVE** (zelené). Pokud fetch selže → **ERR** (červené) + fallback na demo.

### Mapování bridge → v2
- `state.rezim_doma` → Režim domu tile
- `state.spim/phase` → Přítomnost/Fáze tiles
- `health.score/power_total` → Systém/Spotřeba tiles
- `rooms.<zone>` → lights array (agregované light+strip+lampicka devices)
- `rooms.<zone>.speaker_playing` → audio zones
- `heating.zones` → klima cards (pokud bridge podporuje)
- Scenes/cameras/activities: zatím static (bridge v1.9 neexportuje)

## 🔄 Vztah k původním dashboardům

- **Původní 3** (smart_home_rpi/1920/2880.html) zůstávají funkční
- **v2** je greenfield, nic neruší
- Až bude v2 hotový + otestovaný → postupně nahradí původní
