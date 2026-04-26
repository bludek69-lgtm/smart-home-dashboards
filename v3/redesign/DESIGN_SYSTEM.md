# Design System — Premium Smart Home Dashboard
**Source**: User-provided reference images (2026-04-25)
**Target quality**: Vendor-grade (Loxone/Homey Pro/HA Premium)
**Aesthetic**: Premium dark control panel + glass cards + mission control feeling

> ⚠ Reference images = **STYLE ANCHORS**, NEnárrhy přesných stránek. Inspirace pro vizuální jazyk, ne pro kopírování 1:1.

---

## 🎨 Visual Language Summary

5 reference images observed (Phase 0 visual context):

| # | Theme | Klíčové prvky |
|---|---|---|
| 1 | **Overview / Home** ("Dobrý večer, Luděk") | Sidebar nav, header greeting, 6 status tiles, 3-col grid (Lighting + Quick scenes + Cameras), bottom row (Audio, Klima, Activities, Basic controls) |
| 2 | **Multi-section overview + device variants** | Status pills header (HOME MODE/SECURITY/ALARM/AI STATUS/WEATHER), 7 mode buttons, system health gauge 94/100, alerts feed, lights + climate + cameras + audio + energy + AI predictions, Tablet/Mobile/Desktop variants |
| 3 | **Energy / Diagnostics / Scenes / Analytics** | Sankey energy flow, daily balance, tariffs, mission control diagnostics, scenes orchestrator with rich card images, multi-line analytics charts |
| 4 | **Multi-page composite** | Overview health card, Lighting (rooms+scenes+groups), Audio player+zones, Heating per-room+weekly program, Cameras grid, AI Assistant, Settings, Mobile |
| 5 | **AI Brain + Governance Console** | Intent Center (current intent 92% confidence, context snapshot brain visual, predictions, recommendations, quick actions, natural language, learning stats, AI health), Governance Config (system overview, priority engine, overrides, automations, integrations, profiles, backup, access, logs) |

---

## 🌑 Color Tokens

```css
/* === BASE === */
--bg-base:           #050810;  /* deepest background */
--bg-surface:        #0d1424;  /* main canvas */
--bg-card:           #141d33;  /* card / tile background */
--bg-card-hover:     #1a253f;  /* hover state */
--bg-elevated:       #1f2942;  /* elevated/selected */

/* === BORDERS === */
--border-subtle:     rgba(255,255,255,0.05);
--border-default:    rgba(255,255,255,0.08);
--border-strong:     rgba(255,255,255,0.12);
--border-active:     rgba(74,222,128,0.4);  /* green active */

/* === TEXT === */
--text-primary:      #e8edf5;  /* primary text */
--text-secondary:    #9ba8bd;  /* secondary labels */
--text-tertiary:     #5e6e85;  /* hints, captions */
--text-disabled:     #3a4458;

/* === ACCENTS (status semantics) === */
--accent-green:      #4ade80;  /* OK / active / online */
--accent-green-glow: rgba(74,222,128,0.3);
--accent-amber:      #fbbf24;  /* warning / lights ON */
--accent-amber-glow: rgba(251,191,36,0.3);
--accent-red:        #f87171;  /* critical / error / off */
--accent-red-glow:   rgba(248,113,113,0.3);
--accent-blue:       #60a5fa;  /* info / cool / climate */
--accent-blue-glow:  rgba(96,165,250,0.3);
--accent-purple:     #a78bfa;  /* AI / scene / special */
--accent-purple-glow:rgba(167,139,250,0.3);
--accent-cyan:       #22d3ee;  /* SEMILY brand / hi-tech */
--accent-pink:       #f472b6;  /* AI suggestion accent */

/* === SCENE-SPECIFIC === */
--scene-relax:       #a78bfa;
--scene-work:        #60a5fa;
--scene-audio:       #4ade80;
--scene-cinema:      #f87171;
--scene-cooking:     #fb923c;
--scene-romantic:    #f472b6;
```

