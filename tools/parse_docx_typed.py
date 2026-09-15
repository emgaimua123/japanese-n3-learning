# -*- coding: utf-8 -*-
"""Trích đề JLPT từ bản gõ lại .docx (loại do chủ dự án cung cấp).

    cd tools && python parse_docx_typed.py [id đề ...]

Thay cho `parse_docx_2023.py` cũ: mỗi bản gõ lại trình bày một kiểu nên chỗ khác
nhau gom hết vào bảng `EXAMS`, phần xử lý dùng chung. Đề 2021-07 vẫn có bộ riêng
(`parse_docx_2021.py`) vì bố cục lệch hẳn: có mốc 「第N部分」 và bảng đáp án ở cuối.

Khác nhau giữa hai bản đang hỗ trợ:

| | 2023-12 | 2023-07 |
|---|---|---|
| mốc phần thi | không có, nhận ra nhờ số 問題 quay về 1 | có dòng 文字語彙 / 文法・読解 / 聴解 |
| số câu | `1.` | `1)` |
| số câu phần nghe | `1ばん` | `1 番` (lẫn lộn nửa/toàn rộng) |
| 問題 phần nghe | không in, phải suy ra | in đủ 問題1–5 |
| ảnh 問題4 nghe | 2 ảnh chụp trang, mỗi ảnh 2 câu | 4 ảnh, mỗi câu một ảnh |

Kết quả ghi ra `tools/exam_<id>.json` theo schema của `exams.json` (HANDOFF §7),
để gộp vào `exams_manual.json`. Không file nào kèm đáp án — đáp án nhập riêng.
"""
import io
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import docx
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(os.path.expanduser("~"), "Downloads")

EXAMS = {
    "2023-12": {
        "file": "JLPT_N3_12_2023_FIXED.docx",
        "title": "Đề thi tháng 12/2023",
        "q": r"^(\d{1,2})[\.．][　 ]*(.*)$",
        "q_bare": None,
        "ban": r"^(\d{1,2})ばん",
        "sec_marks": None,                 # suy ra từ số 問題 quay về 1
        "choukai_mark": "聴解",
        "m4_mark": "絵の問題",             # 問題4 không in tiêu đề, chỉ có dòng này
        "m4_split": [(1, 2), (3, 4)],      # mỗi ảnh chụp cả trang gồm 2 câu
        "mondai_fix": {},
        "skip": ("Bản chuyển sang text", "2023 年", "文法・読解",
                 "言語知識（文字・語彙）", "言語知識（文法）・読解"),
    },
    "2022-07": {
        "file": "JLPT_N3_07_2022_text_gach_chan.docx",
        "title": "Đề thi tháng 7/2022",
        "q": r"^([0-9０-９]{1,2})[)）][　 ]*(.*)$",
        # phần đọc đánh số kiểu khác hẳn: "23 ", "24．", "25. ", "33.  "
        "q_bare": r"^([0-9０-９]{1,2})[\s　]*[.．]?[\s　]*(\S.*)$",
        "ban": r"^([0-9０-９]{1,2})[　 ]*番",
        # 文法 và 読解 in thành hai tiêu đề nhưng là MỘT phần thi
        "sec_marks": {"文字・語彙": "moji", "文法": "bunpou", "読解": "bunpou",
                      "聴解": "choukai"},
        "choukai_mark": None,
        "m4_mark": None,
        "m4_split": None,
        # bản gõ chép nhầm 問題2 (dạng ★) thành 問題8
        "mondai_fix": {("bunpou", 8): 2},
        "skip": ("Bản chuyển sang text", "2022 年"),
    },
    "2023-07": {
        "file": "JLPT_N3_07_2023_text_gach_chan.docx",
        "title": "Đề thi tháng 7/2023",
        "q": r"^([0-9０-９]{1,2})[)）][　 ]*(.*)$",
        # phần đọc bỏ dấu ngoặc: "24 頑張ろうとあるが…". Chỉ nhận dạng trần khi số
        # lớn hơn 4 (khỏi đụng dòng lựa chọn) và đúng bằng số câu kế tiếp — nếu
        # không thì dòng bài đọc "8 月 11 日…" cũng thành câu 8.
        "q_bare": r"^([0-9０-９]{1,2})[　 ]+(\S.*)$",
        "ban": r"^([0-9０-９]{1,2})[　 ]*番",
        "sec_marks": {"文字語彙": "moji", "文法・読解": "bunpou", "聴解": "choukai"},
        "choukai_mark": None,
        "m4_mark": None,                   # có tiêu đề 問題4 hẳn hoi
        "m4_split": None,                  # 4 ảnh, mỗi câu một ảnh
        "mondai_fix": {},
        "skip": ("Bản chuyển sang text",),
    },
}

