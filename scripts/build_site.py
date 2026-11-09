import csv, html, json, os, re
from collections import OrderedDict

BASE = "https://ranasudhir21.github.io/business-management-reference-library/"
DOI = "10.5281/zenodo.24084354"
REPO = "https://github.com/ranasudhir21/business-management-reference-library"
rows = list(csv.DictReader(open("library/catalogue.csv", encoding="utf-8-sig")))
os.makedirs("docs/clusters", exist_ok=True)
e = html.escape

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

clusters = OrderedDict()
for r in sorted(rows, key=lambda r: r["cluster_id"]):
    clusters.setdefault(r["cluster_id"], {"name": r["cluster"], "rows": []})["rows"].append(r)

CSS = """body{font-family:Georgia,'Times New Roman',serif;max-width:860px;margin:0 auto;padding:28px 18px 60px;color:#1d1d1d;line-height:1.6;background:#fff}
h1{font-size:30px;line-height:1.2;margin:0 0 10px}h2{font-size:21px;margin:34px 0 8px}a{color:#1f4e79}
p.lede{font-size:17px;color:#333}nav{font-family:Arial,sans-serif;font-size:14px;margin-bottom:22px}
ol.refs{padding-left:22px}ol.refs li{margin:0 0 14px}.meta{font-family:Arial,sans-serif;font-size:12.5px;color:#555}
ul.cl{padding-left:20px}ul.cl li{margin:4px 0}footer{margin-top:44px;border-top:1px solid #ccc;padding-top:12px;font-family:Arial,sans-serif;font-size:13px;color:#555}
code{font-size:13px}"""