---

## 📐 Spacing Scale

```css
--space-1:  4px;
--space-2:  8px;
--space-3:  12px;
--space-4:  16px;
--space-5:  20px;
--space-6:  24px;
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

**Card padding**: `--space-5` (20px) standard, `--space-6` (24px) hero.
**Card gap**: `--space-4` (16px) standard, `--space-3` (12px) dense.

---

## 🔲 Border Radius

```css
--radius-sm:  6px;   /* badges, pills */
--radius-md:  10px;  /* buttons, inputs */
--radius-lg:  14px;  /* cards, tiles */
--radius-xl:  18px;  /* hero panels */
--radius-full: 9999px; /* pills, avatars */
```

References: cards have **14px** consistent radius. Hero/featured panels go up to 18px.

---

## ✨ Glass / Depth Effects

```css
/* Standard card */
.card {
  background: linear-gradient(180deg,
    rgba(255,255,255,0.02) 0%,
    rgba(255,255,255,0) 100%),
    var(--bg-card);
  border: 1px solid var(--border-default);
  box-shadow:
    0 1px 0 rgba(255,255,255,0.03) inset,  /* top sheen */
    0 4px 20px rgba(0,0,0,0.3);
  backdrop-filter: blur(8px);  /* if behind translucent */
}

/* Active / highlighted card */
.card.active {
  border-color: var(--accent-green);
  box-shadow:
    0 0 0 1px var(--accent-green-glow),
    0 0 20px var(--accent-green-glow),
    0 4px 20px rgba(0,0,0,0.3);
}

/* Glow tint per accent */
.glow-green  { box-shadow: 0 0 30px var(--accent-green-glow); }
.glow-amber  { box-shadow: 0 0 30px var(--accent-amber-glow); }
.glow-red    { box-shadow: 0 0 30px var(--accent-red-glow); }
.glow-blue   { box-shadow: 0 0 30px var(--accent-blue-glow); }
.glow-purple { box-shadow: 0 0 30px var(--accent-purple-glow); }
```

---

## 🔤 Typography

```css
/* Stack — system + Inter fallback */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont,
             'Segoe UI', Roboto, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Scale */
--text-xs:    11px;  /* captions, badges */
--text-sm:    13px;  /* labels, metadata */
--text-base:  15px;  /* body */
--text-lg:    17px;  /* card titles */
--text-xl:    20px;  /* section headings */
--text-2xl:   24px;  /* page headings */
--text-3xl:   32px;  /* hero values (e.g., temp 22.5°C) */
--text-4xl:   42px;  /* mega values (e.g., kWh totals) */
--text-5xl:   56px;  /* health score 94 */

