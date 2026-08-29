# -*- coding: utf-8 -*-
"""python -m idforge.probe_cli --out data/v1 : run the renderer-leakage probe."""
import argparse, json, os, sys
from .probe import run_all

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="data/v1")
ap.add_argument("--n-records", type=int, default=40)
a = ap.parse_args()
print("running renderer-leakage probe ...", flush=True)
res = run_all(a.out, a.n_records)
os.makedirs(os.path.join(a.out, "stats"), exist_ok=True)
with open(os.path.join(a.out, "stats", "renderer_probe.json"), "w") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps({k: v for k, v in res.items()
                  if k != "exact_difference_audit"}, indent=1))
print("exact audit passed:", res["exact_difference_audit"]["passed"],
      "| pixels changed outside expected region:",
      res["exact_difference_audit"]["total_pixels_changed_outside_expected_region"])
sys.exit(0)
