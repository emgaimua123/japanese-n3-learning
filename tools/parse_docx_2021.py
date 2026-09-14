# -*- coding: utf-8 -*-
"""Trích đề JLPT N3 tháng 7/2021 từ file .docx (bản gõ lại, có đáp án).

    cd tools && python parse_docx_2021.py

Khác mọi script khác trong thư mục này: nguồn là .docx chứ không phải PDF, nên
không dùng chung pipeline `parse_exam2.py`. Kết quả ghi ra `tools/exam_2021_07.json`
theo đúng schema của `exams.json` (HANDOFF §7), để gộp vào `exams_manual.json`.

Ảnh trong docx được tách ra `images/2021-07/`.

Hai chỗ theo đúng format đề JLPT thật:
  - 聴解 問題3 (概要理解, 3 câu, 4 lựa chọn) và 問題5 (即時応答, 9 câu, 3 lựa chọn)
    KHÔNG in gì trên đề, mọi thứ đọc bằng audio. Script vẫn tạo đủ số câu với
    lựa chọn trống để người học nghe rồi chọn số — số lượng lấy từ bảng đáp án.
  - 聴解 問題4 (発話表現, 4 câu, 3 lựa chọn): tranh chính là đề bài.
"""
import io
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import docx

here = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.expanduser("~"), "Downloads",
                   "Đề_thi_JLPT_N3_07_2021_gach_chan.docx")
TAG = "2021-07"
TITLE = "Đề thi tháng 7/2021"
IMGDIR = os.path.join(here, "..", "images", TAG)
AUDIO = "../audio/%s/choukai.mp3" % TAG
OUT = os.path.join(here, "exam_2021_07.json")

SECTIONS = {
    "moji":    {"name": "Từ vựng – Chữ Hán", "jp": "言語知識（文字・語彙）", "minutes": 30},
    "bunpou":  {"name": "Ngữ pháp – Đọc hiểu", "jp": "言語知識（文法）・読解", "minutes": 70},
    "choukai": {"name": "Nghe hiểu", "jp": "聴解", "minutes": 40},
}
SEC_OF = {"第1部分": "moji", "第2部分": "bunpou", "第3部分": "choukai"}
ANS_SEC = {"言語知識（文字・語彙）": "moji", "文法・読解": "bunpou", "聴解": "choukai"}

RX_SEC = re.compile(r"^第(\d)部分")
RX_MONDAI = re.compile(r"^【問題(\d)】\s*(.*)$")
RX_Q = re.compile(r"^(\d{1,2})\.\s*(.*)$")          # 文字・語彙 / 文法・読解
RX_BAN = re.compile(r"^(\d{1,2})番[：:]?\s*(.*)$")   # 聴解
RX_OPT = re.compile(r"^([1-4])\)\s*(.*)$")
RX_ANS_HEAD = re.compile(r"^【(.+?)】$")
RX_ANS = re.compile(r"^問題(\d)\s*\((\d+)\)～\((\d+)\)：\s*(.+)$")

# bài đọc dùng chung cho cả 問題 / riêng cho từng câu
SHARED_PASSAGE = {("bunpou", 3), ("bunpou", 5), ("bunpou", 6), ("bunpou", 7)}
PER_Q_PASSAGE = {("bunpou", 4)}
# 問題 của phần nghe mà đề không in gì: (số câu, số lựa chọn)
AUDIO_ONLY = {3: (3, 4), 5: (9, 3)}


def para_text(p):
    """Giữ dấu gạch chân của đề bằng 【】 — biết từ nào đang được hỏi."""
    out = []
    for r in p.runs:
        out.append("【%s】" % r.text if r.underline and r.text.strip() else r.text)
    return re.sub(r"\s+", " ", "".join(out)).strip()


def save_images(doc):
    """-> {chỉ số đoạn: tên file ảnh} và ghi ảnh ra images/2021-07/."""
    os.makedirs(IMGDIR, exist_ok=True)
    found = {}
    for i, p in enumerate(doc.paragraphs):
        ids = re.findall(r'r:embed="([^"]+)"', p._p.xml)
        if not ids:
            continue
        part = doc.part.related_parts[ids[0]]
        found[i] = (part.blob, os.path.splitext(part.partname)[1] or ".png")
    return found


def parse_answers(doc):
    """-> {(phần, số 問題, số câu): đáp án}"""
    ans, sec = {}, None
    for p in doc.paragraphs:
        t = p.text.strip()
        h = RX_ANS_HEAD.match(t)
        if h and h.group(1) in ANS_SEC:
            sec = ANS_SEC[h.group(1)]
            continue
        m = RX_ANS.match(t)
        if m and sec:
            no, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            vals = [int(x) for x in re.findall(r"[1-4]", m.group(4))]
            labels = list(range(a, b + 1))
            if len(vals) != len(labels):
                raise SystemExit("bảng đáp án lệch: %s (%d số / %d câu)"
                                 % (t, len(vals), len(labels)))
            for lb, v in zip(labels, vals):
                ans[(sec, no, lb)] = v
    return ans


