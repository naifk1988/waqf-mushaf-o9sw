#!/usr/bin/env python3
"""Compact the QCF4 (Madinah Mushaf 1441H) page data from github.com/MohamadHajjRabee/quran-qcf4
(pages/ are MIT-licensed) into data/q4/{page}.json for the app.  Usage: build_q4.py <path-to-quran-qcf4 clone>
Fonts are NOT copied: their license forbids redistribution, so the app loads them from the author's CDN."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1]
OUT = os.path.join(ROOT, "data", "q4")
os.makedirs(OUT, exist_ok=True)
fnum = lambda f: 0 if f == "QCF4_QBSML" else int(f.rsplit("_", 1)[1])

pages = [json.load(open(os.path.join(SRC, "pages", f"{p:03d}.json"), encoding="utf-8")) for p in range(1, 605)]
words = {}  # verse_key -> full word list (text), across page breaks
for d in pages:
    for l in d["lines"]:
        for w in l["words"]:
            if w["type"] == "word":
                lst = words.setdefault(w["verse_key"], [])
                pos = w["position"] - 1
                while len(lst) <= pos:
                    lst.append("")
                lst[pos] = w["text"]

spage = {}
for p, d in enumerate(pages, 1):
    pf = fnum(d["font"])
    keys, lines = [], []
    for l in d["lines"]:
        row = []
        for w in l["words"]:
            t = {"word": "w", "end": "e", "quarter": "q", "surah_header": "h", "bismillah": "b"}[w["type"]]
            item = [t, w["char"]]
            if t in ("w", "e"):
                item += [w["verse_key"], w["position"]]
                if w["verse_key"] not in keys:
                    keys.append(w["verse_key"])
            elif t in ("h", "b"):
                item += [w["sura"]]
                if t == "h":
                    spage.setdefault(w["sura"], p)
            f = fnum(w["font"])
            if f != pf:
                item.append({"f": f})
            row.append(item)
        lines.append([l["line"], row])
    out = {"p": p, "f": pf, "lines": lines, "vw": {k: words[k] for k in keys}}
    with open(os.path.join(OUT, f"{p}.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
print("pages", len(pages), "spage", [spage.get(s) for s in range(1, 115)])
