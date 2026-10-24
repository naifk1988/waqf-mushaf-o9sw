#!/usr/bin/env python3
"""Merge data/raw/*.json into data/waqf.json and build dist/preview.html (data inlined)."""
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")

BOOKS = [
    # id, short name, title, death (AH), khizana book_id
    ("ibnsadan", "ابن سعدان", "الوقف والابتداء في كتاب الله", 231, 17843),
    ("anbari", "ابن الأنباري", "إيضاح الوقف والابتداء", 328, 14255),
    ("nahhas", "النحاس", "القطع والائتناف", 338, 20966),
    ("dani", "الداني", "المكتفى في الوقف والابتدا", 444, 26461),
    ("hudhali", "الهذلي", "الوقف والابتداء في كتاب الله", 465, 1300170),
    ("akhshidh", "ابن الأخشيذ", "منازل القرآن في الوقوف", 524, 30187),
    ("sajawandi", "السجاوندي", "علل الوقوف", 560, 30007),
    ("qastallani", "القسطلاني", "لطائف الإشارات لفنون القراءات", 923, 30041),
    ("ansari", "زكريا الأنصاري", "المقصد لتلخيص ما في المرشد", 926, 10917),
    ("habti", "الهبطي", "تقييد وقف القرآن (بواسطة حاشية محقق لطائف الإشارات)", 930, 30041),
    ("ashmuni", "الأشموني", "منار الهدى في بيان الوقف والابتدا", 1100, 38091),
]


NOTE_RE = re.compile(r"(?<!\()\(([^()]*?(?:بلفظ|ذكره|بلا حكم|مطبوع|المطبوع|الكتاب|يقتبس|عطف|سلسلة|ملاحظة|يحتمل|المصحف|تصحيف|خطأ|السابق|التالي|غير مذكور|لم يذكر|لم ينص)[^()]*)\)(?!\))")


def split_note(reason):
    """Move extraction notes written in parentheses out of the author's text."""
    notes = [m.group(1).strip() for m in NOTE_RE.finditer(reason)]
    if not notes:
        return reason, ""
    clean = re.sub(r"\s{2,}", " ", NOTE_RE.sub("", reason)).strip(" .،")
    return clean, "؛ ".join(notes)


QRE = re.compile(r"قرأ|قرئ|قراءة|قراءته|لمن (?:رفع|نصب|خفض|جر|جرّ|كسر|فتح|ضم|شدد|خفف)|ومن (?:رفع|نصب|خفض|جر|جرّ|كسر|فتح|ضم|شدد|خفف)")


def category(ruling, typ):
    r = (ruling or "").strip()
    if typ == "ibtida" or r.startswith("ابتداء"):
        return "ibtida"
    if "لازم" in r:
        return "lazim"
    if (r.startswith("لا ") or r in ("لا", "لا يوقف") or "ليس" in r or "قبيح" in r
            or "غير تام" in r or "لا يتم" in r or "لا يقطع" in r or "لا يحسن" in r
            or "غير حسن" in r or "خطأ" in r or "لم يقف" in r or "مكروه" in r or "ممنوع" in r):
        return "neg"
    if "مجوز" in r or "مرخص" in r or "لمضطر" in r or "ضرورة" in r or "ناقص" in r:
        return "weak"
    if "تام" in r or "أتم" in r or "تمام" in r or "كامل" in r:
        return "tam"
    if "كاف" in r or "أكفى" in r or "مطلق" in r or "مفهوم" in r:
        return "kafi"
    if "حسن" in r or "جائز" in r or "صالح" in r:
        return "hasan"
    return "other"


SURAH_NAMES = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]

ACTIVE = {"dani", "sajawandi", "ansari", "ashmuni", "habti"}  # books shown in the app; others stay in data/raw