def parse():
    doc = docx.Document(SRC)
    answers = parse_answers(doc)
    images = save_images(doc)

    secs, cur_sec, cur_m, cur_q = [], None, None, None
    buf = []                       # đoạn văn đang gom, chưa biết thuộc về ai

    def flush_passage(target_q):
        """Gắn đoạn văn đã gom vào câu hoặc vào cả 問題."""
        nonlocal buf
        if not buf or cur_m is None:
            buf = []
            return
        text = "\n".join(buf).strip()
        key = (cur_sec["key"], cur_m["no"])
        if key in PER_Q_PASSAGE and target_q is not None:
            target_q["passage"] = text
        elif not cur_m.get("passage"):
            cur_m["passage"] = text
        else:
            cur_m["passage"] += "\n" + text
        buf = []

    for i, p in enumerate(doc.paragraphs):
        t = para_text(p)
        if i in images and cur_q is not None:
            blob, ext = images[i]
            name = "choukai-m%d-q%d%s" % (cur_m["no"], cur_q["label"], ext)
            with open(os.path.join(IMGDIR, name), "wb") as f:
                f.write(blob)
            cur_q["img"] = "../images/%s/%s" % (TAG, name)
        if not t:
            continue
        if t.startswith("答案"):      # từ đây trở xuống là bảng đáp án
            break
        m = RX_SEC.match(t)
        if m:
            flush_passage(cur_q)
            key = SEC_OF.get(t[:4])
            cur_sec = dict(SECTIONS[key], key=key, mondai=[])
            secs.append(cur_sec)
            cur_m = cur_q = None
            continue
        if cur_sec is None:
            continue
        m = RX_MONDAI.match(t)
        if m:
            flush_passage(cur_q)
            cur_m = {"no": int(m.group(1)), "instruction": t,
                     "passage": "", "questions": []}
            cur_sec["mondai"].append(cur_m)
            cur_q = None
            continue
        if cur_m is None:
            continue
        m = RX_OPT.match(t)
        if m and cur_q is not None and len(cur_q["opts"]) == int(m.group(1)) - 1:
            cur_q["opts"].append(m.group(2).strip())
            continue
        m = RX_Q.match(t) if cur_sec["key"] != "choukai" else RX_BAN.match(t)
        if m:
            label = int(m.group(1))
            cur_q = {"label": label, "q": m.group(2).strip(), "opts": [],
                     "answer": answers.get((cur_sec["key"], cur_m["no"], label))}
            if cur_sec["key"] == "choukai":
                cur_q["audio"] = AUDIO
            flush_passage(cur_q)
            cur_m["questions"].append(cur_q)
            continue
        if t.startswith("※"):        # chú thích của người gõ lại, không phải đề
            continue
        # câu đối thoại in nhiều dòng (A「…」 rồi B「…」): còn chưa tới lựa chọn
        # thì dòng này vẫn là phần đề bài, không phải bài đọc của 問題 sau
        if cur_q is not None and not cur_q["opts"]:
            cur_q["q"] = (cur_q["q"] + " " + t).strip()
            continue
        buf.append(t)
    flush_passage(cur_q)

    # bảng 問題7 (案内) nằm trong table của docx, không phải paragraph
    tbl = "\n".join(" ｜ ".join(c.text.strip().replace("\n", " ") for c in r.cells)
                    for r in doc.tables[0].rows)
    m7 = next(m for s in secs if s["key"] == "bunpou"
              for m in s["mondai"] if m["no"] == 7)
    m7["passage"] = (m7["passage"] + "\n" + tbl).strip()

    cho = next(s for s in secs if s["key"] == "choukai")
    # 問題3 / 問題5: đề trắng, số câu lấy theo bảng đáp án đúng format JLPT
    for no, (count, nopt) in sorted(AUDIO_ONLY.items()):
        mon = next((m for m in cho["mondai"] if m["no"] == no), None)
        if mon is None:
            continue
        for lb in range(1, count + 1):
            if any(q["label"] == lb for q in mon["questions"]):
                continue
            mon["questions"].append({
                "label": lb, "q": "", "opts": [""] * nopt, "audio": AUDIO,
                "answer": answers.get(("choukai", no, lb))})
        mon["questions"].sort(key=lambda q: q["label"])
    # 問題1 có câu mà lựa chọn là tranh, 問題4 thì tranh chính là đề bài
    for mon in cho["mondai"]:
        nopt = 3 if mon["no"] in (4, 5) else 4
        for q in mon["questions"]:
            if not q["opts"]:
                q["opts"] = [""] * nopt

    for s in secs:
        for mon in s["mondai"]:
            if not mon["passage"]:
                del mon["passage"]
    return [{"id": TAG, "title": TITLE, "sections": secs}], answers


if __name__ == "__main__":
    exams, answers = parse()
    tot = miss = 0
    for s in exams[0]["sections"]:
        print("[%s] %s" % (s["key"], s["name"]))
        for m in s["mondai"]:
            n = len(m["questions"])
            bad = [q["label"] for q in m["questions"] if not q["answer"]]
            noopt = sum(1 for q in m["questions"] if not any(q["opts"]))
            tot += n
            miss += len(bad)
            print("   問題%d: %2d câu | thiếu đáp án %s | %d câu lựa chọn trống | %s"
                  % (m["no"], n, bad or "-", noopt,
                     "passage %d ký tự" % len(m["passage"]) if m.get("passage")
                     else "không có bài đọc"))
    imgs = [q["img"] for s in exams[0]["sections"] for m in s["mondai"]
            for q in m["questions"] if q.get("img")]
    print("\ntổng %d câu, thiếu đáp án %d, ảnh %d" % (tot, miss, len(imgs)))
    print("đáp án đọc được từ bảng: %d" % len(answers))
    tmp = OUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(exams, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, OUT)
    print("ghi: %s" % OUT)
