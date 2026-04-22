# 🎨 Dashboard v3 — v1 ovládání + v2 grafika

**Datum**: 2026-04-23 večer
**Status**: První release (theme-only port)

## Koncepce

**v3 = v1 dashboard (plná funkcionalita) přestylený do v2 moderního vzhledu**

Žádná ztráta funkce. Všechny v1 features zachované:
- Kompletní **ADVANCED** page (Sanity guard, Device audit, Roleta simulator)
- **AI CONTROL CENTER** (Meta Brain, Predict, Coordinator, 12 diag buttons, 7 overrides)
- **Heating PLÁN** (týdenní editor — visual timeline gradient)
- **BURZA portfolio** (BTC/ETH localStorage + TTS alert)
- **FINANCE** page (VT/NT tarify, TOP 10 spotřebičů, měsíční projekce)
- **ZÓNY** — 9 zon + detailní zone view s device tiles
- **KAMERA** live Foscam polling 3s
- **Scény** — Relax/Work/Audio/Vaření/Kino/Romantika + Reset
- **167 tooltipů** zachováno
- **10 help expandable panels** zachováno

## Co bylo změněno (jen CSS vrstva)

### Design tokens (`:root`)
| Token | v1 hodnota | v3 hodnota (z v2) |
|---|---|---|
| `--bg0` | `#1a0a2e` (fialová) | `#0a0f1c` (neutrální dark) |
| `--bg1` | `#1e1035` | `#111729` |
| `--cyan` | `#64f4d8` | `#22d3ee` (saturovanější) |
| `--green` | `#5ee8a0` | `#3bc97d` |
| `--red` | `#ff6b6b` | `#ef4444` |
| `--purple` | `#c084fc` | `#a855f7` |
| `--orange` | `#ffb347` | `#ff9f40` |
| `--r` (radii) | 14/18/22 px | 12/16/20 px (softer) |
| `--sans` | 'DM Sans' | 'Inter' |

### Nové CSS features
- **Body gradient**: `linear-gradient(180deg, #0a0f1c 0%, #13192b 100%)`
- **Card shadows**: moderní layered (2px/4px/8px/16px/32px)
- **Tile hover**: `transform: translateY(-1px)` + glow cyan
- **Scene active**: glow outline při aktivaci
- **Tabs**: glass blur + cyan glow na aktivní
- **Input focus**: cyan ring 3px
- **Scrollbars**: thin rounded (10px)
- **Page transitions**: 320ms fade + slide
- **Help buttons**: cyan pill s glow

### Fonts
- **Inter** (400-800 weights) — headings + UI
- **JetBrains Mono** — číselné hodnoty (ceny, teploty, časy)
- Importováno z Google Fonts CDN

### v3 banner
Small pill v pravém horním rohu "**v3 • theme**" (informativní, nic neruší).

## Soubory

| File | Velikost | Resolution |
|---|---|---|
| `smart_home_v3.html` | ~470 kB | master (responsive) |
| `smart_home_v3_1920.html` | ~470 kB | FullHD 1920×1080 |
| `smart_home_v3_2880.html` | ~460 kB | MacBook Retina 2880×1800 |
| `smart_home_v3_rpi.html` | ~452 kB | RPi touch 1024×600 |

## Test postup

```bash
# Local (LAN)
file:///C:/HOMEY%20PRO%202026/dasboardy_CLAUDE/v3/smart_home_v3.html

# GitHub Pages
https://bludek69-lgtm.github.io/smart-home-dashboards/v3/smart_home_v3.html
```

**Dashboard požaduje bearer token** (stejný jako v1 — Homey Web → Settings → Personal Access Tokens).

## Mezi v1/v2/v3

| Aspekt | v1 | v2 | **v3** |
|---|---|---|---|
| Navigace | Bottom tabs | Left sidebar | **Bottom tabs** |
| Grafika | Tmavě fialová | Moderní | **Moderní (v2)** |
| Ovládání | Všechno | Základní | **Všechno (v1)** |
| Počet pages | 13 | 14 | **13** |
| Tooltipů | 167 | ~50 | **167** |
| Help panelů | 10 | 3 | **10** |
| TV remote | ✓ (plný) | ✗ | **✓ (plný)** |
| ADVANCED page | ✓ | ✗ | **✓** |
| AI Control Center | ✓ (49 tiles) | Systém (~25) | **✓ (49 tiles)** |
| Heating editor | Týdenní visual | Jen cfg inputs | **Týdenní visual** |

## Známé limity

1. **CSS overlay nemusí být dokonalé** — některé v1 specifické třídy (`.cam-body`, `.hg-apps`) si mohou zachovat původní styl pokud ve `v3 overlay` nejsou
2. **Modal popupy** (infoModal, zoneHelpModal) vypadají trochu jinak — zachovány v1 styly
3. **Nav tabs vs sidebar** — v3 zachovává v1 bottom tabs (nepoužívá v2 sidebar)

## Další kroky (volitelné, next session)

- Pokud user chce **sidebar místo bottom tabs** → velká změna (restructure layout)
- Propagovat **Zone Detail pattern z v2** do v3 (all-in-one zone view)
- **Scene tooltip tooltips** napoprvé zkontrolovat funkčnost (v1 je má, ale CSS overlay by je neměl rozbít)