def main():
    entries, counts, surahs = {}, {}, set()
    for bid, *_ in BOOKS:
        if bid not in ACTIVE:
            continue
        paths = [os.path.join(RAW, bid + ".json")] + sorted(glob.glob(os.path.join(RAW, bid + "_[0-9]*.json")))
        paths = [x for x in paths if os.path.exists(x)]
        if not paths:
            continue
        data = []
        for path in paths:
            try:
                data += json.load(open(path, encoding="utf-8"))
            except Exception as e:
                print("!! cannot read", path, e)
        n = 0
        for e in data:
            try:
                s, a = int(e["s"]), int(e["a"])
            except Exception:
                continue
            typ = e.get("type") or "waqf"
            reason, note = split_note((e.get("reason") or "").strip())
            out = {
                "b": bid, "cue": (e.get("cue") or "").strip(), "type": typ,
                "r": (e.get("ruling") or "").strip(), "raw": (e.get("raw") or "").strip(),
                "c": category(e.get("ruling"), typ), "reason": reason,
                "who": (e.get("who") or "").strip(), "loc": (e.get("loc") or "").strip(),
            }
            if note:
                out["note"] = note
            if QRE.search(out["reason"] + " " + out["raw"] + " " + out["r"] + " " + out["who"]):
                out["q"] = 1  # the ruling depends on a reading (qira'a)
            if not out["cue"]:
                continue
            entries.setdefault(f"{s}:{a}", []).append(out)
            surahs.add(s)
            n += 1
        counts[bid] = n
    books = []
    for bid, short, title, death, kid in BOOKS:
        if bid not in ACTIVE:
            continue
        books.append({"id": bid, "short": short, "title": title, "death": death, "khizana": kid,
                      "count": counts.get(bid, 0), "pending": bid not in counts})
    total = sum(counts.values())
    doc = {"version": 1, "books": books, "entries": entries, "surahs_covered": sorted(surahs),
           "coverage": "، ".join(SURAH_NAMES[x - 1] for x in sorted(surahs)) if len(surahs) < 20 else f"{len(surahs)} سورة، من {SURAH_NAMES[min(surahs)-1]} إلى {SURAH_NAMES[max(surahs)-1]}",
           "total": total}
    # index file (books, coverage) + one entries file per surah, loaded on demand by the app
    index = {k: v for k, v in doc.items() if k != "entries"}
    index["split"] = True
    with open(os.path.join(ROOT, "data", "waqf.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    sdir = os.path.join(ROOT, "data", "s")
    os.makedirs(sdir, exist_ok=True)
    for old in glob.glob(os.path.join(sdir, "*.json")):
        os.remove(old)
    per = {}
    for key, lst in entries.items():
        per.setdefault(key.split(":")[0], {})[key] = lst
    for s, part in per.items():
        with open(os.path.join(sdir, f"{s}.json"), "w", encoding="utf-8") as f:
            json.dump(part, f, ensure_ascii=False, separators=(",", ":"))
    # index of ayahs whose pause rulings depend on the reading: [key, page, cue, [books]]
    page_of = {}
    for pg in range(1, 605):
        fp = os.path.join(ROOT, "data", "q4", f"{pg}.json")
        if os.path.exists(fp):
            for k in json.load(open(fp, encoding="utf-8"))["vw"]:
                page_of.setdefault(k, pg)
    qidx = {}
    for key, lst in entries.items():
        for e in lst:
            if e.get("q"):
                d = qidx.setdefault((key, e["cue"].split(" (")[0]), set())
                d.add(e["b"])
    qlist = sorted(([k, page_of.get(k, 0), cue, sorted(bs)] for (k, cue), bs in qidx.items()),
                   key=lambda x: tuple(map(int, x[0].split(":"))))
    with open(os.path.join(ROOT, "data", "qidx.json"), "w", encoding="utf-8") as f:
        json.dump(qlist, f, ensure_ascii=False, separators=(",", ":"))
    print("reading-dependent spots:", len(qlist))
    # preview: inline data + text so the page works without network
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    text = open(os.path.join(ROOT, "data", "text_preview.json"), encoding="utf-8").read()
    inline = ("<script>window.WAQF_DATA=" + json.dumps(doc, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
              + ";window.TEXT_PREVIEW=" + text.replace("</", "<\\/") + ";window.FORCE_PREVIEW=true;</script>\n")
    html = re.sub(r'<link rel="(manifest|apple-touch-icon)"[^>]*>\n', "", html)
    html = html.replace("<script>\n(function(){", inline + "<script>\n(function(){", 1)
    with open(os.path.join(ROOT, "dist", "preview.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("entries:", total, counts)
    print("categories:", {c: sum(1 for v in entries.values() for e in v if e["c"] == c)
                          for c in ["lazim", "tam", "kafi", "hasan", "weak", "neg", "ibtida", "other"]})


if __name__ == "__main__":
    main()
