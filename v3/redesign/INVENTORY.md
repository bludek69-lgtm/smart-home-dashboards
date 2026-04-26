# Dashboard Feature Inventory — V3/V4
**Generated**: 2026-04-25 noc
**Scope**: `smart_home_v3.html` (master, V3 PC) + `smart_home_v4_rpi.html` (V4 RPi)
**Files analyzed**: 61,218 řádků (v3: 9,831 + v4: 11,790 + variants)

---

## 1. PAGES (13)

| Page | Handler count | Účel |
|---|---|---|
| `page-zones` | 45 | Zones master view (jídelna/kuchyně/ložnice/pracovna/...) |
| `page-audio` | 12 | Speakers, TTS, volume |
| `page-ai` | 65 | AI control (V4 sub-tabs: Brain, Pipeline, Diagnostic) |
| `page-logy` | 38 | Event log + timeline |
| `page-weather` | 8 | Weather + 5-day forecast |
| `page-camera` | **47** ⚠ | TV remote (POWER/Vol/D-pad/numpad) + cameras |
| `page-settings` | **52** | Cfg editor (V4 sub-tabs: Connection/Wake/Roleta/Climate/Finance/Crypto) |
| `page-heating` | 38 | Topení zóny (V4 sub-tabs: Zones, Actions, AI) |
| `page-heating2` | 18 | Secondary heating panel |
| `page-advanced` | 35 | Validator + roleta sim (V4 sub-tabs: Validator/Roleta SIM/Settings) |
| `page-historie` | 24 | History/analytics charts |
| `page-finance` | 42 | NT/VT tariff + TOP 10 spotřebičů + Sheets API |
| `page-burza` | 28 | Crypto markets (CoinGecko) |

**Total: 325+ event handlers** (V3 = 293, V4 = 371 with sub-tabs delta +78)

---

## 2. HOMEY API CALLS — KRITICKÉ (Zero-Loss)

### `runScript()` — 22 unique
```
sh_anomaly_detector_v1, sh_audio_stop_v1, sh_autofix_engine_v1,
sh_conflict_guard_v1, sh_critical_devices_v1, sh_device_map_v1,
sh_diag_analyzer_v1, sh_error_tracker_v1, sh_evening_auto_v1,
sh_explain_last_action_v1, sh_gemini_daily_briefing_v1, sh_gemini_diagnostic_v1,
sh_meta_brain_v1, sh_morning_audit_v1, sh_morning_brain_v1, sh_self_healing_v4,
sh_sleep_brain_v2, sh_state_engine_v1, sh_system_health_v1, sh_system_reconcile_v1,
sh_time_sync_guard_v1, sh_tts_orchestrator_v1
```

### `writeVar()` — 25 unique
```
sh_ai_autonomy_level, sh_air_purifier_guard_enabled, sh_audio_request,
sh_autofix_mode, sh_cfg_heating_ai_enabled, sh_cfg_pm25_alerts_enabled,
sh_cfg_wake_threshold, sh_context_alert_cooldowns, sh_finance_snapshot,
sh_habit_mode, sh_heating_mode, sh_heating_preset, sh_heating_zone_*,
sh_house_state, sh_jsem_vstal, sh_morning_event, sh_notification_request,
sh_sleep_event, sh_sleep_triggered, sh_spim, sh_sunrise_active, sh_sunrise_step,
sh_tts_speaker, sh_tts_text, sh_visitor_mode_cmd
```

### `_getVar()` reads — 36 unique
Highlights: `sh_lux_jidelna, sh_jidelna_roleta_state, sh_rezim_doma, sh_spim, sh_cast_dne, sh_scene_active, sh_system_health_score, sh_morning_tune_recommendation, sh_finance_snapshot, sh_habit_*_avg, sh_cfg_lux_roleta_*, sh_cfg_price_nt/vt, sh_cfg_blind_*, sh_pracka_state, sh_wake_score_*` + 25 dalších

### Device Capabilities — 14+ devices
- `Kuchyn`, `nest max Ložnice 2` → `volume_set`
- `ventilatore` → `onoff`
- Smart plugs → `onoff`, `measure_power`
- Lights (Sektorka1, Stul Jidelna1, Led pasek, ...) → `dim`, `onoff`
- Heating valves (TRV) → `target_temperature`
- Roletas (Roleta Fyrtur1) → `windowcoverings_set`, `windowcoverings_state`
- Air purifier → `onoff`, target PM2.5

---

## 3. EVENT HANDLERS

| Type | Count |
|---|---|
| `onclick=` | 293 |
| `onchange=` | 32 |
| **Total** | **325+** |

Highest density per page: `page-camera` (47), `page-ai` (65), `page-settings` (52), `page-zones` (45)

---

## 4. JS FUNCTIONS — 106 top-level

**Core groups:**
- Navigation (12) — `switchPage`, `setupSubTabsForPage`, `topAncestor`, `relocateV` (V4)
- Homey API (8) — `apiGet/Put`, `runScript`, `writeVar`, `setDeviceCap`, `resolveDeviceName`, `_getVar`
- Device rendering (8) — `renderDeviceTile`, `openDeviceDetail`, `_DEV_DETAIL_RENDERERS`
- Audio (4) — `audioRequest`, `audioStop`, `volumeSet*`, `ttsTrigger`
- Heating (5) — `heatingModeSet`, `heatingPresetSet`, `heatingZoneAdjust`
- Config (6) — `cfgEdit`, `cfgSave`, `cfgValidate` (per category)
- Validator (8) — `validatorRun`, `validatorRender`, ... (Advanced page)
- Finance (12) — `financeFetch`, `financeRender`, NT/VT calc, top10
- History (8) — `historyChart*`, `historyRender`
- Wake (5) — `wakeScoreRender`, `wakeRecommend`
- Camera/IR (7) — `tvKey`, `tvMute`, `irToggle`, ...
- Utilities (14+) — formatters, helpers, fetchers

