# -*- coding: utf-8 -*-
import sys, io, glob, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TAGS = [("7_2021", "2021-07"), ("T7-2022", "2022-07"), ("T12-2022", "2022-12"),
        ("T7-2023", "2023-07"), ("12.2023", "2023-12")]
files = {}
for p in glob.glob(r"C:\Users\Admin\Downloads\*.pdf"):
    b = os.path.basename(p)
    for key, tag in TAGS:
        if key in b:
            files[tag] = p
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exam_files.json")
json.dump(files, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in sorted(files):
    print(k, "->", os.path.basename(files[k]))