/* Weights */
--font-regular:  400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;
```

**Hierarchy**:
- Page heading: `--text-2xl` semibold
- Card title: `--text-lg` medium (uppercase tracking-wide for tile labels)
- Card value (hero): `--text-3xl` to `--text-4xl` bold
- Card label: `--text-xs` semibold uppercase tracking-widest secondary color
- Body: `--text-base` regular

---

## 🧩 Component Anatomy

### Sidebar nav (image 1, 2, 4, 5)
- **Width**: 220-260px (collapses to icons on smaller screens)
- **Background**: `--bg-surface` slightly darker
- **Item**: 12px y / 16px x padding, icon + label
- **Active**: `--bg-elevated` + green left border (3px)
- **Hover**: `--bg-card-hover`
- **Top**: brand mark "SMART HOME" + Homey Pro badge
- **Bottom**: user profile / system status indicator

### Top status bar (image 1, 2, 4, 5)
- **Height**: 56-64px
- **Left**: page title + subtitle
- **Center / Right**: status pills (HOME MODE, SECURITY, ALARM, AI STATUS, WEATHER) — each is small card
- **Far right**: clock + date + user avatar
- **Status pill anatomy**: icon + label + value, ~120-140px wide

### Status tile (image 1 — top row)
- 6 horizontal tiles (REŽIM DOMU, PŘÍTOMNOST, DENNÍ FÁZE, VENKOVNÍ TEPLOTA, SPOTŘEBA, SYSTÉM)
- Layout: label (top, uppercase tiny) + icon (large center, glowing) + value (medium) + sub-text (tiny)
- Width ~180px, height ~140px
- Active uses tinted glow + colored icon

### Mode pills row (image 2 — DOMA/VENKU/SPÁT/...)
- 7 buttons, equal width, ~120px each
- Active: filled with mode color, white text
- Inactive: dark card, gray label, mode-color icon

### Lighting card (image 1, 2, 4)
- Header: room name (left) + ON/OFF state badge (right)
- Body: large slider with percentage label
- Optional: light icon glowing yellow when on
- Height ~120px

### Climate card (image 1, 4)
- Hero number: temp °C (large 32px+)
- Sub: humidity / target / "AUTO" badge
- Mode strip at bottom: AUTO / CHLAZENÍ / TOPENÍ / VLHKOST / VENTILACE
- Active mode highlighted with accent

### Camera live tile (image 1, 4)
- 16:9 aspect ratio
- LIVE badge top-left (red dot + "LIVE")
- Camera name + timestamp overlay bottom
- Hover: brightness boost

### Scene card (image 1, 3, 4)
- Icon-led
- Some have rich background images (image 3: scenes orchestrator)
- Trigger button (play arrow) bottom-right

### Energy flow / Sankey (image 3)
- Solar → Battery / House / Grid flows
- Animated colored ribbons
- Center node = total kW
- Right side: stats by destination

### AI Brain visual (image 5)
- Central animated brain icon with orbital connections
- Connected nodes: Přítomnost / Fáze dne / Lux / Teplota / Hluk / Režim / Aktivita
- Subtle glow + slow pulse

### Mini sparkline (image 3, 4, 5)
- 60-120px wide × 24-32px tall
- Single line, accent color
- Optional fill gradient under line

### Health gauge (image 2, 4)
- Circular SVG, ~140-180px diameter
- Score in center (large, 48px+)
- Color-graded: green (>90), amber (70-89), red (<70)
- Sub label "VÝBORNÉ" / "DOBRÉ" / "POZOR"

### Activity feed (image 1, 4)
- Vertical list of timeline items
- Each: timestamp (small) + icon + title (bold) + subtitle
- ~52px row height

---

## 🌐 Responsive Strategy

### Breakpoints (refined from references)
```css
@media (max-width: 480px)  { /* mobile */ }
@media (max-width: 768px)  { /* tablet portrait */ }
@media (max-width: 1024px) { /* tablet landscape / RPi WaveShare */ }
@media (max-width: 1280px) { /* small laptop */ }
@media (max-width: 1599px) { /* standard laptop */ }
@media (min-width: 1600px) { /* PC monitor */ }
@media (min-width: 2200px) { /* ultrawide / 32" 2880 */ }
```

### Layout strategy
- **Mobile (<768)**: 1-column, full-width cards, bottom nav (5 main tabs)
- **Tablet (1024×600)**: 2-column with collapsed sidebar (icon-only)
- **Laptop (1920)**: full sidebar + 3-column main grid
- **PC monitor (2880)**: full sidebar + 4-column main grid OR 3-column with 1.5× larger tiles

### Ultrawide fix (CRITICAL — fixes V3 collapse @ 2880)
- **Don't** keep `max-width: 1600px` rigid
- **Do** scale grid columns up at `min-width: 2200px`:
  ```css
  @media (min-width: 2200px) {
    .home-grid { grid-template-columns: 280px 1fr 380px; max-width: none; }
    /* sidebar | main | side rail */
  }
  ```
- Add **side rail** with mini-charts, weather, alerts at 2200+

---

## 🎬 Motion / Transitions

```css
/* Standard transitions */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

