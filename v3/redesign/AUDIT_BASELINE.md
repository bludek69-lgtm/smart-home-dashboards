# Visual Audit — Baseline Findings (Phase 2A partial)
**Date**: 2026-04-25 noc, V3 master @ 4 resolutions
**Tooling**: Claude Preview + Python http.server :8123

---

## 🔴 KEY FINDING — Ultrawide layout collapse @ 2880×1800

`.home-grid` container: **1590px max-width centered** in 2880 viewport → **~1290 px wasted** (645px each side, black void).

```
.home-grid: 949px (left tiles) + 632px (right camera) = 1590px / 2880px
```

**Consequence**: At 2880×1800 (user's main 32" monitor), dashboard looks lost in middle of black ocean. Tiles look tiny relative to screen.

**Memory note**: earlier commit `c013ba6` set `max-width: 1600px` deliberately for centering. But on 2880px screens this is too conservative.

---

## 📸 Per-resolution observations

### 1920×1080 (laptop) — ACCEPTABLE baseline
- Home grid fills width well
- Top tile row (4 status: Přítomnost / Fáze dne / Spánek / Health) — sparse, lots of unused space within tiles
- Floor zone tiles (Jídelna/Kuchyně/Ložnice/Koupelna + Pracovna/Prádelna/Předsíň/Toaleta) — 2 rows × 4 cols, OK
- Scene tiles row (Relax/Work/Audio/Vaření/Kino/Romantika/Reset) — 7 tiles squeezed
- Camera live feed = ~40% screen width on right
- Bottom tab bar: 14 tabs squeezed, labels truncated (HOME / ZONY / TOPENÍ / PLÁN / AUDIO / AI / LOGY / ...)
- **Hierarchy issue**: status tiles, zone tiles, scene tiles all visually equal weight — no clear primary focus

### 1024×600 (RPi WaveShare) — BROKEN OVERFLOW
- 4 tiles per row but **right edge cut off** (Spánek + Vaření partially visible)
- Camera in mini-frame (smaller layout)
- Bottom tab bar shows only **6 tabs** (instead of 14) — rest hidden/scroll?
- "Načítám..." footer takes vertical space
- **This is why V4 RPi exists** — V4 has sub-tab engine for narrow displays

### 2880×1800 (32" PC monitor) — UNDERUTILIZED
- Same 1590px content width as 1920 — **just blackness on sides**
- Tiles tiny relative to screen → readability hurts at distance
- NO larger info content (charts, status panels) to fill expanded space
- **Opportunity**: 2-column layout @ 2200px+ width (left: zones+status, right: camera+graphs)

### 430×932 (mobile) — NOT CAPTURED
TBD tomorrow — V3 master likely doesn't have mobile-optimized breakpoint.

---

## 🎨 Visual Issues (cross-resolution)

### Hierarchy
- **No primary CTA / focal point** — všechny tiles stejná weight
- Status tiles vs Zone tiles vs Scene tiles vyžadují vizuální separaci
- Top status row tiles působí jako "header info" ale jsou stejně velké jako zone navigation

### Density
- 1920: dobrá density
- 2880: **příliš sparse** (1590 obsahu v 2880 = 55% využití)
- 1024: **příliš dense + overflow**

### Tile design
- Mostly icon + label (centered)
- Inconsistent: top tiles mají kratší proporce (315×71 = 4.4:1), zone tiles square-ish
- Žádné progress / indicator bars
- Žádné mini sparklines
- Žádné secondary info (např. teplota uvnitř zone tiles)

### Color & Theme
- Dark theme works well
- Accent colors (red/green badges) readable
- BUT: tile borders subtle, low contrast vůči background → "flat panel" feeling
- Glass/blur effects MINIMAL — premium dashboards (Loxone/HA) mají subtle gloss

### Camera panel
- Funguje (LIVE badge, real feed visible)
- Default position: right column (640px) = velký prostor
- Could be smaller @ 1920, larger @ 2880

### Bottom nav
- 14 tabs = nepřehledné
- Icons OK, labels truncated
- **Should**: hierarchical group nav (4-5 primary + sub-menus)

---

## 💡 Design system priorities (Phase 2C TBD tomorrow)

### Must define
1. **Breakpoint strategy** — kdy 1-col vs 2-col vs sub-tabs
2. **Max-width tiers**: 1600 (laptop), 2200+ (PC monitor expand)
3. **Tile anatomy** — size, padding, content slots
4. **Hierarchy tokens**: Primary vs Secondary vs Tertiary tiles
5. **Spacing scale**: 4-8-12-16-24-32-48 grid
6. **Glass effects**: subtle blur + border highlights for depth
7. **Color tokens**: primary/secondary/accent/info/success/warning/danger
8. **Typography scale**: heading/body/caption with weight hierarchy

### Don't redesign (preserve)
- Camera live feed area (hard-won setup)
- TV remote modal
- Fuzzy device naming
- Roleta simulator
- SVG charts
- V4 sub-tabs engine (RPi only)

---

## ⏸ Stopped at this point

**Reason**: Late night, scope is multi-session.
**Status**:
- ✅ Phase 1 inventory done
- ✅ Phase 2A baseline screenshots @ 3/4 resolutions captured + observations
- ⏸ Phase 2A mobile pending (430×932)
- ⏸ Phase 2B detailed page-by-page audit pending (only home page captured)
- ⏸ Phase 2C design system definition pending
- ⏸ Phase 3+ pending

**Tomorrow continue with**:
1. Mobile screenshot 430×932
2. Per-page screenshots @ all 4 resolutions (7 pages × 4 res = 28 images)
3. Critique iteration
4. Design system definition
5. CSS patch
