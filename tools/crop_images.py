# -*- coding: utf-8 -*-
"""Cắt hình minh hoạ trong đề thi ra PNG.

    cd tools && python crop_images.py [id đề ...]

Chỉ phần 聴解 mới có hình thật:
  - 問題1 課題理解: vài câu có lựa chọn là tranh;
  - 問題4 発話表現: mỗi câu một tranh, in thành lưới 2x2, không có chữ nào khác.
Các "bài đọc là ảnh" ở phần 文法・読解 thực ra là text bị bộ lọc watermark ăn mất
(xem HANDOFF §5.3c), không cần cắt.

Ảnh ghi ra `images/<id đề>/choukai-m<số 問題>-q<số câu>.png` và script in sẵn
đoạn JSON để dán vào `exams_manual.json` (trường `img`, đường dẫn tính từ `web/`).
"""
import io
import json
import os
import re
import shutil
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pdfplumber
import pypdfium2
from clean_text import FILES, page_lines

here = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(here, "..", "images")
SCALE = 3               # 3x72 = 216 dpi, đủ nét mà file vẫn nhỏ
PAD = 4                 # chừa lề quanh ảnh, tính bằng point
MIN_AREA = 8000         # bỏ qua icon/đường kẻ vụn
MOND = re.compile(r"^(?:問題|間題)\s*([0-9０-９])")
QNUM = re.compile(r"^\s*([0-9０-９]{1,2})\s*(?:\)|番)")
FW = str.maketrans("０１２３４５６７８９", "0123456789")


def scan(page):
    """-> ([(top, số 問題)], [(top, số câu)]) các mốc trên trang."""
    mondai, qs = [], []
    for l in page_lines(page):
        m = MOND.match(l["text"])
        if m:
            mondai.append((l["top"], int(m.group(1).translate(FW))))
            continue
        q = QNUM.match(l["text"])
        if q:
            qs.append((l["top"], int(q.group(1).translate(FW))))
    return mondai, qs


def collect(tag):
    """-> [(trang, 問題, số câu hoặc None, bbox)] mọi ảnh của đề, theo thứ tự đọc."""
    found = []
    carry = None                       # 問題 còn hiệu lực từ trang trước
    with pdfplumber.open(FILES[tag]) as pl:
        for pi, page in enumerate(pl.pages):
            mondai, qs = scan(page)
            imgs = [im for im in page.images
                    if (im["x1"] - im["x0"]) * (im["bottom"] - im["top"]) > MIN_AREA]
            for im in sorted(imgs, key=lambda i: (round(i["top"]), i["x0"])):
                # chỉ những mốc NẰM TRÊN ảnh mới tính; header dưới ảnh là của phần sau
                md = next((v for t, v in reversed(mondai) if t < im["top"]), carry)
                lb = next((v for t, v in reversed(qs) if t < im["top"]), None)
                found.append([pi, md, lb, (im["x0"], im["top"], im["x1"], im["bottom"])])
            if mondai:
                carry = mondai[-1][1]
    # 問題4 発話表現: tranh CHÍNH LÀ câu hỏi, nhãn 「1番」in 2 cái một dòng nên
    # không bám theo dòng text được -> đánh số theo thứ tự đọc trong cả phần
    m4 = [f for f in found if f[1] == 4]
    for n, f in enumerate(m4, 1):
        f[2] = n
    return found


def crop_exam(tag):
    found = collect(tag)
    if not found:
        return []
    d = os.path.join(OUT, tag)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    made = []
    doc = pypdfium2.PdfDocument(FILES[tag])
    cache = {}
    for pi, md, lb, (x0, top, x1, bottom) in found:
        if md is None or lb is None:
            print("   !! bỏ qua ảnh trang %d: không xác định được câu" % (pi + 1))
            continue
        if pi not in cache:
            cache[pi] = doc[pi].render(scale=SCALE).to_pil()
        bm = cache[pi]
        box = (max(0, int((x0 - PAD) * SCALE)), max(0, int((top - PAD) * SCALE)),
               min(bm.width, int((x1 + PAD) * SCALE)),
               min(bm.height, int((bottom + PAD) * SCALE)))
        name = "choukai-m%d-q%d.png" % (md, lb)
        path = os.path.join(d, name)
        # tranh nét đen trắng: xám 8-bit nhỏ hơn RGB nhiều mà không mất gì
        bm.crop(box).convert("L").save(path, optimize=True)
        made.append({"mondai": md, "label": lb,
                     "img": "../images/%s/%s" % (tag, name)})
        print("   問題%d câu %-2d -> %-22s %5.0f KB (trang %d)"
              % (md, lb, name, os.path.getsize(path) / 1024, pi + 1))
    doc.close()
    return made


if __name__ == "__main__":
    tags = sys.argv[1:] or ["2022-07", "2022-12", "2023-07"]
    manual = []
    for tag in tags:
        print("==", tag)
        made = crop_exam(tag)
        if not made:
            continue
        by_m = {}
        for it in made:
            by_m.setdefault(it["mondai"], []).append(
                {"label": it["label"], "img": it["img"]})
        manual.append({"id": tag, "sections": [{"key": "choukai", "mondai": [
            {"no": no, "questions": qs} for no, qs in sorted(by_m.items())]}]})
    print("\nTổng: %d ảnh" % sum(len(m["questions"])
                                 for e in manual for s in e["sections"] for m in s["mondai"]))
    out = os.path.join(here, "images_manual.json")
    with io.open(out, "w", encoding="utf-8") as f:
        json.dump(manual, f, ensure_ascii=False, indent=2)
    print("Đoạn JSON để gộp vào exams_manual.json: %s" % out)
