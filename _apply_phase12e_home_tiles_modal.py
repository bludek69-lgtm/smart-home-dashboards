"""
PHASE 12e — Home tile clicks → modal with rich details

HOME page má 9 tiles (Přítomnost, Fáze, Spánek, Health, Intent, Výkon,
House State, Návštěva, Dovolená). Aktuálně jen Dovolená má onclick.

Přidávám onclick na ostatní → modal s detaily:

  🏠 Přítomnost → sh_rezim_doma + last transitions (home_ts / away_ts)
  ☀️ Fáze dne  → sh_cast_dne + kontext + auto schedule
  😴 Spánek    → sh_spim + trigger info + habit data
  💚 Health    → sh_system_health_report JSON (full health data)
  🎯 Intent    → sh_user_intent + source + time
  ⚡ Výkon     → total W + per-device breakdown z sh_finance_snapshot
  🔑 House     → sh_house_state + what it composed from
  👥 Návštěva  → sh_visitor_mode + TTS block state

Idempotent. Marker: PHASE12E_HOME_TILES_MODAL_APPLIED.
"""
import os

FILES = [
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_rpi.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_1920x1080.html',
    r'C:\HOMEY PRO 2026\dasboardy_CLAUDE\smart_home_2880x1800.html',
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH A: Add onclick to 8 home tiles
# ═══════════════════════════════════════════════════════════════════════════
REPLACEMENTS = [
    (
        '<div class="tile ht" id="s-presence-tile" title="sh_rezim_doma — home/away. Ovlivněno GPS + odchodové tlačítko.">',
        '<div class="tile ht" id="s-presence-tile" onclick="openHomeTileModal(\'presence\')" title="sh_rezim_doma — klikni pro detail + timestamps" style="cursor:pointer;">'
    ),
    (
        '<div class="tile ht" id="s-phase-tile" title="sh_cast_dne — morning/day/evening/night.">',
        '<div class="tile ht" id="s-phase-tile" onclick="openHomeTileModal(\'phase\')" title="sh_cast_dne — klikni pro detail + schedule" style="cursor:pointer;">'
    ),
    (
        '<div class="tile ht" id="s-sleep-tile" title="sh_spim — yes/no. Sleep button / ranní motion.">',
        '<div class="tile ht" id="s-sleep-tile" onclick="openHomeTileModal(\'sleep\')" title="sh_spim — klikni pro detail + habits" style="cursor:pointer;">'
    ),
    (
        '<div class="tile ht" id="s-health-tile" title="sh_system_health_score — 0-100%. Offline, baterie, errory.">',
        '<div class="tile ht" id="s-health-tile" onclick="openHomeTileModal(\'health\')" title="Klikni pro plný health report JSON" style="cursor:pointer;">'
    ),
    (
        '<div class="tile ht" id="s-intent-tile" title="sh_user_intent — aktuální záměr.">',
        '<div class="tile ht" id="s-intent-tile" onclick="openHomeTileModal(\'intent\')" title="sh_user_intent — klikni pro detail + source" style="cursor:pointer;">'
    ),
    (
        '<div class="tile ht" id="s-power-tile" title="sh_energy_total_power — aktuální spotřeba (W).">',
        '<div class="tile ht" id="s-power-tile" onclick="openHomeTileModal(\'power\')" title="Klikni pro rozpis top spotřebičů + kWh" style="cursor:pointer;">'
    ),
    (
        '<div class="tile ht" id="s-state-tile" title="sh_house_state — kompozitní stav.">',
        '<div class="tile ht" id="s-state-tile" onclick="openHomeTileModal(\'house_state\')" title="sh_house_state — klikni pro složení stavu" style="cursor:pointer;">'
    ),
    (
        '<div class="tile ht" id="s-visitor-tile" title="sh_visitor_mode — návštěva.">',
        '<div class="tile ht" id="s-visitor-tile" onclick="openHomeTileModal(\'visitor\')" title="sh_visitor_mode — klikni pro detail + TTS block state" style="cursor:pointer;">'
    ),
]

# ═══════════════════════════════════════════════════════════════════════════
# PATCH B: JS helper — openHomeTileModal
# ═══════════════════════════════════════════════════════════════════════════
JS_HELPER = """
// PHASE12E_HOME_TILES_MODAL_APPLIED — home tile clicks → modal s detaily
function openHomeTileModal(kind) {
  try {
    const av = (typeof ALL_VARS !== 'undefined') ? ALL_VARS : {};
    const get = k => (av[k] && av[k].value) || '';
    const esc = s => String(s == null ? '—' : s).replace(/[<>&]/g, c=>({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
    const fmtTs = ts => {
      if (!ts) return '—';
      const n = Number(ts);
      if (isNaN(n) || n < 1600000000) return String(ts);
      const d = new Date(n * 1000);
      const diffMin = Math.floor((Date.now()/1000 - n) / 60);
      const humanTime = d.toLocaleString('cs-CZ', {timeZone:'Europe/Prague'});
      return humanTime + ' <span style="color:var(--tx3);">(před ' + (diffMin < 60 ? diffMin + ' min' : Math.floor(diffMin/60) + ' h') + ')</span>';
    };

    let title, icon, html;

    if (kind === 'presence') {
      title = '🏠 Přítomnost — detail';
      icon = '🏠';
      const cur = get('sh_rezim_doma');
      const source = get('sh_presence_source') || '—';
      const homeTs = get('sh_presence_home_ts');
      const awayTs = get('sh_presence_away_ts');
      html = '<div class="im-kv">' +
        '<div class="k">Aktuální stav</div><div class="v"><strong style="color:' + (cur === 'home' ? 'var(--green)' : 'var(--orange)') + ';">' + esc(cur) + '</strong></div>' +
        '<div class="k">Zdroj změny</div><div class="v">' + esc(source) + '</div>' +
        '<div class="k">Poslední HOME</div><div class="v">' + fmtTs(homeTs) + '</div>' +
        '<div class="k">Poslední AWAY</div><div class="v">' + fmtTs(awayTs) + '</div>' +
      '</div>';
      html += '<div style="font-size:11px;color:var(--tx3);margin-top:12px;line-height:1.5;">Přítomnost se mění přes GPS (Homey app), tlačítko „Away/Home" u dveří, nebo manuálně. Script sh_presence_router_v1 loguje přechody do Google Sheets.</div>';
    }
    else if (kind === 'phase') {
      title = '☀️ Fáze dne — detail';
      icon = '☀️';
      const phase = get('sh_cast_dne');
      const phaseNames = {morning:'🌅 Ráno',day:'☀️ Den',evening:'🌆 Večer',night:'🌙 Noc'};
      html = '<div class="im-kv">' +
        '<div class="k">Aktuální fáze</div><div class="v"><strong style="color:var(--cyan);">' + (phaseNames[phase] || esc(phase)) + '</strong></div>' +
        '<div class="k">Night end</div><div class="v">sh_cfg_nt_end_hour = ' + esc(get('sh_cfg_nt_end_hour') || '6') + ':00</div>' +
        '<div class="k">Night start</div><div class="v">sh_cfg_nt_start_hour = ' + esc(get('sh_cfg_nt_start_hour') || '22') + ':00</div>' +
      '</div>';
      html += '<div style="margin-top:14px;padding:10px 12px;background:rgba(255,255,255,.03);border-radius:8px;font-size:11px;line-height:1.6;">' +
        '<strong>Plán:</strong><br>' +
        '• 06:00 → <strong>morning</strong><br>' +
        '• 10:00 → <strong>day</strong><br>' +
        '• 18:00 → <strong>evening</strong><br>' +
        '• 22:00 → <strong>night</strong>' +
      '</div>';
    }
    else if (kind === 'sleep') {
      title = '😴 Spánek — detail';
      icon = '😴';
      const spim = get('sh_spim');
      const jsemVstal = get('sh_jsem_vstal');
      const wakeConf = get('sh_wake_confidence');
      const zones = get('sh_wake_zones_active');
      const wakeAvg = get('sh_habit_wake_avg');
      const sleepAvg = get('sh_habit_sleep_avg');
      const fmtH = h => { const n=Number(h); if(!n) return '—'; const hr=Math.floor(n); const m=Math.round((n-hr)*60); return hr+':'+String(m).padStart(2,'0'); };
      html = '<div class="im-kv">' +
        '<div class="k">Spím</div><div class="v"><strong style="color:' + (spim === 'yes' ? 'var(--orange)' : 'var(--green)') + ';">' + esc(spim) + '</strong></div>' +
        '<div class="k">Jsem vstal</div><div class="v">' + esc(jsemVstal) + '</div>' +
        '<div class="k">Wake confidence</div><div class="v">' + esc(wakeConf) + ' / 3</div>' +
        '<div class="k">Active wake zones</div><div class="v">' + esc(zones) + '</div>' +
      '</div>';
      html += '<div style="margin-top:14px;padding:10px 12px;background:rgba(255,255,255,.03);border-radius:8px;font-size:11px;line-height:1.6;">' +
        '<strong>Habits (7d průměr):</strong><br>' +
        '🌅 Vstávání Ø ' + fmtH(wakeAvg) + '<br>' +
        '😴 Spánek Ø ' + fmtH(sleepAvg) +
      '</div>';
    }
    else if (kind === 'health') {
      title = '💚 System Health — kompletní report';
      icon = '💚';
      const score = get('sh_system_health_score');
      const status = get('sh_system_health_status');
      const report = get('sh_system_health_report');
      const pushMsg = get('push_zprava');
      let reportJson = null;
      try { reportJson = JSON.parse(report); } catch(_){}
      const scoreColor = Number(score) >= 90 ? 'var(--green)' : Number(score) >= 70 ? 'var(--orange)' : 'var(--red)';
      html = '<div style="font-size:24px;font-weight:700;color:' + scoreColor + ';text-align:center;padding:8px 0;">' + esc(score) + '%</div>';
      html += '<div class="im-kv" style="margin-bottom:14px;">' +
        '<div class="k">Status</div><div class="v">' + esc(status) + '</div>' +
        '<div class="k">Push msg</div><div class="v" style="font-size:11px;">' + esc(pushMsg) + '</div>' +
      '</div>';
      if (reportJson) {
        html += '<div style="font-size:11px;color:var(--purple);font-weight:600;margin-bottom:6px;">📋 Plný report</div>';
        html += '<pre style="font-family:var(--mono);font-size:10px;background:var(--bg2);padding:10px;border-radius:8px;white-space:pre-wrap;word-break:break-word;">' + esc(JSON.stringify(reportJson, null, 2)) + '</pre>';
      } else if (report) {
        html += '<div style="font-size:11px;white-space:pre-wrap;word-break:break-word;">' + esc(report) + '</div>';
      }
    }
    else if (kind === 'intent') {
      title = '🎯 User Intent — detail';
      icon = '🎯';
      const intent = get('sh_user_intent');
      const source = get('sh_user_intent_source');
      const req = get('sh_user_intent_request');
      html = '<div class="im-kv">' +
        '<div class="k">Aktuální intent</div><div class="v"><strong style="color:var(--cyan);">' + esc(intent) + '</strong></div>' +
        '<div class="k">Zdroj</div><div class="v">' + esc(source) + '</div>' +
        '<div class="k">Pending request</div><div class="v">' + esc(req) + '</div>' +
      '</div>';
      html += '<div style="font-size:11px;color:var(--tx3);margin-top:12px;line-height:1.5;">Intent je aktuální záměr usera (relax, work, cooking...). Vybírá se automaticky na základě scény + fáze dne + pohybu.</div>';
    }
    else if (kind === 'power') {
      title = '⚡ Spotřeba — rozpis';
      icon = '⚡';
      const totalW = Number((window.DATA && window.DATA.state && window.DATA.state.power_total) || 0);
      const snap = get('sh_finance_snapshot');
      html = '<div style="font-size:28px;font-weight:700;color:var(--cyan);text-align:center;padding:8px 0;">' + Math.round(totalW) + ' W</div>';
      try {
        const s = JSON.parse(snap);
        if (s.totalKWh) html += '<div style="text-align:center;font-size:14px;color:var(--tx2);margin-bottom:14px;">Měsíc dosud: <strong style="color:var(--green);">' + s.totalKWh.toFixed(1) + ' kWh</strong></div>';
        if (s.perDevice) {
          const sorted = Object.entries(s.perDevice).sort((a,b) => b[1] - a[1]).slice(0, 10);
          html += '<div style="font-size:11px;color:var(--purple);font-weight:600;margin-bottom:6px;">📊 Top 10 spotřebičů (kWh)</div>';
          html += '<div class="im-kv">';
          sorted.forEach(([dev, kwh]) => {
            html += '<div class="k">' + esc(dev) + '</div><div class="v" style="font-family:var(--mono);">' + Number(kwh).toFixed(2) + ' kWh</div>';
          });
          html += '</div>';
        }
      } catch(_) {
        html += '<div style="font-size:11px;color:var(--tx3);text-align:center;">sh_finance_snapshot prázdný. Jdi na FINANCE stránku a klikni "Reset baseline".</div>';
      }
    }
    else if (kind === 'house_state') {
      title = '🔑 House State — složení stavu';
      icon = '🔑';
      const state = get('sh_house_state');
      const rezim = get('sh_rezim_doma');
      const spim = get('sh_spim');
      const phase = get('sh_cast_dne');
      const scene = get('sh_scene_active');
      html = '<div style="text-align:center;padding:8px 0;margin-bottom:14px;"><span style="font-size:18px;font-weight:600;color:var(--cyan);">' + esc(state) + '</span></div>';
      html += '<div class="im-kv">' +
        '<div class="k">Režim</div><div class="v">' + esc(rezim) + '</div>' +
        '<div class="k">Fáze</div><div class="v">' + esc(phase) + '</div>' +
        '<div class="k">Spánek</div><div class="v">' + esc(spim) + '</div>' +
        '<div class="k">Scéna</div><div class="v">' + esc(scene) + '</div>' +
      '</div>';
      html += '<div style="font-size:11px;color:var(--tx3);margin-top:12px;line-height:1.5;">House state je kompozit: režim + fáze + sleep + scéna → generuje hodnoty jako "day_home", "night_sleep", "evening_relax" atd. Řídí automatizace.</div>';
    }
    else if (kind === 'visitor') {
      title = '👥 Visitor mode — detail';
      icon = '👥';
      const mode = get('sh_visitor_mode');
      const ttsBlock = get('sh_visitor_tts_block');
      const vacuumBlock = get('sh_vacuum_visitor_block');
      html = '<div class="im-kv">' +
        '<div class="k">Visitor mode</div><div class="v"><strong style="color:' + (mode === 'yes' ? 'var(--orange)' : 'var(--green)') + ';">' + esc(mode) + '</strong></div>' +
        '<div class="k">TTS blokováno</div><div class="v">' + esc(ttsBlock) + '</div>' +
        '<div class="k">Vacuum blokován</div><div class="v">' + esc(vacuumBlock) + '</div>' +
      '</div>';
      html += '<div style="font-size:11px;color:var(--tx3);margin-top:12px;line-height:1.5;">Visitor mode vypne rušivé automatizace (TTS hlášky, spuštění Giuseppe) během návštěvy. Aktivuje se manuálně přes tlačítko nebo dashboard.</div>';
    }
    else {
      html = 'Neznámý typ: ' + esc(kind);
      title = 'Home tile';
      icon = 'ℹ';
    }

    openInfoModal(title, html, { icon: icon, html: true });
  } catch(e) {
    openInfoModal('Home tile', 'Chyba: ' + e.message, { icon: '⚠' });
  }
}
"""


def patch(fp):
    if not os.path.exists(fp):
        return
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        c = f.read()
    orig = c
    is_crlf = '\r\n' in c[:4096]
    changes = []
    marker = 'PHASE12E_HOME_TILES_MODAL_APPLIED'

    for old, new in REPLACEMENTS:
        old2 = old.replace('\n','\r\n') if is_crlf else old
        new2 = new.replace('\n','\r\n') if is_crlf else new
        if old2 in c:
            c = c.replace(old2, new2, 1)
            changes.append('+ ' + old[:40] + '…')
        else:
            # Check if new already present (idempotent)
            if new2[:60] in c:
                changes.append('⏭ tile (už applied)')
            else:
                changes.append('⏭ tile (anchor missing)')

    # Inject JS helper
    if marker + ' — home tile clicks' in c:
        changes.append('⏭ JS helper (už applied)')
    else:
        idx = c.rfind('</script>')
        if idx >= 0:
            inj = JS_HELPER.replace('\n','\r\n') if is_crlf else JS_HELPER
            c = c[:idx] + inj + c[idx:]
            changes.append('+ JS helper openHomeTileModal')

    if c != orig:
        with open(fp, 'w', encoding='utf-8', newline='') as f:
            f.write(c)
        print(f'  ✅ {os.path.basename(fp)}')
    else:
        print(f'  ⏭️  {os.path.basename(fp)}')
    # Short summary of changes
    added = sum(1 for ch in changes if ch.startswith('+ '))
    skipped = sum(1 for ch in changes if ch.startswith('⏭'))
    print(f'     +{added} · skipped {skipped}')


if __name__ == '__main__':
    print('PHASE 12e — Home tile clicks → modal')
    print('='*60)
    for f in FILES:
        patch(f)