---

## 5. CSS CLASSES — 45 key

| Class | Count | Účel |
|---|---|---|
| `.page` | 13 | Page containers |
| `.sect` | 85 | Section blocks |
| `.tile` | 48 | Tile cards |
| `.btn` | 69 | Buttons |
| `.card` | 52 | Card containers |
| `.modal*` | 7 | Modal overlays |
| `.toggle` | 12 | Toggle switches |
| `.help-panel` | 32 | Help text panels |

+ další (`.chip`, `.sparkline`, `.glow`, ...)

---

## 6. RESPONSIVE BREAKPOINTS — 9 @media queries

```
@media (max-width: 1024px)  — RPi WaveShare native
@media (max-width: 900px)
@media (max-width: 1100px)
@media (max-width: 1366px)  — laptop sub-1080
@media (max-width: 1599px)
@media (max-height: 560px)  — narrow screens
@media (max-height: 720px)
@media (max-height: 800px)  — RPi 1280×800
@media (min-width: 1600px)  — PC 32" 2880
```

---

## 7. EXTERNAL APIs — 4 domains

| API | Use case | Endpoint pattern |
|---|---|---|
| **CoinGecko** | Crypto prices | `api.coingecko.com/api/v3/simple/price` |
| **Binance** | Crypto fallback | `api.binance.com/api/v3/ticker/price` |
| **Frankfurter** | USD↔CZK | `api.frankfurter.app/latest?from=USD&to=CZK` |
| **Google Sheets** | Stats/events/tasks | `script.google.com/macros/s/...` |
| **Homey Local** | Devices/vars/scripts/flows | `192.168.1.142/api/manager/*` |

---

## 8. V4 RPi SUB-TABS ENGINE (NEW)

Critical NEW feature in V4 only:
- **`V4_SUB_TABS_MAP`**: mapuje stránky na 3-4 sub-záložky
- Použito v 4 stránkách:
  - `page-ai` → Brain | Pipeline | Diagnostic
  - `page-advanced` → Validator | Roleta SIM | Settings
  - `page-heating` → Zones | Actions | AI
  - `page-settings` → Connection | Wake | Roleta | Climate | Finance | Crypto
- Functions: `setupAllSubTabs()`, `setupSubTabsForPage()`, `topAncestor()`, `relocateV()`
- Regex matching na sec titles (dynamic tab routing)

**KRITICKÉ pro 1024×600 displej** — bez sub-tabs jsou stránky nečitelné na malém screen.

---

## 🔴 TOP 3 REDESIGN RIZIKA

### RISK 1 — Camera/IR Remote Modal
**Detail**: page-camera má 47 onclick handlerů, většina = TV remote tlačítka (POWER/MUTE/Vol/Play-Pause/Stop/CH±/D-pad/HOME/BACK/numpad 0-9). Native `key_*` capabilities.
**Risk**: 1 vynechané tlačítko = nefunkční remote.
**Mitigation**: Kopírovat IR matrix přesně, preservovat `tvMute()`, `toggleIR()`. Test na reálném zařízení.

### RISK 2 — V4 Sub-Tabs System (NEW, RPi only)
**Detail**: V3 nemá tento kód; V4 RPi to vyžaduje na 1024×600. +78 onclick handlerů jen pro tabs.
**Risk**: Kopírováním V3 logiky se rozbije RPi navigace.
**Mitigation**: Zachovat `V4_SUB_TABS_MAP` + `setupSubTabsForPage` 1:1, test na 1024×600.

### RISK 3 — Finance + Burza Pages
**Detail**: 70 handlerů na 2 page (finance 42 + burza 28), 4 external APIs, SVG grafy, localStorage cache.
**Risk**: Změna formátu = rozbité price alerts, portfolio, energy calc.
**Mitigation**: Preservovat všechny formattery, ověřit coin IDs, fallback timeouts (5s).

---

## ⭐ 5 FEATURES TO PRESERVE AS-IS (don't redesign)

1. **TV Remote Modal** — komplexní, funguje, nepřepracovávat
2. **Variable Cache System** (`_getVar` + `loadVarMap`) — eliminates race conditions, kritické pro performance
3. **Fuzzy Device Naming** (`resolveDeviceName`) — kritické pro UX (mapování friendly names → IDs)
4. **Roleta Simulator** — komplexní math, zachovat 1:1
5. **SVG Charts** — bez Chart.js deps, optimalizované pro bandwidth, nešahat

---

## 📊 TOTAL COUNTS

| Category | Count |
|---|---|
| Pages | 13 |
| Scripts called | 22 |
| Variables written | 25 |
| Variables read | 36 |
| Devices controlled | 14+ |
| JS functions | 106 |
| CSS classes (key) | 45 |
| Event handlers | 325+ |
| Responsive breakpoints | 9 |
| External API domains | 4 |
| Lines of code (total) | 61,218 |

---

## ✅ Checkpoint 1 — DONE

**Self-review:**
- ✓ Všechny pages enumerované
- ✓ Všechny Homey API calls (scripts/vars/devices) zmapované
- ✓ Risks identifikované
- ✓ Features to preserve označeny

**Next**: Checkpoint 2 — Visual audit + design system definition. **Ráno**.
