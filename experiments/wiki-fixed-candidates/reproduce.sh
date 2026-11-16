#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p source_data
if [ ! -f source_data/ER_DELAY_PERCOLATION_1_v011/results/public/heldout.jsonl ]; then
  unzip -q -o source_archives/ER_DELAY_PERCOLATION_1_v011_CORRECTED.zip -d source_data
fi
python -m unittest -v test_controls.py
python acquisition_controls.py
python omitted_topology_stress.py
python - <<'PY'
import pandas as pd,json
from pathlib import Path
r=Path('results');df=pd.read_csv(r/'acquisition_control_rates.csv')
z={(float(row.availability),row.policy):int(row.identified) for row in df[df.budget==8].itertuples()}
assert [z[1.,x] for x in ('random','frozen_path','adaptive_path')]==[97,137,241],z
assert [z[.5,x] for x in ('random','frozen_path','adaptive_path')]==[62,74,106],z
assert [z[.25,x] for x in ('random','frozen_path','adaptive_path')]==[46,47,53],z
stress=json.loads((r/'omitted_topology_stress_summary.json').read_text())
assert (stress['heldout_worlds'],stress['worlds_with_hypothetical_unmodeled_shortcut'],stress['false_certificates'])==(160,38,135)
print('Clean replay: exact held-out policy counts and omitted-topology stress verified')
PY
