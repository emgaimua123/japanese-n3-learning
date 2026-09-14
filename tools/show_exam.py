# -*- coding: utf-8 -*-
"""In một đề trong exams.json ra dạng đọc được, để đối chiếu với đề gốc.

    cd tools && python show_exam.py 2021-07 > de.txt

Đáp án đánh dấu bằng ✔ ngay trước lựa chọn. 【】 là chỗ đề gạch chân.
"""
import io
import json
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

here = os.path.dirname(os.path.abspath(__file__))
EXAMS = os.path.join(here, "..", "exams.json")


def show(ex):
    print("=" * 70)
    print("%s — %s" % (ex["id"], ex["title"]))
    for s in ex["sections"]:
        tot = sum(len(m["questions"]) for m in s["mondai"])
        print("\n" + "=" * 70)
        print("%s  %s  (%d phút) — %d câu" % (s["name"], s["jp"], s["minutes"], tot))
        for m in s["mondai"]:
            print("\n" + "-" * 70)
            print("問題%s  %s" % (m["no"], (m.get("instruction") or "").lstrip("【問題0123456789】")))
            if m.get("passage"):
                print("\n[bài đọc chung]")
                print(m["passage"])
            for q in m["questions"]:
                print()
                if q.get("passage"):
                    print("[bài đọc của câu này]")
                    print(q["passage"])
                print("câu %s (số trong app: %s)%s" % (
                    q.get("label"), q.get("n"), "  [có hình]" if q.get("img") else ""))
                if (q.get("q") or "").strip():
                    print("   %s" % q["q"])
                elif not q.get("img"):
                    print("   (đề không in đề bài — nghe audio)")
                for i, o in enumerate(q["opts"], 1):
                    mark = "✔" if q.get("answer") == i else " "
                    txt = str(o).strip() or "(đề không in — nghe audio)"
                    print("   %s %d) %s" % (mark, i, txt))
                if q.get("answer") is None:
                    print("     !! chưa có đáp án")


if __name__ == "__main__":
    exams = json.load(open(EXAMS, encoding="utf-8"))
    want = sys.argv[1] if len(sys.argv) > 1 else None
    for ex in exams:
        if want is None or ex["id"] == want:
            show(ex)
