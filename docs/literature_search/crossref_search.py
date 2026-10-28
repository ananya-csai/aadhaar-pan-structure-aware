"""Literature search for Section II-E (run 28 Oct 2026).

Crossref REST API, query.bibliographic, one query per combination of the three
term groups of Section II-E (4 x 4 x 4 = 64 queries), top ROWS records per
query by Crossref relevance, publication date 2015-01-01 .. 2026-10-28, record
types journal-article, proceedings-article, book-chapter, posted-content.
Writes raw.jsonl (every record returned, with the query) and records.csv
(deduplicated by DOI). No API key; polite pacing.

    python docs/literature_search/crossref_search.py
"""
import csv, itertools, json, time, urllib.parse, urllib.request
from pathlib import Path

G1 = ["Aadhaar", "PAN card", "Indian identity document", "identity document"]
G2 = ["forgery", "tampering", "verification", "OCR"]
G3 = ["checksum", "structural validation", "semantic consistency", "field consistency"]
ROWS = 40
FILTER = ("from-pub-date:2015-01-01,until-pub-date:2026-10-28,"
          "type:journal-article,type:proceedings-article,type:book-chapter,type:posted-content")
OUT = Path(__file__).resolve().parent


def fetch(q):
    url = ("https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": q, "filter": FILTER, "rows": ROWS,
         "select": "DOI,title,container-title,type,issued,abstract,publisher"}))
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)["message"]
        except Exception as e:  # noqa: BLE001
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"failed: {q}")


def main():
    raw, seen = [], {}
    for a, b, c in itertools.product(G1, G2, G3):
        q = f"{a} {b} {c}"
        msg = fetch(q)
        for it in msg["items"]:
            rec = {"query": q, "doi": it.get("DOI", "").lower(),
                   "title": " ".join(it.get("title") or [""]),
                   "venue": " ".join(it.get("container-title") or [""]),
                   "type": it.get("type", ""), "publisher": it.get("publisher", ""),
                   "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
                   "has_abstract": bool(it.get("abstract"))}
            raw.append(rec)
            seen.setdefault(rec["doi"], rec)
        time.sleep(1.0)
    with open(OUT / "raw.jsonl", "w", encoding="utf-8") as f:
        for r in raw:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(OUT / "records.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["doi", "title", "venue", "type", "publisher", "year", "has_abstract"])
        w.writeheader()
        for r in seen.values():
            w.writerow({k: r[k] for k in w.fieldnames})
    print(f"queries 64, records returned {len(raw)}, unique DOIs {len(seen)}")


if __name__ == "__main__":
    main()
