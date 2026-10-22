#!/usr/bin/env python3
"""Align Habti «صه» marks read from the Qalun mushaf (data/raw/habti_[a-d].json)
to the Hafs/Kufan text, and write data/raw/habti.json in the common entry format."""
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = json.load(open(os.path.join(ROOT, "data", "text_preview.json"), encoding="utf-8"))

DIAC = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ࣓-ࣿ]")


def norm(s):
    s = DIAC.sub("", s or "")
    s = re.sub("[ٱأإآ]", "ا", s).replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    s = re.sub(r"[^ء-ي ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def skel(s):
    k = re.sub("[اويءى ]", "", norm(s))
    return k or norm(s).replace(" ", "")


def flat(surah):
    out = []
    for v in TEXT[str(surah)]:
        ws = v["t"].split()
        for i, w in enumerate(ws):
            out.append((v["a"], i, w, skel(w)))
    return out


def similar(a, b):
    if not a or not b:
        return 0
    if a == b:
        return 1
    # cheap ratio: common prefix/suffix share
    import difflib
    return difflib.SequenceMatcher(None, a, b).ratio()


def align(marks, words):
    ptr, out, miss = 0, [], []
    for m in marks:
        c0 = norm(m.get("context") or m.get("word"))
        c0 = re.sub(r"^بسم الله الرحمن الرحيم ?", "", c0) or norm(m.get("word"))
        c0 = re.sub(r"(^| )يا (\S)", r"\1يا\2", c0)  # mushaf writes يا+noun as one word
        c0 = re.sub(r"(^| )ما ذا( |$)", r"\1ماذا\2", c0)
        ctx = [skel(t) for t in c0.split()]
        ctx = [c for c in ctx if c] or [skel(m.get("word"))]
        best, bscore = None, 0
        span = range(ptr, min(len(words), ptr + 160))
        best, bscore = scan(ctx, words, ptr, span)
        if best is None or bscore < 0.62:
            b2, s2 = scan(ctx, words, ptr, range(ptr, len(words)))
            if b2 is not None and s2 >= 0.8:
                best, bscore = b2, s2
        if best is None or bscore < 0.62:
            miss.append(m)
            continue
        a, i, w, _ = words[best]
        cue = " ".join(x[2] for x in words[max(0, best - 1):best + 1] if x[0] == a)
        out.append((a, i, cue, m))
        ptr = best + 1
    return out, miss


def scan(ctx, words, ptr, span):
    best, bscore = None, 0
    if True:
        for j in span:
            # score: compare last k context words to words ending at j
            k = len(ctx)
            sc = 0
            for t in range(k):
                jj = j - t
                if jj < 0:
                    break
                w = 1.0 if t == 0 else 0.6
                sc += w * similar(ctx[k - 1 - t], words[jj][3])
            sc /= (1 + 0.6 * (k - 1))
            sc -= (j - ptr) * 0.0008  # prefer the nearest match
            if sc > bscore:
                best, bscore = j, sc
    return best, bscore


def main():
    marks = []
    files = [f for f in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "habti_*.json")))
             if re.fullmatch(r"habti_[a-z]{1,2}\.json", os.path.basename(f))]
    for f in files:
        marks += json.load(open(f, encoding="utf-8"))
    # chunk files sort alphabetically (a, aa, ab, b…); restore mushaf order by page (stable within a page)
    marks.sort(key=lambda m: int(m.get("pdf_page") or 0))
    entries, misses = [], []
    for surah in range(1, 115):
        if str(surah) not in TEXT:
            continue
        ms = [m for m in marks if int(m.get("surah", 2)) == surah]
        got, miss = align(ms, flat(surah))
        misses += miss
        for a, i, cue, m in got:
            entries.append({
                "s": surah, "a": a, "cue": DIAC.sub("", cue), "type": "waqf",
                "ruling": "وقف", "raw": "صه",
                "reason": "",
                "who": "",
                "loc": f"مصحف الجماهيرية (رواية قالون) ص{m.get('pdf_page')}" + (" — قراءة العلامة غير مؤكدة" if m.get("unsure") else ""),
                "page_id": m.get("pdf_page"),
            })
    json.dump(entries, open(os.path.join(ROOT, "data", "raw", "habti.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("marks", len(marks), "aligned", len(entries), "missed", len(misses))
    for m in misses[:40]:
        print("  miss", m.get("pdf_page"), m.get("context"))


if __name__ == "__main__":
    main()
