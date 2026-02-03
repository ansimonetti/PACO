#!/bin/bash
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
export PYTHONPATH="$PYTHONPATH:$SCRIPT_DIR/src"
python src/run_benchmark.py