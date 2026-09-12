# -*- coding: utf-8 -*-
"""Reading PDF (chapters 5-9) -> reading_raw.json: passages, questions, options, tips."""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pdfplumber

PATH = r"C:\Users\Admin\Downloads\20260320110812_GG N3 - DOCHIEU- C1C9 (260320).pdf"
OUT = r"C:\Users\Admin\AppData\Local\Temp\claude\C--Users-Admin-Coding-GitHub-japanese-n3-learning\fad933dd-dc1d-466d-ba36-cb205e37fcde\scratchpad\reading_raw.json"

CIRC = "①②③④⑤⑥⑦⑧⑨⑩"
PRAC = "❶❷❸❹❺❻❼➊➋➌➍➎➏➐"
JP = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
LAT = re.compile(r"[0-9A-Za-zÀ-ỹ]")


def join_line(words):
    out, prev = "", None
    for w in sorted(words, key=lambda w: w["x0"]):
        t = w["text"]
        if not t:
            continue
        if prev is not None:
            if (LAT.search(prev[-1]) and LAT.search(t[0])) or False:
                out += " "
        out += t
        prev = t
    return re.sub(r"\s+", " ", out).strip()


def group_lines(words, tol=6):
    lines = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        for ln in lines:
            if abs(ln["top"] - w["top"]) <= tol:
                ln["w"].append(w)
                break
        else:
            lines.append({"top": w["top"], "w": [w]})
    return lines


def main():
    chapters = {}
    with pdfplumber.open(PATH) as pdf:
        for pi, page in enumerate(pdf.pages):
            if pi + 1 < 23:
                continue
            words = page.extract_words(extra_attrs=["size"])
            ch = next((int(w["text"]) for w in words
                       if w["size"] > 25 and w["x0"] < 60 and w["text"].isdigit()), None)
            body = [w for w in words if 45 < w["top"] < 800 and 9.5 <= w["size"] < 25]
            lines = [join_line(l["w"]) for l in group_lines(body)]
            lines = [l for l in lines if l and l not in ("ĐỌC HIỂU",)]
            if ch is None:
                ch = chapters and max(chapters) or 5
            chapters.setdefault(ch, []).extend(lines)

    out = []
    for ch in sorted(chapters):
        lines = chapters[ch]
        # everything before the first 練習 is the chapter's technique section
        first = next((i for i, l in enumerate(lines) if l.startswith("練習")), len(lines))
        tips = [l for l in lines[:first] if l]
        blocks, cur = [], None
        for l in lines[first:]:
            if l.startswith("練習"):
                cur = {"label": l, "lines": []}
                blocks.append(cur)
            elif cur is not None:
                cur["lines"].append(l)
        for bi, b in enumerate(blocks):
            passage, questions, q = [], [], None
            for l in b["lines"]:
                if re.match(r"^問\s*[いに0-9０-９]", l):
                    q = {"q": re.sub(r"^問\s*[いに]?\s*[0-9０-９]?\s*", "", l), "opts": []}
                    questions.append(q)
                elif l and l[0] in CIRC and q is not None:
                    q["opts"].append(l[1:].strip())
                elif q is not None and q["opts"]:
                    q["opts"][-1] += l          # wrapped option
                elif q is not None:
                    q["q"] += l                 # wrapped question
                else:
                    passage.append(l)
            out.append({"chapter": ch, "no": bi + 1, "label": b["label"],
                        "passage": passage, "questions": questions,
                        "tips_raw": tips if bi == 0 else []})
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("reading blocks:", len(out), "| questions:", sum(len(b["questions"]) for b in out))
    for ch in sorted({b["chapter"] for b in out}):
        bs = [b for b in out if b["chapter"] == ch]
        print(f"  chapter {ch}: {len(bs)} bài đọc, {sum(len(b['questions']) for b in bs)} câu hỏi, "
              f"độ dài TB {sum(len(''.join(b['passage'])) for b in bs)//max(1,len(bs))} chữ")
    b = out[0]
    print("=" * 60)
    print(b["label"], "| chapter", b["chapter"])
    print("passage:", "".join(b["passage"])[:150])
    for q in b["questions"]:
        print("  Q:", q["q"][:70])
        for i, o in enumerate(q["opts"]):
            print(f"    {CIRC[i]} {o[:60]}")


main()