SECTIONS = {
    "moji":    {"name": "Từ vựng – Chữ Hán", "jp": "言語知識（文字・語彙）", "minutes": 30},
    "bunpou":  {"name": "Ngữ pháp – Đọc hiểu", "jp": "言語知識（文法）・読解", "minutes": 70},
    "choukai": {"name": "Nghe hiểu", "jp": "聴解", "minutes": 40},
}
# bản gõ lại lẫn lộn 問題 với 間題 (nhận dạng sai chữ)
RX_MONDAI = re.compile(r"^[問間]題[　 ]?([0-9０-９])(?![0-9０-９])")
RX_BARE = re.compile(r"^(\d{1,2})$")
# Lựa chọn viết đủ kiểu: "1 あ", "１. あ", và dính liền "1「大きな家」と".
# Không bắt buộc dấu cách — an toàn vì chỗ dùng còn đòi số phải đúng bằng
# lựa chọn kế tiếp, nên dòng như "23 「私」は…" không lọt vào.
RX_OPT1 = re.compile(r"^([1-4１-４])[\s　]*[.．)）]?[\s　]*(\S.*)$")
FW = str.maketrans("０１２３４５６７８９", "0123456789")
PER_Q_PASSAGE = {("bunpou", 4)}
AFTER_Q_PASSAGE = {("bunpou", 7)}
AUDIO_ONLY = {3: (3, 4), 5: (9, 3)}        # 問題: (số câu, số lựa chọn)
# dòng đầu trang lặp lại ở mọi trang, không phải nội dung đề
RX_HEADER = re.compile(r"^[０-９\d]{4}\s*年.*日本語能力試験")


def para_text(p):
    """Văn bản một đoạn, giữ hai thứ mà `.text` làm mất:

    - từ được gạch chân trong đề  -> bọc 【】
    - ô trống của câu sắp xếp ★   -> `＿＿＿`

    Đề 7/2022 không gõ ký tự gạch nào cho ô trống: mỗi ô chỉ là mấy khoảng
    trắng CÓ GẠCH CHÂN. Đọc bằng `.text` là mất sạch, không còn biết ★ nằm ở ô
    thứ mấy — mà đáp án phụ thuộc đúng chỗ đó.
    """
    out = []
    for r in p.runs:
        if not r.underline:
            out.append(r.text)
        elif "★" in r.text:
            out.append(" ★ ")
        elif not r.text.strip():
            out.append(" ＿＿＿ ")
        else:
            out.append("【%s】" % r.text)
    return re.sub(r"[ \t]+", " ", "".join(out)).strip()


def four_on_one_line(t):
    """'1 あ 2 い 3 う 4 え' -> bốn lựa chọn; không đúng dạng thì None."""
    pos, frm = [], 0
    for n in range(1, 5):
        m = re.compile(r"(?:^|[\s　])%d[\s　]" % n).search(t, frm)
        if not m:
            return None
        pos.append(m)
        frm = m.end()
    out = []
    for k in range(4):
        e = pos[k + 1].start() if k < 3 else len(t)
        out.append(t[pos[k].end():e].strip())
    return out if all(out) else None


