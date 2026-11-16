#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python code/ce_recoverability.py --output results
python code/plot_results.py --root .
python -m pytest -q tests/
