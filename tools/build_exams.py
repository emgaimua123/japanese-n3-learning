# -*- coding: utf-8 -*-
"""Turn parsed exams into exams.json in the shape the app expects."""
import sys, io, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from parse_exam2 import parse

here = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(here, "..", "exams.json")
ANSWERS = os.path.join(here, "..", "exam_answers.json")
# dữ liệu nhập tay (đề scan, bài đọc là ảnh, audio phần nghe...) - được merge
# đè lên kết quả trích từ PDF nên chạy lại script KHÔNG làm mất nó
MANUAL = os.path.join(here, "..", "exams_manual.json")

SECTIONS = {
    "moji":    {"name": "Từ vựng – Chữ Hán", "jp": "言語知識（文字・語彙）", "minutes": 30},
    "bunpou":  {"name": "Ngữ pháp – Đọc hiểu", "jp": "言語知識（文法）・読解", "minutes": 70},
    "choukai": {"name": "Nghe hiểu", "jp": "聴解", "minutes": 40},
}
# đề nào trích được text thì thêm vào đây; id phải khớp key trong exam_files.json
TAGS = {"2022-07": "Đề thi tháng 7/2022",
        "2022-12": "Đề thi tháng 12/2022",
        "2023-07": "Đề thi tháng 7/2023"}


def clean(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    return t


def merge_manual(exams):
    """Gộp exams_manual.json vào kết quả trích tự động.

    Khớp theo: đề `id` -> phần `key` -> 問題 `no` -> câu `label`.
    Có sẵn thì cập nhật (đè từng trường, giữ trường cũ không nhắc tới),
    chưa có thì thêm mới. Nhờ vậy nhập tay không bị mất khi chạy lại script.
    """
    if not os.path.exists(MANUAL):
        return exams, 0
    try:
        manual = json.load(open(MANUAL, encoding="utf-8"))
    except ValueError as e:
        raise SystemExit("exams_manual.json lỗi cú pháp JSON: %s" % e)
    if not isinstance(manual, list):
        raise SystemExit("exams_manual.json phải là một mảng các đề")

    changed = 0
    by_id = {e["id"]: e for e in exams}
    for mex in manual:
        ex = by_id.get(mex["id"])
        if ex is None:
            exams.append(mex)
            by_id[mex["id"]] = mex
            changed += sum(len(m["questions"]) for s in mex.get("sections", [])
                           for m in s.get("mondai", []))
            continue
        if mex.get("title"):
            ex["title"] = mex["title"]
        secs = {s["key"]: s for s in ex["sections"]}
        for msec in mex.get("sections", []):
            sec = secs.get(msec["key"])
            if sec is None:
                ex["sections"].append(msec)
                secs[msec["key"]] = msec
                changed += sum(len(m["questions"]) for m in msec.get("mondai", []))
                continue
            for k in ("name", "jp", "minutes"):
                if k in msec:
                    sec[k] = msec[k]
            mons = {m["no"]: m for m in sec["mondai"]}
            for mmon in msec.get("mondai", []):
                mon = mons.get(mmon["no"])
                if mon is None:
                    sec["mondai"].append(mmon)
                    mons[mmon["no"]] = mmon
                    changed += len(mmon.get("questions", []))
                    continue
                for k in ("instruction", "passage"):
                    if k in mmon:
                        mon[k] = mmon[k]
                qs = {q.get("label", q["n"]): q for q in mon["questions"]}
                for mq in mmon.get("questions", []):
                    lbl = mq.get("label", mq.get("n"))
                    if lbl in qs:
                        qs[lbl].update(mq)
                    else:
                        mon["questions"].append(mq)
                    changed += 1
        # đánh số lại toàn phần sau khi gộp để navigator vẫn là 1..n
        for sec in ex["sections"]:
            sec["mondai"].sort(key=lambda m: (m["no"] if isinstance(m["no"], int) else 99))
            seq = 0
            for m in sec["mondai"]:
                for q in m["questions"]:
                    seq += 1
                    q.setdefault("label", q.get("n"))
                    q["n"] = seq
    return exams, changed


def build():
    answers = {}
    if os.path.exists(ANSWERS):
        answers = json.load(open(ANSWERS, encoding="utf-8"))
    exams = []
    for tag, title in TAGS.items():
        secs = parse(tag)
        out_secs = []
        for s in secs:
            meta = SECTIONS[s["key"]]
            mondai = []
            seen_no = set()
            for m in s["mondai"]:
                # a repeated 問題 number means the extractor split one block in two;
                # keep the first, drop the rest so answer keys stay unambiguous
                if s["key"] != "choukai":
                    if m["no"] in seen_no:
                        continue
                    seen_no.add(m["no"])
                # word-order items lose the position of the ★ blank when the PDF
                # is flattened to text, so they cannot be marked - skip the whole set
                if "★" in m["instruction"] or any("★" in q["q"] for q in m["questions"]):
                    continue
                # 文字・語彙 only ever has 問題1-5; anything numbered higher here is
                # a grammar block the extractor put in the wrong section
                if s["key"] == "moji" and isinstance(m["no"], int) and m["no"] > 5:
                    continue
                qs = []
                for q in m["questions"]:
                    if len(q["opts"]) != 4:
                        continue
                    key = "%s/%s/%s" % (tag, s["key"], q["n"])
                    ans = answers.get(key)
                    # only ship questions we can actually mark: the reading passages
                    # that live in the PDF as images, and the ★ word-order items
                    # (which lose the blank's position in extraction), are dropped
                    if ans is None and s["key"] != "choukai":
                        continue
                    qs.append({"n": q["n"], "q": clean(q["q"]),
                               "opts": [clean(o) for o in q["opts"]],
                               "answer": ans})
                if not qs:
                    continue
                mondai.append({"no": m["no"], "instruction": clean(m["instruction"]),
                               "passage": clean(" ".join(m["intro"]))[:2600],
                               "questions": qs})
            if not mondai:
                continue
            # renumber sequentially within the section so the navigator is 1..n
            seq = 0
            for m in mondai:
                for q in m["questions"]:
                    seq += 1
                    q["label"] = q["n"]
                    q["n"] = seq
            out_secs.append({"key": s["key"], "name": meta["name"], "jp": meta["jp"],
                             "minutes": meta["minutes"], "mondai": mondai})
        exams.append({"id": tag, "title": title, "sections": out_secs})

    exams, merged = merge_manual(exams)
    if merged:
        print("đã gộp %d câu từ exams_manual.json" % merged)
    elif os.path.exists(MANUAL):
        print("exams_manual.json rỗng - không có gì để gộp")

    json.dump(exams, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("exams:", len(exams))
    for e in exams:
        tot = sum(len(m["questions"]) for s in e["sections"] for m in s["mondai"])
        withans = sum(1 for s in e["sections"] for m in s["mondai"]
                      for q in m["questions"] if q["answer"] is not None)
        print(f"  {e['id']} {e['title']}: {tot} câu ({withans} đã có đáp án)")
        for s in e["sections"]:
            n = sum(len(m["questions"]) for m in s["mondai"])
            print(f"     [{s['key']}] {s['name']} ({s['minutes']}p): {n} câu / {len(s['mondai'])} mondai")


if __name__ == "__main__":
    build()
