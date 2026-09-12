# -*- coding: utf-8 -*-
"""PDF "GUNGUN N3 - KANJI" -> kanji.json

Bố cục mỗi trang (595x842), mỗi khối là một chữ kanji:
  câu chuyện ghi nhớ : dòng bắt đầu bằng '|' ở x~48, cao ~11
  âm Hán-Việt        : x 60-223, cao >= 12.5, chữ in hoa
  kanji lớn          : x~76, cao >= 60
  訓/音               : kana sau dấu 訓 / 音, cao 10-12
  từ vựng            : x >= 210, cao >= 13.5 (CJK); furigana cao < 9.5; nghĩa x >= 295

Chạy: python parse_kanji.py   (cần pdfplumber; tự tìm PDF trong Downloads)
"""
import sys, io, json, os, re, glob
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import unicodedata
import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "kanji.json")
KANA = re.compile(r"^[\u3040-\u30ffー〜・、]+$")
CJK = re.compile(r"[\u3040-\u30ff\u30a0-\u30ff\u4e00-\u9fff]")
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"
UPPER = ("A-ZĐÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ"
         "ÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ")
HV_RX = re.compile(r"^[%s/\s-]+$" % UPPER)




def _plain(t):
    """bỏ dấu tiếng Việt + về chữ hoa, để so tên file bất kể NFC/NFD"""
    t = unicodedata.normalize("NFD", t)
    return "".join(c for c in t if not unicodedata.combining(c)).upper().replace("Đ", "D")


def _find_pdf(*keywords):
    for p in glob.glob(os.path.join(os.path.expanduser("~"), "Downloads", "*.pdf")):
        name = _plain(os.path.basename(p))
        if all(_plain(k) in name for k in keywords):
            return p
    raise SystemExit("Không tìm thấy PDF chứa: %s (trong Downloads)" % ", ".join(keywords))


def find_pdf():
    return _find_pdf("GUNGUN", "KANJI")


def parse():
    kanjis = []
    with pdfplumber.open(find_pdf()) as pdf:
        for pi, page in enumerate(pdf.pages):
            words = page.extract_words()
            big = [w for w in words if (w["bottom"] - w["top"]) >= 60
                   and CJK.search(w["text"]) and w["x0"] < 200]
            if not big:
                continue                                   # trang bìa / mục lục
            header = [w for w in words if w["top"] < 45]
            chapter = next((int(w["text"]) for w in header
                            if w["x0"] < 40 and (w["bottom"] - w["top"]) > 25 and w["text"].isdigit()), None)
            m = re.search(r"BÀI\s*(\d+)", " ".join(w["text"] for w in header))
            bai = int(m.group(1)) if m else None
            group = next((CIRCLED.index(w["text"][0]) + 1 for w in header
                          if w["text"] and w["text"][0] in CIRCLED), None)
            if chapter is None or bai is None:
                continue

            body = [w for w in words if 45 <= w["top"] < 800]
            big.sort(key=lambda w: w["top"])
            story_tops = sorted(set(round(w["top"]) for w in body
                                    if w["x0"] < 55 and w["text"].lstrip().startswith("|")
                                    and (w["bottom"] - w["top"]) < 13))
            starts = story_tops if len(story_tops) == len(big) else [b["top"] - 75 for b in big]
            bounds = [(s - 3, (starts[i + 1] if i + 1 < len(starts) else 800) - 3)
                      for i, s in enumerate(starts)]

            for b, (t0, t1) in zip(big, bounds):
                blk = [w for w in body if t0 <= w["top"] < t1]
                story_toks, hanviet, kun, on, anchors = [], [], [], [], []
                kun_marker = [w for w in blk if w["text"] == "訓"]
                kun_top = kun_marker[0]["top"] if kun_marker else None

                def linekey(w):
                    return (int((w["top"] + 3) // 6), w["x0"])

                for w in blk:
                    h = w["bottom"] - w["top"]
                    t, x = w["text"], w["x0"]
                    if t in ("訓", "音") or w is b or h >= 60:
                        continue
                    if kun_top is not None and w["top"] >= kun_top - 5 and h < 12.5 and x < 223:
                        if KANA.match(t):
                            (kun if x < 133 else on).append((linekey(w), t))
                        continue
                    if h >= 12.5 and 60 < x < 223 and HV_RX.match(t):
                        hanviet.append((linekey(w), t))
                    elif h >= 13.5 and 210 <= x < 300 and CJK.search(t):
                        anchors.append(w)
                    elif 9.5 <= h < 12.5:
                        story_toks.append(w)

                hanviet.sort()
                anchors.sort(key=lambda w: w["top"])
                items = [{"w": a, "furi": [], "mean": []} for a in anchors]

                def nearest(top, maxd=1e9):
                    if not items:
                        return None
                    it = min(items, key=lambda it: abs(it["w"]["top"] - top))
                    return it if abs(it["w"]["top"] - top) <= maxd else None

                consumed = set()
                for w in blk:
                    h = w["bottom"] - w["top"]
                    if w["x0"] < 210 or w in anchors or h >= 60:
                        continue
                    if h < 9.5 and KANA.match(w["text"]):
                        it = nearest(w["top"] + 5)
                        if it:
                            it["furi"].append((linekey(w), w["text"]))
                    elif w["x0"] >= 295 and 10.5 <= h < 16:
                        it = nearest(w["top"], maxd=15)
                        if it:
                            it["mean"].append((linekey(w), w["text"]))
                            consumed.add(id(w))

                story_toks = [w for w in story_toks if id(w) not in consumed]
                story_toks.sort(key=linekey)
                story = re.sub(r"\s+", " ",
                               " ".join(w["text"] for w in story_toks).replace("|", "")).strip()

                vocab = []
                for it in items:
                    it["furi"].sort()
                    it["mean"].sort()
                    vocab.append({"word": it["w"]["text"],
                                  "reading": "".join(t for _, t in it["furi"]),
                                  "readingParts": [t for _, t in it["furi"]],
                                  "meaning": re.sub(r"\s+", " ",
                                                    " ".join(t for _, t in it["mean"])).strip(" ,;")})
                kun.sort()
                on.sort()
                hv = " ".join(t for _, t in hanviet)
                kanjis.append({"kanji": b["text"], "hanviet": "" if not hv.strip("- ") else hv,
                               "story": story,
                               "kun": "".join(t for _, t in kun).replace("、", "、 ").strip("、 "),
                               "on": "".join(t for _, t in on).replace("、", "、 ").strip("、 "),
                               "words": vocab, "chapter": chapter, "bai": bai,
                               "group": group, "page": pi + 1})

    json.dump(kanjis, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("kanji:", len(kanjis), "| từ đi kèm:", sum(len(k["words"]) for k in kanjis),
          "->", os.path.normpath(OUT))
    print("thiếu nghĩa:", sum(1 for k in kanjis for w in k["words"] if not w["meaning"]))


if __name__ == "__main__":
    parse()
