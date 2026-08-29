# -*- coding: utf-8 -*-
"""python -m idforge.report --out data/v1 : statistics, audits and figures."""
from __future__ import annotations

import argparse
import json
import os
import sys

from .figures import build_all
from .records import IdentityRecord
from .stats import compute, write_reports


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/v1")
    a = ap.parse_args(argv)
    rows = [json.loads(l) for l in open(os.path.join(a.out, "manifest.jsonl"))]
    recs = []
    for l in open(os.path.join(a.out, "records.jsonl"), encoding="utf-8"):
        d = json.loads(l)
        d.pop("split", None)
        recs.append(IdentityRecord(**d))
    print(f"computing statistics over {len(rows)} images ...", flush=True)
    S = compute(rows, recs, a.out)
    write_reports(S, a.out)
    print("building figures ...", flush=True)
    build_all(a.out)
    print(f"wrote {a.out}/stats/REPORT.md and {a.out}/figures/", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
