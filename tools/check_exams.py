# -*- coding: utf-8 -*-
"""Soi lỗi trong exams.json — chạy sau mỗi lần build để biết chỗ nào cần đối chiếu lại đề gốc.

    cd tools && python check_exams.py [id đề]

Không sửa gì, chỉ báo. Ba mức:
  LỖI   — chắc chắn sai, app sẽ hiển thị hỏng hoặc chấm sai
  NGỜ   — có thể sai, nên mở đề gốc xem lại
  TIN   — thông tin, không phải lỗi
"""
import io
import json
import os
import re
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

here = os.path.dirname(os.path.abspath(__file__))
EXAMS = os.path.join(here, "..", "exams.json")
IMGROOT = os.path.join(here, "..", "images")
AUDIOROOT = os.path.join(here, "..", "audio")

# số câu chuẩn của từng 問題 theo format JLPT N3
FORMAT = {
    "moji":    {1: 8, 2: 6, 3: 11, 4: 5, 5: 5},
    "bunpou":  {1: 13, 2: 5, 3: 4, 4: 4, 5: 6, 6: 4, 7: 2},
    "choukai": {1: 6, 2: 6, 3: 3, 4: 4, 5: 9},
}
# số lựa chọn chuẩn: 問題4 và 問題5 phần nghe chỉ có 3
OPTS = {("choukai", 4): 3, ("choukai", 5): 3}
JP = re.compile(r"[぀-ヿ一-鿿]")


def check(ex):
    out = []
    add = lambda lv, s: out.append((lv, s))
    for sec in ex["sections"]:
        k = sec["key"]
        seen_n = []
        for m in sec["mondai"]:
            where = "[%s] 問題%s" % (k, m["no"])
            want = FORMAT.get(k, {}).get(m["no"])
            got = len(m["questions"])
            if want and got != want:
                add("NGỜ", "%s: %d câu, format chuẩn là %d" % (where, got, want))
            labels = [q.get("label") for q in m["questions"]]
            if len(set(labels)) != len(labels):
                add("LỖI", "%s: số câu gốc bị trùng %s" % (where, labels))
            nopt = OPTS.get((k, m["no"]), 4)
            for q in m["questions"]:
                w = "%s câu %s" % (where, q.get("label"))
                if q.get("n") is None:
                    add("LỖI", "%s: thiếu số thứ tự n (navigator sẽ hiện undefined)" % w)
                else:
                    seen_n.append(q["n"])
                opts = q.get("opts")
                if not isinstance(opts, list):
                    add("LỖI", "%s: không có mảng lựa chọn" % w)
                    continue
                if len(opts) != nopt:
                    add("LỖI", "%s: %d lựa chọn, phải là %d" % (w, len(opts), nopt))
                blank = sum(1 for o in opts if not str(o).strip())
                if blank and blank != len(opts):
                    add("LỖI", "%s: %d/%d lựa chọn bị trống" % (w, blank, len(opts)))
                if blank == len(opts) and not q.get("img") and k != "choukai":
                    add("LỖI", "%s: lựa chọn trống mà không phải phần nghe" % w)
                if len(set(map(str, opts))) != len(opts) and not blank:
                    add("NGỜ", "%s: có hai lựa chọn giống hệt nhau" % w)
                a = q.get("answer")
                if a is not None and not (1 <= a <= len(opts)):
                    add("LỖI", "%s: đáp án %s nằm ngoài 1–%d" % (w, a, len(opts)))
                if a is None:
                    add("TIN", "%s: chưa có đáp án nên không chấm điểm" % w)
                txt = q.get("q") or ""
                # phần nghe thì câu hỏi đọc bằng audio, đề không in gì là bình thường
                if k != "choukai" and not txt.strip() and not q.get("img") and not (
                        m.get("passage") or q.get("passage")):
                    add("NGỜ", "%s: không có đề bài, không ảnh, không bài đọc" % w)
                if k == "choukai" and not q.get("audio"):
                    add("NGỜ", "%s: phần nghe mà chưa gắn audio" % w)
                if txt and not JP.search(txt):
                    add("NGỜ", "%s: đề bài không có chữ Nhật: %r" % (w, txt[:40]))
                for o in opts:
                    if str(o).strip() and not JP.search(str(o)) and not re.fullmatch(
                            r"[\W\dA-Za-z ]+", str(o)):
                        add("NGỜ", "%s: lựa chọn lạ %r" % (w, str(o)[:30]))
                if q.get("img"):
                    p = os.path.join(IMGROOT, *q["img"].split("/")[2:])
                    if not os.path.isfile(p):
                        add("LỖI", "%s: thiếu file ảnh %s" % (w, q["img"]))
                if q.get("audio"):
                    p = os.path.join(AUDIOROOT, *q["audio"].split("/")[2:])
                    if not os.path.isfile(p):
                        add("LỖI", "%s: thiếu file audio %s" % (w, q["audio"]))
            pas = m.get("passage") or ""
            if pas and len(pas) > 2600:
                add("NGỜ", "%s: bài đọc %d ký tự, dài bất thường" % (where, len(pas)))
            if k == "bunpou" and m["no"] in (5, 6, 7) and not pas:
                add("NGỜ", "%s: dạng đọc hiểu mà không có bài đọc" % where)
        if seen_n and sorted(seen_n) != list(range(1, len(seen_n) + 1)):
            add("LỖI", "[%s] số thứ tự n không liên tục 1..%d" % (k, len(seen_n)))
    return out


if __name__ == "__main__":
    exams = json.load(open(EXAMS, encoding="utf-8"))
    want = sys.argv[1] if len(sys.argv) > 1 else None
    total = {"LỖI": 0, "NGỜ": 0, "TIN": 0}
    for ex in exams:
        if want and ex["id"] != want:
            continue
        res = check(ex)
        n = {lv: sum(1 for l, _ in res if l == lv) for lv in total}
        print("=" * 64)
        print("%s — %d lỗi, %d chỗ nghi ngờ, %d câu chưa chấm điểm"
              % (ex["id"], n["LỖI"], n["NGỜ"], n["TIN"]))
        for lv in ("LỖI", "NGỜ"):
            for l, s in res:
                if l == lv:
                    print("  %-4s %s" % (l, s))
            total[lv] += n[lv]
        total["TIN"] += n["TIN"]
    print("=" * 64)
    print("TỔNG: %d lỗi, %d chỗ nghi ngờ, %d câu chưa có đáp án"
          % (total["LỖI"], total["NGỜ"], total["TIN"]))
    sys.exit(1 if total["LỖI"] else 0)
