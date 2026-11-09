#!/usr/bin/env python3
"""Build the clustered master BibTeX library, catalogue and skill package."""
import csv, re, unicodedata, json, collections, os, datetime

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ load
recs = {}

def norm_doi(d):
    return d.strip().lower()

def add(rec, coll):
    k = norm_doi(rec["doi"])
    if k in recs:
        recs[k]["collections"].add(coll)
        return
    rec["collections"] = {coll}
    recs[k] = rec

def fmt_lf(n):
    p = n.split()
    return n if len(p) == 1 else p[-1] + ", " + " ".join(p[:-1])

def split_authors(s):
    return [a.strip() for a in s.split(";") if a.strip()]

for line in open(os.path.join(D, "me.psv"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line:
        continue
    f = line.split("|")
    assert len(f) == 15, (len(f), line[:80])
    doi, yr, typ, venue, pub, vol, iss, fp, lp, title, au, bt, ed, isbn, kw = f
    add(dict(doi=doi, year=yr, type=typ, venue=venue, publisher=pub, volume=vol, issue=iss,
             pages=(fp + ("--" + lp if lp and lp != fp else "")) if fp else "",
             title=title, authors=split_authors(au), booktitle=bt, editors=split_authors(ed),
             isbn=isbn, kw=kw, fmt="fl"), "Rana publications")

for line in open(os.path.join(D, "fiib.psv"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line:
        continue
    f = line.split("|")
    assert len(f) == 11, (len(f), line[:80])
    doi, yr, typ, vol, iss, fp, lp, title, au, topic, kw = f
    add(dict(doi=doi, year=yr, type=typ, venue="FIIB Business Review", publisher="SAGE",
             volume=vol, issue=iss, pages=(fp + ("--" + lp if lp and lp != fp else "")) if fp else "",
             title=title, authors=split_authors(au), booktitle="", editors=[], isbn="",
             kw=topic + ", " + kw, fmt="fl"), "FIIB Business Review 2024 onward")

for line in open(os.path.join(D, "rml.psv"), encoding="utf-8"):
    line = line.rstrip("\n")
    if not line:
        continue
    f = line.split("|")
    assert len(f) == 8, (len(f), line[:80])
    doi, yr, vol, bt, pages, title, au, isbn = f
    rec = dict(doi=doi, year=yr, type="book-chapter", venue="Review of Management Literature",
               publisher="Emerald Publishing Limited", volume=vol, issue="",
               pages=pages.replace("-", "--"), title=title, authors=split_authors(au),
               booktitle=bt, editors=[], isbn=isbn, kw="", fmt="lf")
    k = norm_doi(doi)
    if k in recs:  # prefer the Crossref RML metadata for RML chapters
        coll = recs[k]["collections"]
        recs[k] = rec
        rec["collections"] = coll | {"Review of Management Literature"}
    else:
        add(rec, "Review of Management Literature")

for r in recs.values():
    if r["venue"] == "Review of Management Literature":
        r["collections"].add("Review of Management Literature")

# Rana-authored items inside FIIB/RML also belong to the publications collection
for r in recs.values():
    names = " ".join(r["authors"] + r["editors"]).lower()
    if "sudhir" in names and "rana" in names:
        r["collections"].add("Rana publications")

# ------------------------------------------------------------------ print-year corrections
# Crossref print-issue year where it differs from the online-first year
YEARFIX = {
 "10.1108/ribs-07-2021-0105": "2022", "10.1108/ijoem-04-2020-0415": "2022", "10.1177/22785337211001969": "2022",
 "10.1108/bl-05-2023-0139": "2026", "10.1108/cr-04-2023-0076": "2024", "10.1108/ijoem-03-2023-0390": "2025",
 "10.1108/k-07-2022-0963": "2024", "10.1108/apjba-12-2024-0693": "2026", "10.1080/10496491.2020.1829773": "2021",
 "10.1108/ijoa-03-2020-2097": "2022", "10.1002/cb.2142": "2024", "10.1080/10696679.2023.2221442": "2024",
 "10.1108/whatt-10-2022-0122": "2023", "10.1080/15378020.2024.2430063": "2026", "10.1177/09721509211015369": "2024",
 "10.1007/s11365-024-01026-9": "2025", "10.1108/ijphm-10-2024-0104": "2026", "10.1177/23197145251407427": "2026",
 "10.1108/sajm-03-2022-0013": "2023", "10.1108/sajbs-10-2021-0375": "2023", "10.1108/srj-05-2021-0181": "2023",
 "10.1108/ijis-02-2025-0091": "2026", "10.34120/ajas.2025.1387": "2026",
 "10.1177/23197145231217550": "2026", "10.1177/23197145231216861": "2026", "10.1177/23197145231220439": "2026",
 "10.1177/23197145231224985": "2026", "10.1177/23197145241228436": "2026", "10.1177/23197145241244620": "2026",
 "10.1177/23197145241232185": "2025", "10.1177/23197145241262637": "2025", "10.1177/23197145241258835": "2026",
 "10.1177/23197145241264865": "2026", "10.1177/23197145241291853": "2025", "10.1177/23197145241288974": "2026",
 "10.1177/23197145241288403": "2025", "10.1177/23197145241304274": "2025", "10.1177/23197145251342714": "2026",
 "10.1177/23197145251356368": "2026", "10.1177/23197145251358316": "2026", "10.1177/23197145251368600": "2026",
 "10.1177/23197145251387907": "2026",
}
for k, r in recs.items():
    r["online_year"] = ""
    if k in YEARFIX and YEARFIX[k] != r["year"]:
        r["online_year"] = r["year"]
        r["year"] = YEARFIX[k]

# Volume editors of the Review of Management Literature series (Crossref book records)
RML_EDITORS = {
 "1": "Rana, Sudhir; Kathuria, Sakshi; Singh, Jagroop",
 "2": "Rana, Sudhir; Singh, Jagroop; Kathuria, Sakshi",
 "3": "Kaurav, Rahul Pratap Singh; Mishra, Vinaytosh",
 "4A": "Rana, Sudhir", "4B": "Rana, Sudhir", "5": "Rana, Sudhir",
 "6": "Dewasiri, Narayanage Jayantha; Kumar, Jitender; Singhania, Shubham; Baker, H. Kent",
}
for r in recs.values():
    if r["venue"] == "Review of Management Literature" and r["type"] == "book-chapter" and r["volume"] in RML_EDITORS:
        r["editors"] = split_authors(RML_EDITORS[r["volume"]])
        if r["fmt"] == "fl":
            r["authors"] = [fmt_lf(a) for a in r["authors"]]
            r["fmt"] = "lf"

# ------------------------------------------------------------------ clusters
CLUSTERS = [
    ("C01", "Research Methods, Literature Review and Scholarly Publishing",
     r"literature review method|review methodolog|power framework|prisma|realist synthesis|systematic literature reviews: steps|plan and write for systematic|conduct of bibliometric|technology-based bibliometric|scholarly publishing|peer review|responsible scholar|shared goals|research culture|management scholars|future of business management research|respondents|case study manuscript|industry experiences with academic|first five years|theory building in marketing|methodological trends|research methodology|conference review|research agenda for management|journal history"),
    ("C02", "Artificial Intelligence, Analytics and Digital Transformation",
     r"artificial intelligence|\bai\b|ai-|gpt|generative|machine learning|neural network|big data|analytics|business intelligence|digital transformation|digitali[sz]ation|digital twin|metaverse|industry 4\.0|industry 5\.0|robot|deep ?fake|large language model|internet of things|smart technolog|disruptive technolog|multi-agent|algorithm|digital divide|eeg|neuro"),
    ("C03", "Technology Adoption, FinTech and Blockchain",
     r"utaut|technology acceptance|adoption|m-banking|mobile banking|mobile payment|chatbot|fintech|blockchain|digital banking|robo-advisor|cloud computing|social commerce|self-service technolog|peer-to-peer lending|digital payment|digital assets|continuance intention|resistance to"),
    ("C04", "Consumer Behaviour and Decision Making",
     r"consumer|purchase|buying|shopping|nostalgia|compulsive|impulsive|luxury|consumption|consumerism|boycott|organic food|rationality|decision mak|gen y|millennial|food waste|ott apps|gratification"),
    ("C05", "Digital Marketing, Social Media and Phygital Marketing",
     r"social media|ewom|word of mouth|influencer|digital marketing|instagram|advertising|phygital|live-?stream|omnichannel|digital content|gamification|e-mail|brand engagement|storytelling|personali[sz]|online review|twitter|brand-generated|digital sources|e-commerce|paid, owned|online brand communit|metaverse marketing"),
    ("C06", "Marketing Strategy, Services and Customer Relationships",
     r"service quality|customer satisfaction|b2b|sales|marketing capabilit|market orientation|promotion|promotional|servitization|marketing leadership|customer experience|customer relationship|crm|inclusive marketing|marketing communication|brand trust|brand attachment|marketing effectiveness|customer needs|e-service|customer service|value chain|customer engagement|sdg12"),
    ("C07", "International Business, International Marketing and Emerging Markets",
     r"international|export|emerging market|globali[sz]|cross-cultural|cross-border|foreign|fdi|indo-pacific|cultural differences|global markets|internationali[sz]|global financial markets"),
    ("C08", "Strategy, Firm Performance and Organizational Capabilities",
     r"firm performance|business performance|competitive|strateg|dynamic capabilit|resource|resilience|ambidexterit|business model|organi[sz]ational success|collaborative arrangement|change management|organi[sz]ational change|dominant logic|hybrid organi|positioning|middle manager|business practices|stakeholder"),
    ("C09", "Entrepreneurship and Innovation",
     r"entrepreneur|innovation|copreneur|start-?up|creative industr|cooperative|social enterprise|social stock exchange|innovative"),
    ("C10", "Sustainability, CSR, ESG and Corporate Governance",
     r"sustainab|csr|corporate social|\besg\b|green|circular|governance|board|greenwash|integrated reporting|climate|sdg|renewable|environmental|gender diversity|anti-corruption|ethic|food waste"),
    ("C11", "Organizational Behaviour, HRM and Leadership",
     r"employee|\bwork|leadership|leader|\bhr\b|human resource|job |job$|team|organi[sz]ational behaviour|cynicism|knowledge.sharing|knowledge management|bullying|workplace|engagement|happiness|deviance|mindfulness|retention|grit|career|teaching|lmx|leader-member|stress|favouritism|humility|humour|well-being|performance orientation|trust and joy|organizational culture|non-monetary|internal communication|diversity, equity|workaholi|frontliner|me-time|gig"),
    ("C12", "Finance, Banking and Economics",
     r"financ|bank|invest|\bipo\b|stock|portfolio|dividend|m&a|capital|inflation|oil price|mutual fund|microfinance|loan|economic growth|econom|housing|forensic accounting|intangible asset|risk management|insurance|retirement|exchange rate|forex|accounting|market discipline|cash flow|tea exports|migrant"),
    ("C13", "Tourism, Hospitality and Healthcare Management",
     r"touris|hospitality|tourist|destination|medical|health|hospital|nurs|pharma|diabetes|football|homestay|heritage|travel|critical care|food delivery|fire safety|cannabis"),
    ("C14", "Operations, Supply Chain and Quality Management",
     r"supply chain|logistic|lean|kaizen|quality|manufactur|recycl|capacity planning|operations|decision sciences|interpretive structural|ism-|project failure|wastes|servitization|production service"),
]
CLABEL = {c: l for c, l, _ in CLUSTERS}

# Manual primary-cluster decisions where keyword scoring is ambiguous
OVERRIDE = {
    "10.1108/ribs-07-2021-0105": "C07",
    "10.1016/j.jbusres.2020.07.001": "C08",
    "10.1108/ijoem-04-2020-0415": "C07",
    "10.1177/22785337211001969": "C03",
    "10.1108/bij-05-2021-0257": "C08",
    "10.1108/apjba-09-2021-0483": "C10",
    "10.1108/bl-05-2023-0139": "C13",
    "10.1108/cr-04-2023-0076": "C06",
    "10.1080/10496491.2023.2216292": "C04",
    "10.1007/s11365-024-00973-7": "C02",
    "10.1108/ijoem-03-2023-0390": "C03",
    "10.1108/jkm-02-2023-0140": "C11",
    "10.1108/bfj-08-2023-0681": "C03",
    "10.1108/apjba-12-2024-0693": "C05",
    "10.1002/cb.2142": "C04",
    "10.1109/access.2024.3355977": "C04",
    "10.1108/jbim-01-2024-0007": "C05",
    "10.1016/b978-0-323-88468-6.00001-2": "C02",
    "10.1080/15378020.2024.2430063": "C04",
    "10.1007/978-3-031-88781-9_8": "C02",
    "10.1177/09721509211015369": "C11",
    "10.1504/ijtmkt.2022.123866": "C07",
    "10.1177/2319714518803440": "C07",
    "10.1108/tqm-06-2022-0203": "C14",
    "10.1080/08911762.2023.2178354": "C05",
    "10.1504/ejim.2023.130362": "C07",
    "10.1108/ijqrm-11-2021-0380": "C14",
    "10.1108/md-02-2024-0346": "C10",
    "10.1504/ijsoi.2023.137471": "C02",
    "10.1201/9781003569008": "C05",
    "10.1504/jgba.2016.074899": "C07",
    "10.1108/sajbs-10-2021-0375": "C08",
    "10.4018/979-8-3693-2849-1.ch002": "C03",
    "10.1515/9783110733716-012": "C14",
    "10.1007/978-3-031-33898-4_11": "C02",
    "10.1007/s11365-024-01026-9": "C09",
    "10.4018/979-8-3373-0219-5.ch009": "C02",
    "10.1007/s10834-024-10015-7": "C08",
    "10.1080/14724049.2025.2572985": "C13",
    "10.1080/0965254x.2025.2605721": "C02",
    "10.1108/ijoa-01-2025-5199": "C03",
    "10.1080/0144929x.2026.2641606": "C02",
    "10.1177/2319714519839802": "C02",
    "10.1177/2319714518818231": "C08",
    "10.4324/9781003315568": "C14",
    "10.1007/978-3-031-36589-8_3": "C05",
    "10.4324/9781003315582": "C07",
    "10.4324/9781003315582-1": "C07",
    "10.4324/9781003199168": "C07",
    "10.4324/9781003199168-1": "C07",
    "10.1504/ijtlid.2024.137485": "C06",
    "10.1504/ijsoi.2024.143148": "C03",
    "10.1007/978-3-031-70219-8_1": "C07",
    "10.4337/9781035301348.00020": "C02",
    "10.34120/ajas.2025.1387": "C02",
    "10.1016/j.techfore.2026.124659": "C03",
    "10.1177/23197145211025965": "C04",
    "10.1177/2319714520933970": "C12",
    "10.1177/2278682117713579": "C05",
    "nodoi-2017-jibe": "C07",
    "10.1504/ijicbm.2020.109336": "C06",
    "10.1504/ijims.2023.132761": "C14",
    "10.1177/09722629231216822": "C04",
    "10.1201/9780429280818-4": "C07",
    "10.17010/pijom/2023/v16i3/172749": "C14",
    "10.1177/23197145231161408": "C01",
    "10.1177/2319714519854232": "C10",
    "10.1108/sajm-03-2021-071": "C01",
    "10.1177/23197145211062431": "C04",
    "10.1177/23197145221083730": "C09",
    "10.1177/23197145221105158": "C12",
    "10.1108/sajm-10-2022-141": "C02",
    "10.1177/23197145211044528": "C02",
    "10.1108/sajm-04-2022-118": "C01",
    "10.1177/23197145251379928": "C01",
    "10.1177/2319714520981455": "C12",
    "10.1177/2319714518804086": "C08",
    "10.1177/2319714519876135": "C10",
    "10.1177/2319714519893529": "C06",
    "10.1177/2319714520914500": "C11",
    "10.2139/ssrn.4263844": "C03",
    "nodoi-2008-csr": "C10",
    "nodoi-2013-transport": "C07",
    "nodoi-2015-state": "C07",
    "nodoi-2015-topics": "C07",
    "nodoi-2012-ejbm": "C07",
    "nodoi-2019-kulim": "C09",
    "10.1007/978-3-031-36589-8_8": "C05",
    "10.4135/9781071926888": "C08",
    "10.4018/979-8-3693-5298-4.ch015": "C05",
    "10.4324/9781003514114-4": "C12",
    "10.1016/j.procs.2025.03.200": "C13",
    "10.1108/ijphm-10-2024-0104": "C13",
    "10.2174/9789815324068125010002": "C10",
    "10.21315/aamj2025.30.2.1": "C05",
    "10.4324/9781003655282-10": "C13",
    "10.1108/jbsed-05-2025-0135": "C05",
    "10.3390/logistics10050112": "C14",
    "10.1108/bfj-02-2025-0236": "C06",
    "10.1002/jsc.70112": "C11",
    "10.1504/ijbis.2026.155648": "C03",
    "10.1007/978-981-92-1780-9": "C02",
    "10.1108/imr-03-2025-0148": "C07",
    "10.1108/sajm-03-2022-0013": "C03",
    "10.1080/10696679.2023.2221442": "C04",
    "10.1108/whatt-10-2022-0122": "C13",
    "10.1108/srj-05-2021-0181": "C10",
    "10.1108/jhom-04-2024-0142": "C13",
    "10.1080/0965254x.2024.2318216": "C02",
    "10.1177/2319714520958216": "C07",
    "10.1177/23197145211006218": "C08",
    "10.1177/23197145221140634": "C01",
    "10.1177/23197145221117851": "C01",
    "10.1177/23197145241247591": "C01",
    "10.1177/23197145241247869": "C01",
    "10.1177/23197145251407427": "C01",
    "10.29368/fiib.6.1.2017.28-30": "C01",
    "10.1080/00208825.2023.2257537": "C10",
    "10.1007/s13198-024-02520-7": "C07",
    "10.1111/ijcs.70163": "C04",
    "10.1108/s1474-797920140000025009": "C07",
    "10.1108/ijoem-09-2019-0742": "C07",
    "10.1108/ribs-03-2020-0021": "C07",
    "10.1177/0972262918821228": "C06",
    "10.1108/ijoa-03-2020-2097": "C04",
    "10.1080/10496491.2020.1829773": "C04",
    "10.1108/k-07-2022-0963": "C10",
    # FIIB
    "10.1177/23197145231222774": "C02",
    "10.1177/23197145231225335": "C10",
    "10.1177/23197145241227757": "C03",
    "10.1177/23197145241229915": "C05",
    "10.1177/23197145241269203": "C10",
    "10.1177/23197145241305678": "C09",
    "10.1177/23197145241281033": "C05",
    "10.1177/23197145241247704": "C02",
    "10.1177/23197145231220428": "C10",
    "10.1177/23197145241271467": "C09",
    "10.1177/23197145241306831": "C05",
    "10.1177/23197145261416212": "C03",
    "10.1177/23197145241288403": "C09",
    "10.1177/23197145231216861": "C08",
    "10.1177/23197145241304274": "C08",
    "10.1177/23197145231223058": "C03",
    "10.1177/23197145231225570": "C06",
    "10.1177/23197145241241956": "C06",
    "10.1177/23197145241280491": "C13",
    "10.1177/23197145241284080": "C04",
    "10.1177/23197145241300899": "C12",
    "10.1177/23197145251315540": "C12",
    "10.1177/23197145241297426": "C13",
    "10.1177/23197145241305685": "C11",
    "10.1177/23197145251324785": "C04",
    "10.1177/23197145251342714": "C02",
    "10.1177/23197145251387906": "C11",
    "10.1177/23197145231220439": "C11",
    "10.1177/23197145241241959": "C13",
    "10.1177/23197145241313486": "C11",
    "10.1177/23197145251313833": "C09",
    "10.1177/23197145241244620": "C12",
    "10.1177/23197145251317576": "C05",
    "10.1177/23197145251368600": "C11",
    "10.1177/23197145251333102": "C11",
    "10.1177/23197145261417114": "C14",
    "10.1177/23197145261425820": "C02",
    "10.1177/23197145261445551": "C05",
    "10.1177/23197145231217384": "C09",
    "10.1177/23197145231224985": "C11",
    "10.1177/23197145251330150": "C06",
    "10.1177/23197145231214433": "C14",
    "10.1177/23197145241244596": "C11",
    "10.1177/23197145241291407": "C06",
    "10.1177/23197145251343708": "C05",
    "10.1177/23197145241228436": "C12",
    "10.1177/23197145241262637": "C12",
    "10.1177/23197145241264865": "C08",
    "10.1177/23197145251323392": "C01",
    "10.1177/23197145251346630": "C10",
    "10.1177/23197145251347733": "C10",
    "10.1177/23197145251345235": "C14",
    "10.1177/23197145251346629": "C02",
    "10.1177/23197145251363947": "C12",
    "10.1177/23197145251370854": "C08",
    "10.1177/23197145251392697": "C12",
    "10.1177/23197145251404251": "C04",
    "10.1177/23197145261416246": "C13",
    "10.1177/23197145261421705": "C10",
    "10.1177/23197145261426043": "C11",
    "10.1177/23197145261461659": "C04",
    "10.1177/23197145231217550": "C07",
    "10.1177/23197145231210343": "C12",
    "10.1177/23197145241237000": "C13",
    "10.1177/23197145251324542": "C09",
    "10.1177/23197145251356368": "C09",
    "10.1177/23197145241276898": "C05",
    "10.1177/30499240251356878": "C11",
    "10.1177/23197145241291853": "C10",
    "10.1177/23197145261420493": "C11",
    "10.1177/23197145261466982": "C11",
    "10.1177/23197145241232185": "C14",
    "10.1177/23197145241258835": "C07",
    "10.1177/23197145251324541": "C01",
    "10.1177/23197145251339781": "C13",
    "10.1177/23197145251358316": "C04",
    "10.1177/23197145251368628": "C09",
    "10.1177/23197145251387907": "C08",
    "10.1177/23197145251404250": "C08",
    "10.1177/23197145251406429": "C03",
    "10.1177/23197145261416250": "C09",
    "10.1177/23197145261416244": "C08",
    "10.1177/23197145261426224": "C05",
    "10.1177/23197145261433417": "C04",
    "10.1177/23197145261447154": "C07",
    "10.1177/23197145261450023": "C08",
    "10.1177/23197145261451945": "C03",
    "10.1177/23197145261457716": "C04",
    "10.1177/23197145261462389": "C04",
    "10.1177/23197145261466523": "C10",
    "10.1177/23197145261471671": "C09",
    "10.1177/23197145261475534": "C09",
    "10.1177/23197145261451137": "C05",
    "10.1177/23197145261468827": "C02",
    "10.1177/23197145261480908": "C10",
    "10.1177/23197145261478789": "C12",
    "10.1177/23197145261485384": "C02",
    "10.1177/23197145261488500": "C10",
    "10.1177/23197145261486657": "C11",
    "10.1177/23197145261486648": "C03",
    "10.1177/23197145261491421": "C13",
    "10.1177/23197145261488273": "C11",
    "10.1177/23197145251365723": "C12",
    "10.1177/23197145251414575": "C12",
    "10.1177/23197145251414289": "C12",
    "10.1177/23197145261421703": "C12",
    "10.1177/23197145261425110": "C12",
    "10.1177/23197145261433126": "C12",
    "10.1177/23197145241288974": "C12",
    "10.1177/23197145241279670": "C12",
    "10.1177/23197145241301934": "C12",
    "10.1177/23197145241306838": "C10",
    "10.1177/23197145251376409": "C12",
    "10.1177/23197145261425108": "C11",
    # RML
    "10.1108/s2754-586520220000001001": "C01",
    "10.1108/s2754-586520230000002001": "C01",
    "10.1108/s2754-586520220000001002": "C03",
    "10.1108/s2754-586520220000001003": "C02",
    "10.1108/s2754-586520220000001004": "C04",
    "10.1108/s2754-586520220000001005": "C03",
    "10.1108/s2754-586520220000001006": "C12",
    "10.1108/s2754-586520220000001007": "C05",
    "10.1108/s2754-586520220000001009": "C14",
    "10.1108/s2754-586520220000001010": "C10",
    "10.1108/s2754-586520220000001011": "C14",
    "10.1108/s2754-586520220000001012": "C09",
    "10.1108/s2754-586520220000001013": "C12",
    "10.1108/s2754-586520240000003001": "C08",
    "10.1108/s2754-586520240000003002": "C08",
    "10.1108/s2754-586520240000003003": "C13",
    "10.1108/s2754-586520240000003004": "C05",
    "10.1108/s2754-586520240000003005": "C02",
    "10.1108/s2754-586520240000003006": "C05",
    "10.1108/s2754-586520240000003007": "C03",
    "10.1108/s2754-586520240000003008": "C13",
    "10.1108/s2754-586520240000003009": "C09",
    "10.1108/s2754-586520240000003010": "C02",
    "10.1108/s2754-586520240000003011": "C11",
    "10.1108/s2754-586520240000003012": "C08",
    "10.1108/s2754-586520240000003013": "C02",
    "10.1108/s2754-586520240000003014": "C05",
    "10.1108/s2754-58652025000004a002": "C11",
    "10.1108/s2754-58652025000004a003": "C11",
    "10.1108/s2754-58652025000004a004": "C11",
    "10.1108/s2754-58652025000004a005": "C11",
    "10.1108/s2754-58652025000004a006": "C11",
    "10.1108/s2754-58652025000004a007": "C11",
    "10.1108/s2754-58652025000004b001": "C02",
    "10.1108/s2754-58652025000004b002": "C02",
    "10.1108/s2754-58652025000004b003": "C14",
    "10.1108/s2754-58652025000004b004": "C10",
    "10.1108/s2754-58652025000004b005": "C12",
    "10.1108/s2754-58652025000004b006": "C11",
    "10.1108/s2754-58652025000004b007": "C02",
    "10.1108/s2754-586520260000005001": "C03",
    "10.1108/s2754-586520260000005002": "C13",
    "10.1108/s2754-586520260000005003": "C04",
    "10.1108/s2754-586520260000005004": "C06",
    "10.1108/s2754-586520260000005005": "C13",
    "10.1108/s2754-586520260000005006": "C02",
    "10.1108/s2754-586520260000005007": "C04",
    "10.1108/s2754-586520260000005008": "C10",
    "10.1108/s2754-586520260000005009": "C09",
    "10.1108/s2754-586520260000005010": "C08",
    "10.1108/s2754-586520260000005011": "C03",
    "10.1108/s2754-586520260000005012": "C04",
    "10.1108/s2754-586520260000005013": "C06",
    "10.1108/s2754-586520260000005014": "C10",
    "10.1108/s2754-586520260000006001": "C12",
    "10.1108/s2754-586520260000006002": "C12",
    "10.1108/s2754-586520260000006003": "C12",
    "10.1108/s2754-586520260000006004": "C12",
    "10.1108/s2754-586520260000006005": "C10",
    "10.1108/s2754-586520260000006006": "C12",
    "10.1108/s2754-586520260000006007": "C12",
    "10.1108/s2754-586520260000006008": "C12",
    "10.1108/s2754-586520260000006009": "C10",
    "10.1108/s2754-586520260000006010": "C12",
    "10.1108/s2754-586520260000006011": "C12",
    "10.1108/s2754-586520260000006012": "C10",
}
OVERRIDE.update({
    "10.1080/21568316.2026.2698868": "C13", "10.1108/ijis-02-2025-0091": "C09",
    "10.1108/s2754-5865202301": "C01", "10.1108/s2754-5865202402": "C01", "10.1108/978-1-83708-756-3": "C11",
    "10.1108/978-1-83708-752-5": "C02", "10.1108/978-1-80592-677-1": "C01", "10.1007/978-3-032-06099-0": "C08",
    "10.1108/9781836080688": "C02", "10.4018/979-8-3373-0209-6": "C12", "10.1201/9780429280818": "C08",
    "10.1177/2319714518798860": "C01", "10.1177/2319714518773835": "C01", "nodoi-2025-deepfake": "C02",
    "nodoi-2024-impulse": "C05", "nodoi-2024-ocb": "C11", "nodoi-2021-ijtm": "C05", "nodoi-2016-insurance": "C12",
    "nodoi-2016-sajm": "C08", "nodoi-2014-iel": "C07",
})
# RML method chapters
for d in ["10.1108/s2754-5865202300000020%02d" % i for i in range(2, 9)]:
    OVERRIDE[d] = "C01"

def scores(r):
    text_t = r["title"].lower()
    text_k = (r["kw"] + " " + r["booktitle"]).lower()
    s = {}
    for c, _, pat in CLUSTERS:
        v = 2 * len(re.findall(pat, text_t)) + len(re.findall(pat, text_k))
        if v:
            s[c] = v
    return s

for k, r in recs.items():
    s = scores(r)
    auto = max(s, key=lambda c: (s[c], -int(c[1:]))) if s else "C08"
    r["auto"] = auto
    r["cluster"] = OVERRIDE.get(k, auto)
    sec = sorted([c for c, v in s.items() if v >= 2 and c != r["cluster"]],
                 key=lambda c: -s[c])[:2]
    r["secondary"] = sec

missing_override = [k for k in recs if k not in OVERRIDE]

# ------------------------------------------------------------------ bibtex
def ascii_fold(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).encode("ascii", "ignore").decode()

COMPOUND = ["Dal Mas", "Jiménez Partearroyo", "Adá Lameiras", "Pérez-Bustamante Yábar",
            "Díaz Garrido", "Morais Lopes", "Ben Hamad", "Abd. Rahman", "Abd Rahman",
            "Abdul Hamid", "Abdul Lathief", "Das Chakladar", "Al Qaydi", "Al Abri", "Al Makdami",
            "Bin Osman", "Hack-Polay", "Singh Kaurav"]

def esc(s):
    s = s.replace("&amp;", "&")
    s = s.replace("\\", "\\textbackslash{}")
    for a, b in [("&", "\\&"), ("%", "\\%"), ("#", "\\#"), ("_", "\\_"), ("$", "\\$")]:
        s = s.replace(a, b)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "--").replace("—", "--")
    return s

PROPER = ["United Arab Emirates", "Indian Railways", "European Union", "South Asian", "South Asia", "Sri Lanka",
          "Lean Six Sigma", "Six Sigma", "Laal Singh Chaddha", "Mad Flavours", "Yair Aharoni", "Kulim",
          "India", "Indian", "Emirati", "Australian", "Egypt", "Jordan", "Lebanon", "Saudi", "Malaysian", "Malaysia",
          "Africa", "African", "Turkey", "Russia", "Russian", "China", "Chinese", "Bangladeshi", "Kazakhstani", "Indo-Pacific",
          "Asia-Pacific", "Asian", "McDonald's", "Zara", "Twitter", "Instagram", "X.com", "Deweyan", "Dewey", "Schwartz's",
          "Gioia", "Leximancer", "Bitcoin", "MasterCard", "Tencent", "Kaizen", "Boomers", "Millennials", "Gen", "Alpha",
          "Bopchain", "Bottom of the Pyramid", "COVID-19", "COVID", "Industry", "Internet of Things", "Delphi", "Hi-tech Park",
          "Gulf", "Arab", "Dubai", "Abu Dhabi", "Middle East", "Western", "Global South"]

def protect_title(t):
    t = esc(t)
    pat = "|".join(re.escape(p) for p in sorted(PROPER, key=len, reverse=True))
    t = re.sub(r"(?<![\w{])(" + pat + r")(?![\w}])", lambda m: "\x00" + m.group(1) + "\x01", t)
    def rep(m):
        w = m.group(0)
        if sum(1 for ch in w if ch.isupper()) >= 2 or re.match(r"^[A-Z]\d", w):
            return "{" + w + "}"
        return w
    parts = re.split(r"(\x00[^\x01]*\x01)", t)
    out = []
    for p in parts:
        if p.startswith("\x00"):
            out.append("{" + p[1:-1] + "}")
        else:
            out.append(re.sub(r"[A-Za-z][A-Za-z0-9\.\-]*[A-Za-z0-9]", rep, p))
    return "".join(out)

ACC = {"\u0301": "'", "\u0300": "`", "\u0302": "^", "\u0308": '"', "\u0303": "~",
       "\u0304": "=", "\u0307": ".", "\u030b": "H", "\u030c": "v", "\u0306": "u", "\u0327": "c", "\u0328": "k"}
SPECIAL = {"ı": "{\\i}", "ł": "{\\l}", "Ł": "{\\L}", "ø": "{\\o}", "Ø": "{\\O}", "ß": "{\\ss}", "æ": "{\\ae}"}

def latexify(s):
    out = []
    for ch in s:
        if ord(ch) < 128:
            out.append(ch); continue
        if ch in SPECIAL:
            out.append(SPECIAL[ch]); continue
        d = unicodedata.normalize("NFD", ch)
        base, marks = d[0], d[1:]
        if len(marks) == 1 and marks in ACC and ord(base) < 128:
            a = ACC[marks]
            b = "\\i" if base == "i" and a in "'`^\"~=" else base
            out.append("{\\" + a + ("{" + b + "}" if a.isalpha() else b) + "}")
        else:
            out.append("{" + ch + "}")
    return "".join(out)

def fmt_name(n, fmt):
    return latexify(_fmt_name(n, fmt))

def _fmt_name(n, fmt):
    n = n.strip()
    if fmt == "lf":
        if "," in n:
            last, first = [x.strip() for x in n.split(",", 1)]
            if not first:
                return "{" + esc(last) + "}"
            if " " in last:
                last = "{" + last + "}"
            return esc(last) + ", " + esc(first)
        return "{" + esc(n) + "}"
    # first-last
    for c in COMPOUND:
        if n.endswith(" " + c) or n == c:
            first = n[: -len(c)].strip()
            return "{" + esc(c) + "}" + (", " + esc(first) if first else "")
    parts = n.split()
    if len(parts) == 1:
        return "{" + esc(n) + "}"
    return esc(parts[-1]) + ", " + esc(" ".join(parts[:-1]))

def family(n, fmt):
    f = _fmt_name(n, fmt)
    return f.split(",")[0].strip("{}")

STOP = set("a an the of on in for and to with from by at as is are does do how what why when which who toward towards through using between into beyond".split())

used = collections.Counter()
def make_key(r):
    names = r["authors"] or r["editors"]
    fam = family(names[0], r["fmt"]) if names else "anon"
    fam = re.sub(r"[^A-Za-z]", "", ascii_fold(fam)) or "anon"
    words = [w for w in re.findall(r"[A-Za-z0-9]+", ascii_fold(r["title"])) if w.lower() not in STOP]
    tw = (words[0] if words else "x").lower()
    base = f"{fam}{r['year']}{tw}"
    used[base] += 1
    return base if used[base] == 1 else base + "abcdefghijklmnop"[used[base] - 1]

def sort_key(r):
    return (r["cluster"], -int(r["year"] or 0), r["title"].lower())

ordered = sorted(recs.values(), key=sort_key)
for r in ordered:
    r["key"] = make_key(r)

COLL_TAG = {"Rana publications": "rana-publications",
            "FIIB Business Review 2024 onward": "fiib-2024-onward",
            "Review of Management Literature": "review-of-management-literature"}

def entry(r):
    f = collections.OrderedDict()
    t = r["type"]
    is_doi = not r["doi"].lower().startswith("nodoi")
    names = " and ".join(fmt_name(a, r["fmt"]) for a in r["authors"])
    eds = " and ".join(fmt_name(a, r["fmt"]) for a in r["editors"])
    note = []
    if t in ("article", "editorial", "review"):
        etype = "article"
        f["author"] = names
        f["title"] = protect_title(r["title"])
        f["journal"] = esc(r["venue"])
        f["year"] = r["year"]
        if r["volume"]: f["volume"] = r["volume"]
        if r["issue"]: f["number"] = r["issue"]
        if r["pages"]: f["pages"] = r["pages"]
        if r["publisher"]: f["publisher"] = esc({"Emerald": "Emerald Publishing Limited", "SAGE": "SAGE Publications", "Elsevier": "Elsevier", "Wiley": "Wiley", "Springer": "Springer"}.get(r["publisher"], r["publisher"]))
        if r["venue"] == "FIIB Business Review":
            f["issn"] = "2319-7145"
        if t == "editorial": note.append("Editorial")
        if t == "review": note.append("Review article")
        if not r["volume"] and is_doi: note.append("Online first; check volume, issue and pages before citing")
    elif t == "book-chapter":
        etype = "incollection"
        f["author"] = names
        f["title"] = protect_title(r["title"])
        f["booktitle"] = protect_title(r["booktitle"] or r["venue"])
        if eds: f["editor"] = eds
        if r["venue"] == "Review of Management Literature":
            f["series"] = "Review of Management Literature"
            f["volume"] = r["volume"]
        elif r["venue"] and r["venue"] not in (r["publisher"], r["booktitle"]) and r["booktitle"]:
            f["series"] = esc(r["venue"])
            if r["volume"]: f["volume"] = r["volume"]
        f["publisher"] = esc({"Emerald": "Emerald Publishing Limited"}.get(r["publisher"], r["publisher"]))
        if r["venue"] == "Review of Management Literature":
            f["address"] = "Leeds"
        f["year"] = r["year"]
        if r["pages"]: f["pages"] = r["pages"]
        if r["isbn"]: f["isbn"] = r["isbn"]
    elif t == "book":
        etype = "book"
        f["editor"] = names
        f["title"] = protect_title(r["title"])
        if r["venue"] and r["venue"] not in ("Routledge India", "Apple Academic Press", "CRC Press", "Emerald Publishing Limited"):
            f["series"] = esc(r["venue"])
        if r["volume"]: f["volume"] = r["volume"]
        f["publisher"] = esc({"Routledge": "Routledge"}.get(r["publisher"], r["publisher"]))
        if r["venue"] == "Review of Management Literature": f["address"] = "Leeds"
        f["year"] = r["year"]
        if r["isbn"]: f["isbn"] = r["isbn"]
        note.append("Edited volume")
    else:
        etype = "misc"
        f["author"] = names
        f["title"] = protect_title(r["title"])
        f["year"] = r["year"]
        if t == "preprint": f["howpublished"] = "SSRN Electronic Journal (preprint)"
        elif t == "case": f["howpublished"] = "SAGE Business Cases Originals"; f["publisher"] = "SAGE Publications"
        elif r["venue"]: f["howpublished"] = esc(r["venue"])
        if not is_doi: note.append("Metadata incomplete in public indexes; verify source details before citing")
    if not is_doi and etype != "misc":
        note.append("No DOI; metadata from Google Scholar profile, verify source details before citing")
    if r.get("online_year"):
        note.append("First published online " + r["online_year"])
    if is_doi:
        f["doi"] = r["doi"]
        f["url"] = "https://doi.org/" + r["doi"]
    kws = [CLABEL[r["cluster"]]] + [CLABEL[c] for c in r["secondary"]]
    kws += [COLL_TAG[c] for c in sorted(r["collections"])]
    f["keywords"] = esc("; ".join(kws))
    if note: f["note"] = "; ".join(note)
    body = ",\n".join(f"  {k:<10}= {{{v}}}" for k, v in f.items() if v)
    return f"@{etype}{{{r['key']},\n{body}\n}}\n"

stamp = datetime.date.today().isoformat()
HEADER = f"""% ==========================================================================
% Business Management Reference Library: master BibTeX file
% Compiled {stamp}
%
% Collections
%   (1) Journal papers, book chapters, edited books and editorials by
%       Sudhir Rana (ORCID 0000-0002-9910-1930)
%   (2) Articles and editorials published in FIIB Business Review
%       (SAGE, ISSN 2319-7145) from January 2024 onward
%   (3) All chapters published in the Review of Management Literature
%       book series (Emerald, ISSN 2754-5865), volumes 1 to 6
%
% Sources: OpenAlex and Crossref metadata retrieved by DOI. Every DOI entry
% resolves at https://doi.org/. Entries without a DOI are flagged in `note`.
% Each entry carries a primary thematic cluster (first item in `keywords`),
% up to two secondary clusters, and its collection tag(s).
% Licence for this metadata compilation: CC0 1.0.
% ==========================================================================

"""

counts = collections.Counter(r["cluster"] for r in ordered)
parts = [HEADER]
for c, label, _ in CLUSTERS:
    items = [r for r in ordered if r["cluster"] == c]
    if not items:
        continue
    parts.append(f"% --------------------------------------------------------------------------\n% {c}  {label}  ({len(items)} entries)\n% --------------------------------------------------------------------------\n\n")
    for r in items:
        parts.append(entry(r) + "\n")
bib = "".join(parts)
open(os.path.join(OUT, "business-management-master.bib"), "w", encoding="utf-8").write(bib)

# collection-specific bibs
for coll, tag in COLL_TAG.items():
    sub = [r for r in ordered if coll in r["collections"]]
    open(os.path.join(OUT, f"{tag}.bib"), "w", encoding="utf-8").write(
        HEADER.replace("master BibTeX file", f"{coll} subset") + "".join(entry(r) + "\n" for r in sub))

# ------------------------------------------------------------------ RIS
def ris(r):
    t = r["type"]
    ty = {"article": "JOUR", "editorial": "JOUR", "review": "JOUR", "book-chapter": "CHAP", "book": "EDBOOK"}.get(t, "GEN")
    L = [f"TY  - {ty}"]
    for a in (r["authors"] if t != "book" else []):
        L.append("AU  - " + _fmt_name(a, r["fmt"]).replace("{", "").replace("}", "").replace("\\&", "&"))
    for a in (r["authors"] if t == "book" else r["editors"]):
        L.append("ED  - " + _fmt_name(a, r["fmt"]).replace("{", "").replace("}", ""))
    L.append("TI  - " + r["title"].replace("&amp;", "&"))
    if t in ("article", "editorial", "review"):
        L.append("JO  - " + r["venue"])
    elif t == "book-chapter":
        L.append("T2  - " + (r["booktitle"] or r["venue"]))
        if r["venue"] == "Review of Management Literature":
            L.append("T3  - Review of Management Literature")
    L.append("PY  - " + r["year"])
    if r["volume"]: L.append("VL  - " + r["volume"])
    if r["issue"]: L.append("IS  - " + r["issue"])
    if r["pages"]:
        p = r["pages"].split("--")
        L.append("SP  - " + p[0])
        if len(p) > 1: L.append("EP  - " + p[1])
    if r["publisher"]: L.append("PB  - " + r["publisher"])
    if r["isbn"]: L.append("SN  - " + r["isbn"])
    if not r["doi"].lower().startswith("nodoi"):
        L.append("DO  - " + r["doi"])
        L.append("UR  - https://doi.org/" + r["doi"])
    L.append("KW  - " + CLABEL[r["cluster"]])
    for c in r["secondary"]:
        L.append("KW  - " + CLABEL[c])
    for c in sorted(r["collections"]):
        L.append("KW  - " + COLL_TAG[c])
    L.append("ER  - ")
    return "\n".join(L)

open(os.path.join(OUT, "business-management-master.ris"), "w", encoding="utf-8").write(
    "\n\n".join(ris(r) for r in ordered) + "\n")

# ------------------------------------------------------------------ catalogue
def apa_auth(r):
    names = r["authors"]
    out = []
    for a in names:
        f = _fmt_name(a, r["fmt"]).replace("{", "").replace("}", "").replace("\\&", "&")
        if "," in f:
            last, first = [x.strip() for x in f.split(",", 1)]
            ini = " ".join(p[0] + "." for p in re.split(r"[\s\-]+", first) if p and p[0].isalpha())
            out.append(f"{last}, {ini}")
        else:
            out.append(f)
    if not out:
        return ""
    if len(out) == 1:
        return out[0]
    if len(out) <= 20:
        return ", ".join(out[:-1]) + ", & " + out[-1]
    return ", ".join(out[:19]) + ", ... " + out[-1]

def apa(r):
    a = apa_auth(r)
    t = r["title"].replace("&amp;", "&")
    doi = "" if r["doi"].lower().startswith("nodoi") else f" https://doi.org/{r['doi']}"
    typ = r["type"]
    if typ in ("article", "editorial", "review"):
        vi = r["volume"] + (f"({r['issue']})" if r["issue"] else "")
        pg = r["pages"].replace("--", "–")
        tail = ", ".join(x for x in [r["venue"], vi, pg] if x)
        return f"{a} ({r['year']}). {t}. {tail}.{doi}"
    if typ == "book-chapter":
        bt = r["booktitle"] or r["venue"]
        ser = f" ({r['venue']}, Vol. {r['volume']})" if r["venue"] == "Review of Management Literature" else ""
        pg = f" (pp. {r['pages'].replace('--', '–')})" if r["pages"] else ""
        return f"{a} ({r['year']}). {t}. In {bt}{ser}{pg}. {r['publisher']}.{doi}"
    if typ == "book":
        return f"{a} (Eds.). ({r['year']}). {t}. {r['publisher']}.{doi}"
    return f"{a} ({r['year']}). {t}.{doi}"

rows = []
for r in ordered:
    rows.append({
        "bibtex_key": r["key"], "cluster_id": r["cluster"], "cluster": CLABEL[r["cluster"]],
        "secondary_clusters": "; ".join(CLABEL[c] for c in r["secondary"]),
        "collections": "; ".join(sorted(r["collections"])), "year": r["year"],
        "type": r["type"], "title": r["title"].replace("&amp;", "&"),
        "authors": "; ".join(r["authors"]) if r["type"] != "book" else "",
        "editors": "; ".join(r["authors"] if r["type"] == "book" else r["editors"]),
        "source": r["venue"] if r["type"] != "book-chapter" else (r["booktitle"] or r["venue"]),
        "series": r["venue"] if r["type"] == "book-chapter" else "",
        "volume": r["volume"], "issue": r["issue"], "pages": r["pages"].replace("--", "-"),
        "publisher": r["publisher"],
        "doi": "" if r["doi"].lower().startswith("nodoi") else r["doi"],
        "topic_terms": r["kw"], "apa7": apa(r)})
with open(os.path.join(OUT, "catalogue.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
json.dump(rows, open(os.path.join(OUT, "catalogue.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ print-year corrections
# Crossref print-issue year where it differs from the online-first year
YEARFIX = {
 "10.1108/ribs-07-2021-0105": "2022", "10.1108/ijoem-04-2020-0415": "2022", "10.1177/22785337211001969": "2022",
 "10.1108/bl-05-2023-0139": "2026", "10.1108/cr-04-2023-0076": "2024", "10.1108/ijoem-03-2023-0390": "2025",
 "10.1108/k-07-2022-0963": "2024", "10.1108/apjba-12-2024-0693": "2026", "10.1080/10496491.2020.1829773": "2021",
 "10.1108/ijoa-03-2020-2097": "2022", "10.1002/cb.2142": "2024", "10.1080/10696679.2023.2221442": "2024",
 "10.1108/whatt-10-2022-0122": "2023", "10.1080/15378020.2024.2430063": "2026", "10.1177/09721509211015369": "2024",
 "10.1007/s11365-024-01026-9": "2025", "10.1108/ijphm-10-2024-0104": "2026", "10.1177/23197145251407427": "2026",
 "10.1108/sajm-03-2022-0013": "2023", "10.1108/sajbs-10-2021-0375": "2023", "10.1108/srj-05-2021-0181": "2023",
 "10.1108/ijis-02-2025-0091": "2026", "10.34120/ajas.2025.1387": "2026",
 "10.1177/23197145231217550": "2026", "10.1177/23197145231216861": "2026", "10.1177/23197145231220439": "2026",
 "10.1177/23197145231224985": "2026", "10.1177/23197145241228436": "2026", "10.1177/23197145241244620": "2026",
 "10.1177/23197145241232185": "2025", "10.1177/23197145241262637": "2025", "10.1177/23197145241258835": "2026",
 "10.1177/23197145241264865": "2026", "10.1177/23197145241291853": "2025", "10.1177/23197145241288974": "2026",
 "10.1177/23197145241288403": "2025", "10.1177/23197145241304274": "2025", "10.1177/23197145251342714": "2026",
 "10.1177/23197145251356368": "2026", "10.1177/23197145251358316": "2026", "10.1177/23197145251368600": "2026",
 "10.1177/23197145251387907": "2026",
}
for k, r in recs.items():
    r["online_year"] = ""
    if k in YEARFIX and YEARFIX[k] != r["year"]:
        r["online_year"] = r["year"]
        r["year"] = YEARFIX[k]

# Volume editors of the Review of Management Literature series (Crossref book records)
RML_EDITORS = {
 "1": "Rana, Sudhir; Kathuria, Sakshi; Singh, Jagroop",
 "2": "Rana, Sudhir; Singh, Jagroop; Kathuria, Sakshi",
 "3": "Kaurav, Rahul Pratap Singh; Mishra, Vinaytosh",
 "4A": "Rana, Sudhir", "4B": "Rana, Sudhir", "5": "Rana, Sudhir",
 "6": "Dewasiri, Narayanage Jayantha; Kumar, Jitender; Singhania, Shubham; Baker, H. Kent",
}
for r in recs.values():
    if r["venue"] == "Review of Management Literature" and r["type"] == "book-chapter" and r["volume"] in RML_EDITORS:
        r["editors"] = split_authors(RML_EDITORS[r["volume"]])
        if r["fmt"] == "fl":
            r["authors"] = [fmt_lf(a) for a in r["authors"]]
            r["fmt"] = "lf"

# ------------------------------------------------------------------ clusters.md
md = ["# Thematic clusters\n",
      "Each entry has one primary cluster. Keys are the BibTeX keys in `business-management-master.bib`.\n"]
coll_counts = collections.Counter(c for r in ordered for c in r["collections"])
for c, label, _ in CLUSTERS:
    items = [r for r in ordered if r["cluster"] == c]
    md.append(f"\n## {c}. {label} ({len(items)})\n")
    for r in items:
        tag = "".join({"Rana publications": "R", "FIIB Business Review 2024 onward": "F",
                       "Review of Management Literature": "M"}[x] for x in sorted(r["collections"]))
        md.append(f"- `{r['key']}` [{tag}] {r['year']}. {r['title'].replace('&amp;', '&')}")
md.append("\nCollection codes: R = Sudhir Rana publications; F = FIIB Business Review 2024 onward; M = Review of Management Literature.\n")
open(os.path.join(OUT, "clusters.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")

stats = {"total": len(ordered), "clusters": {CLABEL[c]: counts[c] for c, _, _ in CLUSTERS},
         "collections": dict(coll_counts),
         "types": dict(collections.Counter(r["type"] for r in ordered)),
         "no_doi": sum(1 for r in ordered if r["doi"].lower().startswith("nodoi")),
         "missing_override": missing_override,
         "auto_disagree": sum(1 for r in ordered if r["auto"] != r["cluster"])}
json.dump(stats, open(os.path.join(OUT, "stats.json"), "w"), indent=1)
print(json.dumps(stats, indent=1))