def page(title, desc, body, path, ld):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}{path}"><style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head>
<body><nav><a href="{BASE}">Business Management Reference Library</a> &middot; <a href="{REPO}">GitHub and Claude skill</a> &middot; <a href="https://doi.org/{DOI}">Zenodo DOI</a></nav>
{body}
<footer>Business Management Reference Library, version 1.0.0, compiled by Sudhir Rana (Liwa University). Cite as: Rana, S. (2026). <i>Business Management Reference Library: A clustered, DOI-verified BibTeX collection</i> (Version 1.0.0) [Data set]. Zenodo. <a href="https://doi.org/{DOI}">https://doi.org/{DOI}</a>. Metadata released under CC0 1.0; the works remain under their publishers' copyright.</footer>
</body></html>"""

def ref_item(r):
    apa = e(r["apa7"])
    if r["doi"]:
        link = r["doi"] if r["doi"].startswith("http") else "https://doi.org/" + r["doi"]
        apa = apa.replace(e(link), f'<a href="{e(link)}">{e(link)}</a>')
    terms = "; ".join([t for t in r["topic_terms"].split(";") if t.strip()][:6])
    return f'<li>{apa}<div class="meta">{e(r["type"])} &middot; {e(r["collections"])}' + (f' &middot; Topics: {e(terms)}' if terms else "") + "</div></li>"

def work_ld(r):
    d = {"@type": "ScholarlyArticle" if r["type"] in ("article", "review", "editorial") else "CreativeWork",
         "name": r["title"], "datePublished": r["year"],
         "author": [{"@type": "Person", "name": a.strip()} for a in r["authors"].split(";") if a.strip()],
         "isPartOf": {"@type": "Periodical" if r["type"] in ("article", "review", "editorial") else "Book", "name": r["source"]}}
    if r["doi"]:
        d["sameAs"] = r["doi"] if r["doi"].startswith("http") else "https://doi.org/" + r["doi"]
    return d

for cid, c in clusters.items():
    rs = sorted(c["rows"], key=lambda r: (-int(r["year"] or 0), r["title"]))
    title = f"{c['name']}: business and management research papers"
    desc = f"{len(rs)} DOI-verified papers on {c['name'].lower()} for literature reviews, systematic reviews and research gap analysis, from FIIB Business Review, Review of Management Literature and related outlets."
    body = (f"<h1>{e(c['name'])}</h1><p class=\"lede\">{e(desc)} Each entry gives the full APA 7 reference with its DOI.</p>"
            f"<ol class=\"refs\">{''.join(ref_item(r) for r in rs)}</ol>")
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": desc,
          "isPartOf": {"@type": "Dataset", "name": "Business Management Reference Library", "identifier": "https://doi.org/" + DOI},
          "hasPart": [work_ld(r) for r in rs]}
    path = f"clusters/{slug(cid + '-' + c['name'])}.html"
    c["path"] = path
    open("docs/" + path, "w", encoding="utf-8").write(page(title, desc, body, path, ld))

n = len(rows)
cols = OrderedDict()
for r in rows:
    for k in r["collections"].split("; "):
        cols[k] = cols.get(k, 0) + 1
items = "".join(f'<li><a href="{c["path"]}">{e(c["name"])}</a> ({len(c["rows"])})</li>' for c in clusters.values())
recent = sorted(rows, key=lambda r: (-int(r["year"] or 0), r["title"]))[:25]
body = f"""<h1>Business Management Reference Library</h1>
<p class="lede">A curated, DOI-verified library of {n} business and management research papers, book chapters and reviews for researchers writing research papers, literature reviews and systematic literature reviews (SLRs), finding research gaps, building conceptual frameworks and hypotheses, and preparing peer reviews.</p>
<p>The library covers every article in <i>FIIB Business Review</i> (SAGE) from 2024 onward, every chapter of the Emerald book series <i>Review of Management Literature</i>, and the publications of Sudhir Rana. Collections: {', '.join(f'{e(k)} ({v})' for k, v in cols.items())}.</p>
<h2>Browse by research area</h2><ul class="cl">{items}</ul>
<h2>Use it in Claude, LaTeX or a reference manager</h2>
<p>Download the <a href="{REPO}/tree/main/skill-download">Claude skill</a> and add it in Claude under Settings, Capabilities, Skills; Claude will then search and cite the library during literature reviews and paper writing. The <a href="{REPO}/tree/main/library">BibTeX, RIS and CSV files</a> import into Overleaf, Zotero, Mendeley, EndNote and JabRef. The full release is archived on Zenodo at <a href="https://doi.org/{DOI}">https://doi.org/{DOI}</a>.</p>
<h2>Most recent additions</h2><ol class="refs">{''.join(ref_item(r) for r in recent)}</ol>"""
ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Business Management Reference Library",
      "description": f"A curated, DOI-verified bibliographic library of {n} business and management works in 14 research clusters.",
      "identifier": "https://doi.org/" + DOI, "url": BASE, "license": "https://creativecommons.org/publicdomain/zero/1.0/",
      "creator": {"@type": "Person", "name": "Sudhir Rana", "identifier": "https://orcid.org/0000-0002-9910-1930",
                  "affiliation": {"@type": "Organization", "name": "Liwa University"}},
      "keywords": ["business management", "literature review", "systematic literature review", "research gaps", "marketing",
                   "consumer behaviour", "strategic management", "FIIB Business Review", "Review of Management Literature"],
      "distribution": [{"@type": "DataDownload", "encodingFormat": "application/x-bibtex", "contentUrl": f"{REPO}/raw/main/library/business-management-master.bib"}]}
open("docs/index.html", "w", encoding="utf-8").write(page("Business Management Reference Library: DOI-verified papers for literature reviews and SLRs",
     f"{n} DOI-verified business and management papers in 14 research areas, with APA 7 references, BibTeX and a Claude skill for literature reviews, SLRs and research gap analysis.", body, "", ld))

urls = [BASE] + [BASE + c["path"] for c in clusters.values()]
open("docs/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n")
open("docs/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
open("docs/.nojekyll", "w").write("")
print("pages:", len(urls))
