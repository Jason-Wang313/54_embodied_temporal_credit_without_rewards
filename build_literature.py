import csv
import json
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

QUERIES = [
    "robot",
    "robot learning",
    "robot control",
    "robot manipulation",
    "embodied ai",
    "embodied intelligence",
    "reinforcement learning",
    "offline reinforcement learning",
    "model-based reinforcement learning",
    "world model",
    "planning and control",
    "imitation learning",
    "temporal credit assignment",
    "credit assignment",
    "causal reasoning robotics",
    "self-supervised robot learning",
    "robot foundation models",
    "visual servoing",
    "tactile sensing robot",
    "predictive state representation",
]

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0"})

def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

def crossref_search(query, rows=100, offset=0):
    url = "https://api.crossref.org/works"
    params = {
        "query.bibliographic": query,
        "rows": rows,
        "offset": offset,
        "select": "DOI,title,author,issued,container-title,abstract,URL,type",
    }
    r = SESSION.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["message"]

records = OrderedDict()
for qi, q in enumerate(QUERIES, 1):
    seen = 0
    for page in range(10):
        try:
            msg = crossref_search(q, rows=100, offset=page * 100)
        except Exception as e:
            print(f"query_failed\t{q}\t{e}", file=sys.stderr)
            break
        items = msg.get("items", [])
        if not items:
            break
        for it in items:
            doi = (it.get("DOI") or "").lower()
            title = (it.get("title") or [""])[0]
            year = None
            issued = it.get("issued", {}).get("date-parts", [[None]])
            if issued and issued[0]:
                year = issued[0][0]
            key = doi or norm(title)
            if not key:
                continue
            records[key] = {
                "query": q,
                "title": title,
                "year": year,
                "venue": (it.get("container-title") or [""])[0],
                "doi": it.get("DOI", ""),
                "url": it.get("URL", ""),
                "type": it.get("type", ""),
                "abstract": re.sub(r"<[^>]+>", " ", it.get("abstract", "") or "").strip(),
            }
            seen += 1
        if len(items) < 100:
            break
    print(f"query_done\t{qi}/{len(QUERIES)}\t{q}\t{seen}")

rows = list(records.values())
rows.sort(key=lambda r: (-(1 if "robot" in (r["title"] or "").lower() else 0), -(r["year"] or 0), r["title"]))
out_csv = DOCS / "related_work_matrix.csv"
with out_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["bucket", "query", "title", "year", "venue", "doi", "url", "type", "abstract"])
    writer.writeheader()
    for i, r in enumerate(rows, 1):
        title_l = (r["title"] or "").lower()
        if any(k in title_l for k in ["robot", "manipulation", "embodied", "control"]):
            bucket = "robotics"
        elif any(k in title_l for k in ["reinforcement", "rl", "control"]):
            bucket = "rl"
        else:
            bucket = "adjacent"
        writer.writerow({"bucket": bucket, **r})

summary = {
    "created_at": datetime.utcnow().isoformat() + "Z",
    "queries": QUERIES,
    "unique_records": len(rows),
}
(DOCS / "literature_build_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
