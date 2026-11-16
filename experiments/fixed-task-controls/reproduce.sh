#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p inputs
if [ ! -d inputs/ER_DELAY_PERCOLATION_1_v011 ]; then unzip -oq inputs/ER_DELAY_PERCOLATION_1_v011_CORRECTED.zip -d inputs; fi
if [ ! -d inputs/ER_CE_RECOVERABILITY_1 ]; then unzip -oq inputs/ER_CE_RECOVERABILITY_1_COMPLETE.zip -d inputs; fi
export ER_DELAY_ROOT="$PWD/inputs/ER_DELAY_PERCOLATION_1_v011"
export ER_CE_ROOT="$PWD/inputs/ER_CE_RECOVERABILITY_1"
python run_audit.py > replay_run_log.txt
python extra_controls.py > replay_extra_log.txt
python plots.py > replay_plot_log.txt
python -m pytest -q tests/ | tee replay_test_log.txt
