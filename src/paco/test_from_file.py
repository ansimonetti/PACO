import argparse
import json
from pathlib import Path

import numpy as np

from src.paco.solver import paco
from src.utils.env import IMPACTS_NAMES

__test__ = False


def run(file_path: str, bound_value: float) -> int:
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    with path.open("r", encoding="utf-8") as handle:
        bpmn = json.load(handle)

    bpmn = {eval(k): v for k, v in bpmn.items()}
    bound = np.array([bound_value] * len(bpmn[IMPACTS_NAMES]), dtype=np.float64)
    results = paco(bpmn, bound)
    print(results)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PACO solver using a BPMN JSON file.")
    parser.add_argument("--file", default="test.json", help="Path to BPMN JSON file.")
    parser.add_argument("--bound", type=float, default=0.1, help="Scalar bound value.")
    args = parser.parse_args()
    return run(args.file, args.bound)


if __name__ == "__main__":
    raise SystemExit(main())
