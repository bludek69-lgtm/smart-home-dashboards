# Smart Home Dashboard — Premium Redesign Plan v7
**Started**: 2026-04-25 noc
**Mission**: Premium redesign existující V3/V4 dashboard, ZERO regression
**Quality target**: Vendor-grade (Loxone/HA premium level)

---

## 🔒 HARD LOCKS (nikdy neporušit)
- ✋ NEVER touch JS logic
- ✋ NEVER touch onclick handlers
- ✋ NEVER touch IDs (243 interactive divs per memory)
- ✋ NEVER break Homey REST API calls (`runScript`, `writeVar`, `setDeviceCap`)
- ✋ NEVER touch `_sync_variants.py` script logic
- ✋ NEVER break responsive breakpoints (4 resolutions: 2880×1800, 1920×1080, 1024×600, mobile)

**Pokud regrese → ROLLBACK z `_redesign_backup_<timestamp>` adresáře.**

---

## 📁 Source files
- `smart_home_v3.html` (master, 540 KB) — PC 32" 16:10
- `smart_home_v3_1920.html` — 14" notebook 16:9
- `smart_home_v3_2880.html` — 32" 2880×1800 16:10
- `smart_home_v3_rpi.html` — RPi 1280×800
- `smart_home_v3_rpi_1024.html` — WaveShare 1024×600
- `smart_home_v4_rpi.html` — RPi V4 with sub-tab engine (newer, 649 KB)

**Active variants for redesign**:
- V3 (PC) — master + 1920 + 2880
- V4 (RPi) — replacing v3_rpi*

---

## 🗂 Phase Tree

### CHECKPOINT 1 — INVENTORY (Workstream A)
- [ ] Catalog all pages per variant
- [ ] Catalog all `runScript('sh_*')` calls
- [ ] Catalog all `writeVar()` calls
- [ ] Catalog all `setDeviceCap()` calls
- [ ] Catalog all interactive widgets (modals, sliders, tiles)
- [ ] **Output**: `INVENTORY.md` — feature parity matrix
- [ ] **Self-review**: každá feature musí být zdokumentovaná, žádné slepé skvrny

### CHECKPOINT 2 — REDESIGN CONCEPT (Workstream B)
- [ ] Render current state — 4 resolutions × 7 pages = 28 screenshots (Playwright)
- [ ] Visual audit findings (overcrowded? wasted space? hierarchy issues?)
- [ ] Define design system:
  - Colors (palette + tokens)
  - Typography (scale, weights, families)
  - Spacing (4-8-12-16-24-32-48 grid?)
  - Glass / blur / shadow effects
  - Component anatomy (tiles, modals, sidebar)
  - Motion (transitions, easing)
- [ ] Reference comparison vs Loxone/HA Premium screenshots
- [ ] **Output**: `DESIGN_SYSTEM.md` + `BEFORE_screenshots/`
- [ ] **Self-review**: design system pokrývá vše vidíme v dashboardu

### CHECKPOINT 3 — CSS PATCH (Workstream C)
- [ ] Backup `_redesign_backup_<timestamp>/`
- [ ] Aplikovat design system **JEN přes CSS** (variables, classes)
- [ ] Žádné HTML structure changes
- [ ] Žádné JS changes
- [ ] Test v browseru každé page (manual)
- [ ] **Output**: Patched HTMLs + `CSS_DIFF.md`
- [ ] **Self-review**: žádný HARD LOCK porušen, regression-free

### CHECKPOINT 4 — SCREENSHOT QA (Workstream D)
- [ ] Render after-state — 4 resolutions × 7 pages
- [ ] Generate before/after comparison boards
- [ ] Self-critique loop (3 iterations):
  - "Co stále vypadá slabě?"
  - "Co je přeplněné?"
  - "Co se opakuje zbytečně?"
- [ ] Improve CSS based on findings
- [ ] **Output**: `AFTER_screenshots/` + `COMPARISON_BOARDS/` + 3 critique iterations
- [ ] **Self-review**: každá page projde QA checklist

### CHECKPOINT 5 — DOCUMENTATION (Workstream E)
- [ ] `REDESIGN_HANDBOOK.md` — proč + co + jak
- [ ] `RESPONSIVE_GUIDE.md` — breakpointy + adaptace per device
- [ ] `DESIGN_SYSTEM.md` (refined post-QA)
- [ ] `QA_CHECKLIST.md`
- [ ] Annotated screenshot review
- [ ] **Output**: kompletní dokumentační balíček v `redesign/docs/`

### CHECKPOINT 6 — FINAL PACKAGE
- [ ] Production HTMLs (master + variants)
- [ ] Verify `_sync_variants.py` still works
- [ ] Deploy plan (RPi + GitHub Pages)
- [ ] Rollback procedure documented
- [ ] **Output**: shipping package + handoff

---

## 🛠 Tooling
- **Render/QA**: Playwright (zatím není set up — zařídit v Phase 4)
- **Screenshot**: `npx playwright screenshot` per page × resolution
- **Diff**: git diff přes redesign branch
- **Live preview**: Chromium kiosk na RPi (192.168.1.122)

---

## 📊 Effort estimate (realistic)
| Phase | Time | Session |
|---|---|---|
| 1 Inventory | 30-60 min | tonight (start) |
| 2 Concept | 60-90 min | tomorrow morning |
| 3 CSS patch | 2-3h | tomorrow |
| 4 QA loop | 1-2h | tomorrow afternoon |
| 5 Docs | 60 min | tomorrow evening |
| 6 Package | 30 min | end |

**Total: ~6-9h spread over 2-3 sessions**

---

## ⚠ Rizika
1. **HTMLs jsou velké** (500-650KB) — read in chunks, grep targeted
2. **243 onclick handlers** — žádný se nesmí rozbít. Inventory MUSÍ být úplný.
3. **Playwright not installed** — bude třeba install npm + playwright (~3 min)
4. **GitHub Pages cache** — po deploy možná force refresh
5. **RPi WaveShare 1024×600** — fyzický displej, screenshot z desktop nemusí matchnout

---

## ✅ Dnes večer scope
- [x] Plan dokument (TENTO soubor)
- [ ] **Checkpoint 1 inventory** — feature parity matrix (spawned subagent)
- ⏸ Phase 2-6 — zítra

Stop after Checkpoint 1. User review. Continue tomorrow.
