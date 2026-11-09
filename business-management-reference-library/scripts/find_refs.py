#!/usr/bin/env python3
"""Search the Business Management Reference Library.

Examples
  python3 find_refs.py "consumer decision" --format apa
  python3 find_refs.py --cluster C02 --collection fiib --format keys
  python3 find_refs.py "literature review" --format bibtex > refs.bib
"""
import argparse, csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "references")

def load():
    with open(os.path.join(REF, "catalogue.csv"), encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))

def bib_entries():
    text = open(os.path.join(REF, "business-management-master.bib"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"@\w+\{([^,]+),.*?\n\}\n", text, re.S):
        out[m.group(1)] = m.group(0)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="*", help="words that must all appear in title, cluster or topic terms")
    ap.add_argument("--cluster", help="cluster id, e.g. C04")
    ap.add_argument("--collection", help="rana | fiib | rml")
    ap.add_argument("--author", help="author surname")
    ap.add_argument("--since", type=int, help="earliest year")
    ap.add_argument("--format", default="table", choices=["table", "apa", "keys", "bibtex"])
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    rows = load()
    words = [w.lower() for w in a.query]
    coll = {"rana": "Rana publications", "fiib": "FIIB Business Review", "rml": "Review of Management Literature"}
    hits = []
    for r in rows:
        hay = " ".join([r["title"], r["cluster"], r["secondary_clusters"], r["topic_terms"]]).lower()
        if words and not all(w in hay for w in words): continue
        if a.cluster and r["cluster_id"].upper() != a.cluster.upper(): continue
        if a.collection and coll.get(a.collection, a.collection) not in r["collections"]: continue
        if a.author and a.author.lower() not in (r["authors"] + r["editors"]).lower(): continue
        if a.since and int(r["year"] or 0) < a.since: continue
        hits.append(r)
    if a.limit: hits = hits[: a.limit]
    if a.format == "bibtex":
        b = bib_entries()
        sys.stdout.write("\n".join(b[r["bibtex_key"]] for r in hits if r["bibtex_key"] in b))
    elif a.format == "apa":
        for r in sorted(hits, key=lambda r: r["apa7"]): print(r["apa7"] + "\n")
    elif a.format == "keys":
        print(",".join(r["bibtex_key"] for r in hits))
    else:
        for r in hits:
            print(f'{r["bibtex_key"]:<34} {r["cluster_id"]}  {r["year"]}  {r["title"][:90]}')
    print(f"\n{len(hits)} match(es)", file=sys.stderr)

if __name__ == "__main__":
    main()
