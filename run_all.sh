#!/bin/bash
# Team Rem: full flow, mode solve to DRC
set -e
python3 modes.py
python3 gap_sweep.py
python3 -c "import json; from modes import neff; e,o=neff(1.55,gap=0.325)[:2]; m=json.load(open('modes.json')); m['supermodes_gap325_1550']=[e,o]; json.dump(m,open('modes.json','w'),indent=1)"
python3 circuits.py
python3 layout.py
python3 render.py
python3 -c "import gdsfactory as gf; gf.gpdk.PDK.activate(); gf.components.ring_single(gap=0.15, radius=10, length_x=4, cross_section='strip').write_gds('ring_bad_gap150.gds')"
python3 drc.py rem_photonics.gds ring.gds mzi.gds ring_bad_gap150.gds
