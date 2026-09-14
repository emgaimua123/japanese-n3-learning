# -*- coding: utf-8 -*-
"""Extract watermark-free text from a JLPT exam PDF."""
import sys, io, json, os, re
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pdfplumber

here = os.path.dirname(os.path.abspath(__file__))
FILES = json.load(open(os.path.join(here, "exam_files.json"), encoding="utf-8"))
WM_FONT = "Helvetica"          # the "Tôi Yêu Ngoại Ngữ Group / Yuuki Bùi" overlay
# Watermark còn rải thêm mấy mẩu "ạữ" bằng Arial. Phân biệt với chữ số thật
# (cũng in bằng Arial) bằng MÀU: rác watermark là `(0.0,)`, chữ thật là `(0,)`.
#
# Luật cũ lọc mọi ký tự màu `(0.0,)` bất kể font → ăn nhầm cả bài đọc, vì thân
# bài in bằng UDDigiKyokashoNK-R cũng mang đúng màu ấy (2046 ký tự ở đề 12/2022,
# 1423 ở đề 7/2023). Đó là lý do 問題3/4/7 từng bị coi là "bài đọc nằm trong ảnh".
WM_COLOR_FONTS = ("Helvetica", "Arial")


def is_watermark(c):
    # the overlay uses Helvetica (big diagonal text) plus Arial for the stray
    # "ạữ" fragments, and is much larger than the 11-14pt body text
    if WM_FONT in c["fontname"]:
        return True
    if (str(c.get("non_stroking_color")) == "(0.0,)"
            and any(f in c["fontname"] for f in WM_COLOR_FONTS)):
        return True
    if c["size"] > 15.5 and not re.match(r"[　-鿿＀-￯]", c["text"]):
        return True
    return False


def page_lines(page, tol=3.2):
    chars = [c for c in page.chars if not is_watermark(c)]
    if not chars:
        return []
    rows = []
    for c in sorted(chars, key=lambda c: (round(c["top"], 1), c["x0"])):
        for r in rows:
            if abs(r["top"] - c["top"]) <= tol:
                r["cs"].append(c)
                break
        else:
            rows.append({"top": c["top"], "cs": [c]})
    out = []
    for r in sorted(rows, key=lambda r: r["top"]):
        cs = sorted(r["cs"], key=lambda c: c["x0"])
        txt, prev = "", None
        for c in cs:
            if prev is not None and c["x0"] - prev["x1"] > 3:
                txt += " "
            txt += c["text"]
            prev = c
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            out.append({"top": round(r["top"], 1), "text": txt,
                        "size": round(max(c["size"] for c in cs), 1)})
    return out


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "2023-07"
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    b = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    with pdfplumber.open(FILES[tag]) as pdf:
        print("pages:", len(pdf.pages))
        for i in range(a, min(b, len(pdf.pages))):
            print(f"\n========== page {i+1} ==========")
            for l in page_lines(pdf.pages[i]):
                print(f"[{l['size']}] {l['text']}")
