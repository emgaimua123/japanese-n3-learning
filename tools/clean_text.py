# -*- coding: utf-8 -*-
"""Extract watermark-free text from a JLPT exam PDF."""
import sys, io, json, os, re
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pdfplumber

here = os.path.dirname(os.path.abspath(__file__))
FILES = json.load(open(os.path.join(here, "exam_files.json"), encoding="utf-8"))
WM_FONT = "Helvetica"          # the "Tôi Yêu Ngoại Ngữ Group / Yuuki Bùi" overlay


def is_watermark(c):
    # the overlay uses Helvetica, renders in colour (0.0,) rather than (0,),
    # and is much larger than the 11-14pt body text
    if WM_FONT in c["fontname"]:
        return True
    if str(c.get("non_stroking_color")) == "(0.0,)":
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
