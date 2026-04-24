"""Sync 5 patches z master smart_home_v3.html do 3 variant.

Master → 1920 / 2880 / rpi.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).parent

master = (HERE / 'smart_home_v3.html').read_text(encoding='utf-8')

PATCHES = [
    # (search_anchor_in_variant, replacement_from_master_boundary_lines)
]


def extract(txt, start_anchor, end_anchor):
    i = txt.find(start_anchor)
    if i < 0: return None
    j = txt.find(end_anchor, i)
    if j < 0: return None
    return txt[i:j + len(end_anchor)]


def patch_variant(fn):
    p = HERE / fn
    txt = p.read_text(encoding='utf-8')
    changed = 0

    # Patch 1: bedroom zoneDetailData
    a = 'bedroom: {\n    title: '
    b_old = 'Motion < 3:00 → LED pásek (WC). Motion 3:00+ → 2× do 3 min = confirmed wake → rutina. Alarm → sunrise simulace (6 kroků).'
    b_new = "Motion < 3:00 → LED pásek (WC). Motion 3:00+ → 2× do 3 min = confirmed wake → rutina. Alarm → sunrise simulace (6 kroků). Odchod → zasuvka kamera ON (camera_router).'"
    # Take master version fully (from bedroom: to bathroom: {)
    m_block = extract(master, 'bedroom: {\n    title: ', "\n  bathroom: {")
    v_block = extract(txt, 'bedroom: {\n    title: ', "\n  bathroom: {")
    if m_block and v_block and v_block != m_block:
        txt = txt.replace(v_block, m_block, 1)
        changed += 1

    # Patch 2: bedroom quick actions
    m_qa = extract(master, "bedroom: [\n    ['💡 Soft ON'", "\n  ],\n  bathroom: [")
    v_qa = extract(txt, "bedroom: [\n    ['💡 Soft ON'", "\n  ],\n  bathroom: [")
    if m_qa and v_qa and v_qa != m_qa:
        txt = txt.replace(v_qa, m_qa, 1)
        changed += 1

    # Patch 3: render block with _device_cap
    m_render = extract(master, 'actions.forEach(([lbl, varName, val]) => {', 'html += \'</div></div>\';')
    v_render = extract(txt, 'actions.forEach(([lbl, varName, val]) => {', 'html += \'</div></div>\';')
    if m_render and v_render and v_render != m_render:
        txt = txt.replace(v_render, m_render, 1)
        changed += 1

    # Patch 4: pradelna zoneDetailData
    m_prad = extract(master, "pradelna: {\n    title: '🌀 Prádelna", "\n  predsin: {")
    v_prad = extract(txt, "pradelna: {\n    title: '🌀 Prádelna", "\n  predsin: {")
    if m_prad and v_prad and v_prad != m_prad:
        txt = txt.replace(v_prad, m_prad, 1)
        changed += 1

    # Patch 5: pradelna zoneConfigs
    m_cfg = extract(master, "  pradelna: [\n    { name: 'sh_cfg_power_alert'", "\n  ],\n};")
    v_cfg = extract(txt, "  pradelna: [\n    { name: 'sh_cfg_power_alert'", "\n  ],\n};")
    if m_cfg and v_cfg and v_cfg != m_cfg:
        txt = txt.replace(v_cfg, m_cfg, 1)
        changed += 1

    p.write_text(txt, encoding='utf-8')
    print(f'  [OK] {fn}: {changed} bloky sync')


for fn in ['smart_home_v3_1920.html', 'smart_home_v3_2880.html', 'smart_home_v3_rpi.html']:
    patch_variant(fn)
