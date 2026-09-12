# -*- coding: utf-8 -*-
import sys, io, json, os, re
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

here = os.path.dirname(os.path.abspath(__file__))
tag = sys.argv[1]
want = sys.argv[2] if len(sys.argv) > 2 else None
secs = json.load(open(os.path.join(here, "exam_parsed_%s.json" % tag), encoding="utf-8"))
for s in secs:
    if want and s["key"] != want:
        continue
    print("#### SECTION", s["key"])
    for m in s["mondai"]:
        print("== 問題", m["no"], "|", re.sub(r"\s+", " ", m["instruction"])[:80])
        if m["intro"]:
            txt = re.sub(r"\s+", " ", " ".join(m["intro"]))
            print("   [passage]", txt[:1100])
        for q in m["questions"]:
            if len(q["opts"]) != 4:
                continue
            print(f"  {q['n']}) {re.sub(r'  +', ' ', q['q'])[:200]}")
            print("      " + " | ".join(f"{i+1}.{o}" for i, o in enumerate(q["opts"])))