--duration-fast:    150ms;  /* hover states */
--duration-base:    250ms;  /* card transitions */
--duration-slow:    400ms;  /* page transitions */
--duration-glacial: 800ms;  /* deliberate reveals */
```

Key motion patterns:
- Card hover: `transform: translateY(-2px)` + shadow lift, 250ms ease-out
- Active state pulse: subtle 2s infinite for "LIVE" indicators
- Sidebar slide: 250ms ease-out
- Page swap: 200ms fade (avoid distracting)

---

## 📊 Data Viz

- **Charts**: SVG (no external lib), use accent gradients
- **Sparklines**: 1.5px stroke, smoothed line + 30% opacity gradient fill
- **Bars**: rounded corners (4px), gradient top→bottom
- **Donut**: 12px stroke, segment colors per category
- **Gauges**: SVG arc with 8-12px stroke, animate dasharray

---

## 🔑 Visual Hierarchy Rules

1. **Hero values** (temperature, kWh, score) — always largest type, highest contrast
2. **Status indicators** (badges, pills) — accent color for state (green/amber/red)
3. **Section labels** — uppercase, tracking-widest, secondary color, small
4. **Body text** — high contrast, readable line-height (1.5)
5. **Captions** — tertiary color, smallest size

**One focal point per card.** Don't compete.

---

## 🚫 Anti-patterns (avoid)

- ❌ Multiple competing accent colors in one tile
- ❌ Borders and gradients fighting (pick one)
- ❌ Plain rectangle "boxes" (always have either subtle grad or border highlight)
- ❌ Equal weight on all elements (must have hierarchy)
- ❌ Tiny touch targets (<44px on touch devices)
- ❌ Centered text in long blocks (use left-align except hero values)
- ❌ Square-edged cards (always round 10px+)

---

## ✅ Mapping references → Our pages

| Our page | Inspired by | Klíčové prvky převzít |
|---|---|---|
| `page-home` | Image 1 | Greeting header, 6 status tiles, lighting+scenes+cameras layout |
| `page-zones` | Image 1, 4 (Lighting page) | Room cards with sliders, on/off badges |
| `page-audio` | Image 1, 2, 4 | Now playing player + zones list + quick controls |
| `page-heating`, `heating2` | Image 4 (Heating) | Per-room temp cards + weekly program panel |
| `page-camera` | Image 1, 4 | 16:9 grid + LIVE badges + detect/record toggles |
| `page-finance` | Image 3 (Energy Cockpit) | Sankey flow + tariffs + top consumers + daily balance |
| `page-ai` | Image 5 (AI Brain) | Intent center + brain visual + predictions + recommendations |
| `page-settings` | Image 5 (Governance Console) | System overview + priority engine + overrides + integrations + backup |
| `page-historie` | Image 3 (Analytics) | 4 stat tiles + multi-line chart + zone donut + events scatter |
| `page-burza` | Image 3 (Energy reused style) | Crypto in same cockpit pattern |
| `page-weather` | Image 1 (mini), Image 3 detail | Hero current + 5-day strip + AI weather impact |
| `page-logy`, `page-advanced` | Image 3 (Diagnostics) | Mission control: health score + offline list + router latency + errors + heartbeat |

---

## 📝 Implementation notes (Phase 3 CSS patch)

- **CSS variables only** — define above tokens at `:root`, then refactor existing classes to use them
- **DO NOT** rewrite HTML structure — just CSS
- **DO NOT** touch JS / onclick / IDs
- Add **new utility classes** for: `.card-hero`, `.card-status`, `.scene-card`, `.glow-*`, `.tile-grid-auto`
- Refine existing `.tile`, `.card`, `.btn`, `.sect` to match anchors
- Use `clamp()` for responsive font sizes:
  ```css
  font-size: clamp(15px, 1.2vw, 20px);
  ```
- Use CSS Grid `auto-fit` with `minmax()` for self-adjusting tile rows
