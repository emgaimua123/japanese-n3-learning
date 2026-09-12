# -*- coding: utf-8 -*-
"""Turn parsed exams into exams.json in the shape the app expects."""
import sys, io, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from parse_exam2 import parse

here = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\Admin\Coding\GitHub\japanese-n3-learning\exams.json"
ANSWERS = os.path.join(here, "..", "exam_answers.json")

SECTIONS = {
    "moji":    {"name": "Từ vựng – Chữ Hán", "jp": "言語知識（文字・語彙）", "minutes": 30},
    "bunpou":  {"name": "Ngữ pháp – Đọc hiểu", "jp": "言語知識（文法）・読解", "minutes": 70},
    "choukai": {"name": "Nghe hiểu", "jp": "聴解", "minutes": 40},
}
TAGS = {"2022-07": "Đề thi tháng 7/2022",
        "2022-12": "Đề thi tháng 12/2022",
        "2023-07": "Đề thi tháng 7/2023"}


def clean(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    return t


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
