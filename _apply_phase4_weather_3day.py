"""
PHASE 4 — Weather 3-day daily aggregation + Energy kWh hint
Idempotent. Marker: PHASE4_WEATHER_3DAY_APPLIED.

REUSE FIRST audit:
  - Existing page-weather už má current + 24h (8×3h) forecast
  - Existing page-finance už má totalKWh + top 5 devices + monthly projection
  - → Phase 4 přidá JEN co chybí: 3-day DAILY aggregation

ADDS:
  1) <div id="wx-forecast-daily"></div> pod existující forecast grid na weather page
  2) cnt=16 → cnt=24 v OWM API URL (72h pro 3-day agregaci)
  3) aggregateDailyForecast() + renderWeatherDaily() funkce
  4) Call z existing renderWeather()
  5) Bonus: s-power tile tooltip rozšířen o "dnes X kWh" info
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

MARKER = 'PHASE4_WEATHER_3DAY_APPLIED'

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 1: Add <div id="wx-forecast-daily"></div> after existing forecast
# ═══════════════════════════════════════════════════════════════════════════
OLD_FC_DIV = '''      <div class="sect" style="color:var(--green);margin-top:8px;">PŘEDPOVĚĎ · 24H</div>
      <div id="wx-forecast"></div>'''

NEW_FC_DIV = '''      <div class="sect" style="color:var(--green);margin-top:8px;">PŘEDPOVĚĎ · 24H</div>
      <div id="wx-forecast"></div>
      <!-- PHASE4_WEATHER_3DAY_APPLIED -->
      <div class="sect" style="color:var(--green);margin-top:8px;">PŘEDPOVĚĎ · 3 DNY</div>
      <div id="wx-forecast-daily"></div>'''

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 2: Bump cnt=16 → cnt=24 (72h of data for 3-day aggregation)
# ═══════════════════════════════════════════════════════════════════════════
OLD_CNT = 'cnt=16'
NEW_CNT = 'cnt=24'

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 3: Call renderWeatherDaily from existing renderWeather
# Anchor: "  el('wx-loading').style.display = 'none';"
# ═══════════════════════════════════════════════════════════════════════════
OLD_RENDER_TAIL = '''  el('wx-forecast').innerHTML = html;
  el('wx-updated').textContent = 'Aktualizováno: ' + new Date().toLocaleTimeString('cs-CZ', { timeZone: 'Europe/Prague' });

  el('wx-loading').style.display = 'none';
  el('wx-main').style.display = 'block';
}'''

NEW_RENDER_TAIL = '''  el('wx-forecast').innerHTML = html;
  el('wx-updated').textContent = 'Aktualizováno: ' + new Date().toLocaleTimeString('cs-CZ', { timeZone: 'Europe/Prague' });

  // PHASE4_WEATHER_3DAY_APPLIED — render 3-day daily aggregation
  try { renderWeatherDaily(fc); } catch(e) { console.warn('daily forecast err', e); }

  el('wx-loading').style.display = 'none';
  el('wx-main').style.display = 'block';
}

// ══ PHASE4_WEATHER_3DAY_APPLIED — helpers ═════════════════════════════════
function _wxPragueDateKey(unix) {
  const d = new Date(unix * 1000);
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Prague', year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
}
function _wxPragueDayName(unix) {
  const d = new Date(unix * 1000);
  return new Intl.DateTimeFormat('cs-CZ', { timeZone: 'Europe/Prague', weekday: 'short', day: 'numeric', month: 'numeric' }).format(d);
}

function aggregateDailyForecast(fc) {
  const items = (fc && fc.list) || [];
  const byDay = {};
  for (const it of items) {
    const k = _wxPragueDateKey(it.dt);
    if (!byDay[k]) byDay[k] = { items: [], dt_first: it.dt };
    byDay[k].items.push(it);
  }
  const days = Object.keys(byDay).sort();
  const todayKey = _wxPragueDateKey(Math.floor(Date.now() / 1000));
  // Skip today (already shown in hourly) — take next 3 days
  const future = days.filter(k => k > todayKey).slice(0, 3);
  return future.map(k => {
    const day = byDay[k];
    const temps = day.items.map(x => Number(x.main && x.main.temp) || 0);
    const rains = day.items.map(x => Number((x.rain && (x.rain['3h'] || x.rain['1h'])) || 0));
    const winds = day.items.map(x => Number((x.wind && x.wind.speed) || 0) * 3.6);
    // Pick representative condition: the one around 12:00 Prague, or max frequency
    let rep = day.items[0];
    for (const it of day.items) {
      const h = new Date(it.dt * 1000).toLocaleString('en-GB', { timeZone: 'Europe/Prague', hour: '2-digit', hour12: false });
      if (h === '12') { rep = it; break; }
    }
    return {
      dateKey: k,
      dtFirst: day.dt_first,
      dayLabel: _wxPragueDayName(day.dt_first),
      tMin: Math.round(Math.min(...temps)),
      tMax: Math.round(Math.max(...temps)),
      rainSum: rains.reduce((a, b) => a + b, 0),
      windMax: Math.round(Math.max(...winds)),
      icon: (rep.weather && rep.weather[0] && rep.weather[0].icon) || '',
      desc: (rep.weather && rep.weather[0] && rep.weather[0].description) || '',
      pop: Math.round(Math.max(...day.items.map(x => Number(x.pop) || 0)) * 100)
    };
  });
}

function renderWeatherDaily(fc) {
  const el = document.getElementById('wx-forecast-daily');
  if (!el) return;
  const days = aggregateDailyForecast(fc);
  if (!days.length) { el.innerHTML = '<div style="color:var(--tx3);font-size:11px;padding:8px;text-align:center;">Data pro 3-day agregaci chybí (ověř cnt v OWM URL).</div>'; return; }
  let html = '<div style="display:grid;grid-template-columns:repeat(' + days.length + ',1fr);gap:6px;">';
  for (const d of days) {
    const iconHtml = (typeof wxIconImg === 'function') ? wxIconImg(d.icon, 56) : '';
    const rainStr = d.rainSum > 0.1 ? ' · 🌧 ' + d.rainSum.toFixed(1) + ' mm' : '';
    html += '<div style="background:var(--bg2);border:1px solid var(--bd);border-radius:var(--r2);padding:10px 8px;text-align:center;">' +
      '<div style="font-size:11px;color:var(--cyan);font-family:var(--mono);font-weight:500;">' + d.dayLabel + '</div>' +
      '<div style="margin:4px 0;line-height:1;">' + iconHtml + '</div>' +
      '<div style="font-size:22px;font-weight:700;color:var(--tx1);line-height:1.1;">' +
        '<span style="color:var(--red);">' + d.tMax + '°</span>' +
        ' <span style="font-size:13px;color:var(--tx3);">/ ' + d.tMin + '°</span>' +
      '</div>' +
      '<div style="font-size:10px;color:var(--tx2);margin-top:3px;">' + d.desc + '</div>' +
      '<div style="font-size:10px;color:var(--tx3);margin-top:2px;font-family:var(--mono);">💨 ' + d.windMax + ' km/h' + rainStr + '</div>' +
      (d.pop > 0 ? '<div style="font-size:10px;color:var(--blue);margin-top:1px;font-family:var(--mono);">💧 pop ' + d.pop + '%</div>' : '') +
    '</div>';
  }
  html += '</div>';
  el.innerHTML = html;
}
// ══ END PHASE4 ══════════════════════════════════════════════════════════='''

# ═══════════════════════════════════════════════════════════════════════════
# PATCH 4: s-power tile — enhance title tooltip with kWh info + optional inline kWh
# Old line: setText('s-power', Math.round(h.power_total||0) + ' W');
# New: also show today kWh from sh_finance_snapshot
# ═══════════════════════════════════════════════════════════════════════════
OLD_SPOWER = "  setText('s-power', Math.round(h.power_total||0) + ' W');"

NEW_SPOWER = """  // PHASE4_WEATHER_3DAY_APPLIED — enhance s-power with today kWh
  (function() {
    let kwhSuffix = '';
    try {
      const snapRaw = String((ALL_VARS && ALL_VARS['sh_finance_snapshot'] && ALL_VARS['sh_finance_snapshot'].value) || '');
      if (snapRaw && snapRaw.length > 2) {
        const snap = JSON.parse(snapRaw);
        const t = Number(snap.totalKWh || 0);
        if (t > 0) kwhSuffix = ' · ' + t.toFixed(1) + ' kWh';
      }
    } catch(_){}
    setText('s-power', Math.round(h.power_total||0) + ' W' + kwhSuffix);
  })();"""


def patch(fp):
    if not os.path.exists(fp):
        print(f"  ❌ SKIP (not found): {fp}")
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        content = f.read()
    if MARKER in content:
        print(f"  ⏭️  ALREADY PATCHED: {os.path.basename(fp)}")
        return
    orig = content
    changes = []
    is_crlf = '\r\n' in content[:4096]

    def replace(old, new, label, count=1):
        nonlocal content
        old2 = old.replace('\n', '\r\n') if is_crlf else old
        new2 = new.replace('\n', '\r\n') if is_crlf else new
        if old2 in content:
            content = content.replace(old2, new2, count)
            changes.append(label)
        else:
            changes.append('❌ ' + label + ' (not found)')

    replace(OLD_FC_DIV, NEW_FC_DIV, 'Add wx-forecast-daily div on weather page')
    # cnt=16 appears once in the OWM URL
    replace(OLD_CNT, NEW_CNT, 'Bump cnt=16 → cnt=24 (72h data)')
    replace(OLD_RENDER_TAIL, NEW_RENDER_TAIL, 'Add renderWeatherDaily + aggregator helpers')
    replace(OLD_SPOWER, NEW_SPOWER, 'Enhance s-power tile with today kWh')

    failed = [c for c in changes if c.startswith('❌')]
    if content != orig and not failed:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ PATCHED: {os.path.basename(fp)}")
        for c in changes:
            print(f"     + {c}")
    else:
        print(f"  ⚠️  PROBLEM: {os.path.basename(fp)}")
        for c in changes:
            print(f"     {c}")


if __name__ == '__main__':
    print('PHASE 4 — Weather 3-day daily + s-power kWh')
    print('=' * 60)
    for f in FILES:
        print(f"Processing: {os.path.basename(f)}")
        patch(f)
        print()
    print('Hotovo.')