def split_panels(blob, count):
    """Ảnh chụp cả trang -> cắt lấy `count` khung tranh theo khoảng trắng giữa chúng."""
    im = Image.open(io.BytesIO(blob)).convert("L")
    w, h = im.size
    px = im.load()
    thr = max(4, w // 4 // 40)
    runs, start = [], None
    for y in range(h):
        dark = sum(1 for x in range(0, w, 4) if px[x, y] < 160)
        if dark > thr and start is None:
            start = y
        elif dark <= thr and start is not None:
            runs.append([start, y])
            start = None
    if start is not None:
        runs.append([start, h])
    merged = []
    for a, b in runs:
        if merged and a - merged[-1][1] < 30:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    panels = sorted([r for r in merged if r[1] - r[0] > 300],
                    key=lambda r: r[1] - r[0], reverse=True)[:count]
    panels.sort()
    if len(panels) != count:
        raise SystemExit("ảnh: tìm được %d khung, cần %d" % (len(panels), count))
    return [im.crop((0, max(0, a - 12), w, min(h, b + 12))) for a, b in panels]


def parse(tag):
    cfg = EXAMS[tag]
    doc = docx.Document(os.path.join(DL, cfg["file"]))
    rx_q = re.compile(cfg["q"])
    rx_bare_q = re.compile(cfg["q_bare"]) if cfg.get("q_bare") else None
    last_lb = [0]
    rx_ban = re.compile(cfg["ban"])
    imgdir = os.path.join(here, "..", "images", tag)
    audio = "../audio/%s/choukai.mp3" % tag

    imgs = {}
    for i, p in enumerate(doc.paragraphs):
        ids = re.findall(r'r:embed="([^"]+)"', p._p.xml)
        if ids:
            imgs[i] = doc.part.related_parts[ids[0]].blob

    secs, cur_sec, cur_m, cur_q = [], None, None, None
    buf, pend_img = [], []

    def new_sec(key):
        s = dict(SECTIONS[key], key=key, mondai=[])
        secs.append(s)
        return s

    def flush(target_q):
        nonlocal buf
        if not buf or cur_m is None:
            buf = []
            return
        text = "\n".join(buf).strip()
        if (cur_sec["key"], cur_m["no"]) in PER_Q_PASSAGE and target_q is not None:
            target_q["passage"] = text
        else:
            cur_m["passage"] = (cur_m.get("passage", "") + "\n" + text).strip()
        buf = []

    for i, p in enumerate(doc.paragraphs):
        t = para_text(p)
        # ảnh: chỉ phần nghe mới dùng, ảnh trong phần đọc chỉ là icon trang trí
        if i in imgs and cur_sec and cur_sec["key"] == "choukai":
            if cur_m and cur_m["no"] == 4:
                pend_img.append(imgs[i])
            elif cur_q is not None:
                os.makedirs(imgdir, exist_ok=True)
                name = "choukai-m%d-q%d.png" % (cur_m["no"], cur_q["label"])
                open(os.path.join(imgdir, name), "wb").write(imgs[i])
                cur_q["img"] = "../images/%s/%s" % (tag, name)
        if not t or RX_HEADER.match(t) or t.startswith(cfg["skip"]):
            continue
        if cfg["sec_marks"] and t in cfg["sec_marks"]:
            flush(cur_q)
            k = cfg["sec_marks"][t]
            # 文法 và 読解 là hai tiêu đề của cùng một phần thi: gặp cái thứ
            # hai thì đi tiếp chứ không mở phần mới
            if cur_sec is None or cur_sec["key"] != k:
                cur_sec = new_sec(k)
                cur_m = cur_q = None
            continue
        if cfg["choukai_mark"] and t.startswith(cfg["choukai_mark"]) and not cfg["sec_marks"]:
            flush(cur_q)
            cur_sec = new_sec("choukai")
            cur_m = {"no": 1, "instruction": t, "questions": []}
            cur_sec["mondai"].append(cur_m)
            cur_q = None
            continue
        if cfg["m4_mark"] and t.startswith(cfg["m4_mark"]):
            flush(cur_q)
            cur_m = {"no": 4, "instruction":
                     "問題4 では、えを見ながら質問を聞いてください。やじるし（→）の人は何と"
                     "言いますか。1から3の中から、最もよいものを一つえらんでください。",
                     "questions": []}
            cur_sec["mondai"].append(cur_m)
            cur_q = None
            continue
        m = RX_MONDAI.match(t)
        if m:
            flush(cur_q)
            no = int(m.group(1).translate(FW))
            if cur_sec is not None:
                no = cfg.get("mondai_fix", {}).get((cur_sec["key"], no), no)
                # phần nghe in tiêu đề 問題N hai lần liền nhau (dòng tiêu đề
                # rồi tới dòng hướng dẫn) — lần thứ hai không mở 問題 mới
                if cur_m is not None and cur_m["no"] == no and not cur_m["questions"]:
                    cur_m["instruction"] = t
                    continue
            if cur_sec is None:
                cur_sec = new_sec("moji")
            elif not cfg["sec_marks"] and no == 1 and cur_sec["key"] == "moji":
                cur_sec = new_sec("bunpou")
            cur_m = {"no": no, "instruction": t, "questions": []}
            cur_sec["mondai"].append(cur_m)
            cur_q = None
            continue
        if cur_sec is None or cur_m is None:
            continue
        key = (cur_sec["key"], cur_m["no"])
        if cur_q is not None and len(cur_q["opts"]) < 4:
            # thử bốn-cái-một-dòng TRƯỚC, vì dòng đó cũng khớp dạng một-lựa-chọn-một-dòng
            if not cur_q["opts"]:
                four = four_on_one_line(t)
                if four:
                    cur_q["opts"] = four
                    continue
            om = RX_OPT1.match(t)
            if om and int(om.group(1).translate(FW)) == len(cur_q["opts"]) + 1:
                cur_q["opts"].append(om.group(2).strip())
                continue
        if cur_sec["key"] == "choukai":
            qm = rx_ban.match(t)
            if qm:
                lb = int(qm.group(1).translate(FW))
                if lb == 1 and cur_m["questions"] and cfg["m4_mark"]:
                    cur_m = {"no": cur_m["no"] + 1, "instruction": "", "questions": []}
                    cur_sec["mondai"].append(cur_m)
                cur_q = {"label": lb, "q": "", "opts": [], "answer": None, "audio": audio}
                cur_m["questions"].append(cur_q)
                continue
        else:
            qm = rx_q.match(t) or (RX_BARE.match(t) if key == ("bunpou", 3) else None)
            if not qm and rx_bare_q:
                bm = rx_bare_q.match(t)
                if bm:
                    n = int(bm.group(1).translate(FW))
                    if n > 4 and n == last_lb[0] + 1:
                        qm = bm
            if qm:
                body = qm.group(2).strip() if qm.lastindex and qm.lastindex > 1 else ""
                lb = int(qm.group(1).translate(FW))
                last_lb[0] = lb
                cur_q = {"label": lb, "q": body, "opts": [], "answer": None}
                flush(cur_q)
                cur_m["questions"].append(cur_q)
                continue
        # Dòng ※ chỉ bỏ ở phần nghe (ghi chú của người gõ: "選択肢は音声で読まれる").
        # Ở phần đọc, ※ là nội dung đề thật — đề 12/2023 câu 38 hỏi đúng dòng
        # "※…2,000円割引します" nên bỏ đi là câu đó thành không giải được.
        if cur_sec["key"] == "choukai" and (
                t.startswith("※") or t.replace("ー", "").replace("―", "").strip() == "メモ"):
            continue
        if cur_q is not None and not cur_q["opts"] and key not in AFTER_Q_PASSAGE:
            cur_q["q"] = (cur_q["q"] + " " + t).strip()
            continue
        buf.append(t)
    flush(cur_q)

    if doc.tables:
        tbl = "\n".join("\n".join(" ｜ ".join(c.text.strip().replace("\n", " ") for c in r.cells)
                                  for r in tb.rows) for tb in doc.tables)
        m7 = next((m for s in secs if s["key"] == "bunpou"
                   for m in s["mondai"] if m["no"] == 7), None)
        if m7:
            m7["passage"] = (m7.get("passage", "") + "\n" + tbl).strip()

    cho = next(s for s in secs if s["key"] == "choukai")
    m4 = next((m for m in cho["mondai"] if m["no"] == 4), None)
    if m4 is not None and pend_img:
        os.makedirs(imgdir, exist_ok=True)
        if cfg["m4_split"]:
            for blob, labels in zip(pend_img, cfg["m4_split"]):
                for panel, lb in zip(split_panels(blob, len(labels)), labels):
                    name = "choukai-m4-q%d.png" % lb
                    panel.save(os.path.join(imgdir, name), optimize=True)
                    m4["questions"].append({"label": lb, "q": "", "opts": ["", "", ""],
                                            "answer": None, "audio": audio,
                                            "img": "../images/%s/%s" % (tag, name)})
        else:
            for n, blob in enumerate(pend_img, 1):
                name = "choukai-m4-q%d.png" % n
                open(os.path.join(imgdir, name), "wb").write(blob)
                q = next((x for x in m4["questions"] if x["label"] == n), None)
                if q is None:
                    q = {"label": n, "q": "", "opts": ["", "", ""], "answer": None, "audio": audio}
                    m4["questions"].append(q)
                q["img"] = "../images/%s/%s" % (tag, name)
        m4["questions"].sort(key=lambda q: q["label"])

    # 問題3 / 問題5 phần nghe: đề trắng, vẫn tạo đủ số câu đúng format JLPT
    for no, (count, nopt) in AUDIO_ONLY.items():
        mon = next((m for m in cho["mondai"] if m["no"] == no), None)
        if mon is None:
            mon = {"no": no, "instruction":
                   "問題%d では、問題用紙に何もいんさつされていません。" % no, "questions": []}
            cho["mondai"].append(mon)
        for lb in range(1, count + 1):
            if not any(q["label"] == lb for q in mon["questions"]):
                mon["questions"].append({"label": lb, "q": "", "opts": [""] * nopt,
                                         "answer": None, "audio": audio})
        mon["questions"].sort(key=lambda q: q["label"])
    cho["mondai"].sort(key=lambda m: m["no"])
    for m in cho["mondai"]:
        for q in m["questions"]:
            if not q["opts"]:
                q["opts"] = [""] * (3 if m["no"] in (4, 5) else 4)
    for s in secs:
        for m in s["mondai"]:
            if not m.get("passage"):
                m.pop("passage", None)
    return {"id": tag, "title": cfg["title"], "sections": secs}


if __name__ == "__main__":
    for tag in (sys.argv[1:] or list(EXAMS)):
        ex = parse(tag)
        tot = 0
        print("==", tag)
        for s in ex["sections"]:
            print("  [%s]" % s["key"])
            for m in s["mondai"]:
                tot += len(m["questions"])
                print("     問題%d: %2d câu | %s" % (
                    m["no"], len(m["questions"]),
                    "passage %d ký tự" % len(m["passage"]) if m.get("passage") else "-"))
        print("  tổng %d câu" % tot)
        out = os.path.join(here, "exam_%s.json" % tag.replace("-", "_"))
        tmp = out + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as f:
            json.dump([ex], f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(tmp, out)
        print("  ghi:", out)
