# -*- coding: utf-8 -*-
"""PDF "GG N3 - TỪ VỰNG TỔNG HỢP" -> vocab.json

Bố cục cột trái của mỗi mục (x0 < 206):
  từ        x~60,  cao 12-13, CJK
  từ loại   x 124-160, cao 5-8   -> (N), (N/Nする), PT, Aい ...
  Hán-Việt  x >= 160,  cao ~8    -> chữ in hoa
  cách đọc  x < 124,   cao ~8    -> kana
  nghĩa     dòng bắt đầu bằng ❖ (cao ~11) + phần xuống dòng cỡ 9

Chạy: python parse_vocab.py   (cần pdfplumber; tự tìm PDF trong Downloads)
Sau đó chạy fix_vocab2.py để dọn các nghĩa bị lẫn câu ví dụ.
"""
import sys, io, json, os, re, glob
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import unicodedata
import pdfplumber

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "vocab.json")
KANA = re.compile(r"^[\u3040-\u30ffー〜]+$")
CJK = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\u30a0-\u30ffー〜]")
POS_OK = re.compile(r"^[()/A-Zいなする\-]+$")




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
    return _find_pdf("TU VUNG")


def parse():
    entries = []
    with pdfplumber.open(find_pdf()) as pdf:
        for pi, page in enumerate(pdf.pages):
            header = [w for w in page.extract_words() if w["top"] < 40]
            m = re.search(r"CHƯƠNG\s*(\d+)\s*BÀI\s*(\d+)", " ".join(w["text"] for w in header))
            chapter, bai = (int(m.group(1)), int(m.group(2))) if m else (None, None)

            words = [w for w in page.extract_words() if w["x0"] < 206 and 42 < w["top"] < 700]
            lines = []
            for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
                for ln in lines:
                    if abs(ln["top"] - w["top"]) < 4:
                        ln["words"].append(w)
                        break
                else:
                    lines.append({"top": w["top"], "words": [w]})

            cur = None
            for ln in lines:
                ws = sorted(ln["words"], key=lambda w: w["x0"])
                first = ws[0]
                fh = first["bottom"] - first["top"]
                if first["x0"] < 100 and fh >= 11.5 and CJK.search(first["text"]):
                    if cur:
                        entries.append(cur)
                    cur = {"word": first["text"], "reading": "", "hanviet": [], "pos": [],
                           "meaning_words": [], "chapter": chapter, "bai": bai, "page": pi + 1}
                    rest = ws[1:]
                elif cur is None:
                    continue
                else:
                    rest = ws
                for w in rest:
                    h = w["bottom"] - w["top"]
                    t = w["text"]
                    if h < 10 and 124 <= w["x0"] < 160.5 and POS_OK.match(t):
                        cur["pos"].append(t)
                    elif h < 10 and w["x0"] >= 160.5:
                        cur["hanviet"].append(t)
                    elif KANA.match(t) and h < 10:
                        cur["reading"] += t
                    else:
                        cur["meaning_words"].append(t)
            if cur:
                entries.append(cur)

    out, seen = [], set()
    for e in entries:
        pos = "".join(e["pos"]).replace("(", "").replace(")", "")
        hanviet = " ".join(e["hanviet"])
        mpos = re.match(r"^\((.+)\)$", hanviet)          # "(PT)" / "(định ngữ)"
        if mpos and not pos:
            pos, hanviet = mpos.group(1), ""
        senses = [s.strip(" ,;") for s in " ".join(e["meaning_words"]).split("❖") if s.strip(" ,;")]
        if not senses:
            continue
        reading = e["reading"] or (e["word"] if KANA.match(e["word"]) else "")
        if not reading:                                   # prefix/suffix entries: kana sits in the gloss
            for i, s in enumerate(senses):
                mm = re.search(r"[～〜]?([\u3040-\u309f]+)[～〜]?", s)
                if mm:
                    reading = mm.group(1)
                    rest = re.sub(r"\(?(tiền tố|hậu tố|Tiền tố|Hậu tố)\)?\s*", "", s)
                    rest = re.sub(r"[～〜]?[\u3040-\u309f]+[～〜]?\s*[;,]?\s*", "", rest, count=1).strip(" ,;")
                    if rest:
                        senses[i] = rest
                    else:
                        senses.pop(i)
                    break
        key = (e["word"], reading)
        if key in seen:
            continue
        seen.add(key)
        out.append({"word": e["word"], "reading": reading, "hanviet": hanviet, "pos": pos,
                    "meanings": senses, "chapter": e["chapter"], "bai": e["bai"], "page": e["page"]})

    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("entries:", len(out), "->", os.path.normpath(OUT))
    print("thiếu cách đọc:", sum(1 for e in out if not e["reading"]))


if __name__ == "__main__":
    parse()
