# Business Management Reference Library

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24084354.svg)](https://doi.org/10.5281/zenodo.24084354)

A Claude skill and DOI-verified BibTeX library of 351 business and management works. Add it to Claude and it will draw on these works whenever you write a research paper, write a literature review or systematic literature review (SLR), identify research gaps, search for papers, build a conceptual framework or hypotheses, or prepare a peer review.

## What is inside

| Collection | Works |
|---|---|
| FIIB Business Review (SAGE, ISSN 2319-7145), every article and editorial from January 2024 | 136 |
| Review of Management Literature (Emerald, ISSN 2754-5865), every chapter in volumes 1 to 6 | 78 |
| Publications of Sudhir Rana (ORCID 0000-0002-9910-1930) | 149 |

Twelve works belong to two collections, so the unique total is 351. Every record carries a verified DOI (twelve without one are flagged), a ready APA 7 reference and one of 14 research clusters: research methods and literature reviews; AI, analytics and digital transformation; technology adoption, FinTech and blockchain; consumer behaviour and decision making; digital marketing and social media; marketing strategy and services; international business and emerging markets; strategy and firm performance; entrepreneurship and innovation; sustainability, CSR, ESG and governance; organisational behaviour, HRM and leadership; finance, banking and economics; tourism, hospitality and healthcare management; operations and supply chain management.

## Add the skill to Claude

1. Download [`skill-download/business-management-reference-library.zip`](skill-download/business-management-reference-library.zip).
2. In Claude, open Settings, then Capabilities, then Skills, and upload the zip.
3. Ask Claude for a literature review, a gap analysis or a paper search in business and management. It searches the library and cites works with their exact metadata.

For Claude Code, copy the `business-management-reference-library` folder into `~/.claude/skills/`.

## Use the files without Claude

| File | Use |
|---|---|
| `library/business-management-master.bib` | All 351 entries for LaTeX, Overleaf, Zotero, JabRef, Mendeley and EndNote |
| `library/rana-publications.bib`, `library/fiib-2024-onward.bib`, `library/review-of-management-literature.bib` | Collection subsets with the same citation keys |
| `library/business-management-master.ris` | RIS export for EndNote, Mendeley, Zotero and RefWorks |
| `library/catalogue.csv` | One row per work with cluster, DOI, topic terms and an APA 7 reference |
| `library/clusters.md` | Every work listed under its cluster |
| `build.py`, `data/` | Source data and the script that regenerates every file |

A searchable online version is at https://claude.ai/code/artifact/b2c0df6f-c18d-4f14-907f-23e611aed4f4

## Cite

Rana, S. (2026). *Business Management Reference Library: A clustered, DOI-verified BibTeX collection* (Version 1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24084354

## Licence

The bibliographic metadata compilation is released under CC0 1.0. The works themselves remain under their publishers' copyright and licences.
