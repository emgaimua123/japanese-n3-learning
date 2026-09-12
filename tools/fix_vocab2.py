# -*- coding: utf-8 -*-
"""Clean vocab entries where the PDF's POS column, Han-Viet reading, example
sentence or section header leaked into the meaning / hanviet fields."""
import sys, io, json, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vocab.json")
UP = "A-ZĐÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ"
POS_PFX = re.compile(r"^\s*[（(]\s*([VNA][^)）]{0,12}?)\s*[)）]\s*")
HV_PFX = re.compile(r"^([%s]{2,}(?:\s+[%s]{2,})*)\s+" % (UP, UP))
HV_ONLY = re.compile(r"^[%s]{2,}(?:\s+[%s]{2,})*$" % (UP, UP))
JP = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
HEADER = re.compile(r"\s*TỪ VỰNG.*$")

data = json.load(open(V, encoding="utf-8"))
changed_m, dropped, changed_hv = 0, 0, 0

for e in data:
    # --- hanviet: keep only the leading all-caps reading ---
    hv = (e.get("hanviet") or "").strip()
    if hv and not HV_ONLY.match(hv):
        m = HV_PFX.match(hv + " ")
        new_hv = m.group(1).strip() if m else ""
        if new_hv != hv:
            e["hanviet"] = new_hv
            changed_hv += 1

    # --- meanings ---
    out = []
    for orig in e["meanings"]:
        m = orig.split("・")[0]              # example sentences start with ・
        m = HEADER.sub("", m)               # page header bled in
        if "。" in m:                        # a full Japanese sentence leaked in
            m = m.split("。")[-1]
        pm = POS_PFX.match(m)
        if pm:
            if not e.get("pos"):
                e["pos"] = pm.group(1).strip()
            m = m[pm.end():]
        hm = HV_PFX.match(m)
        if hm:
            if not e.get("hanviet"):
                e["hanviet"] = hm.group(1).strip()
            m = m[hm.end():]
        m = m.strip(" ,;.:-")
        if m != orig.strip():
            changed_m += 1
        if not m:
            dropped += 1
            continue
        jp_ratio = len(JP.findall(m)) / max(1, len(m))
        if jp_ratio > 0.6 and len(m) > 12:   # essentially Japanese text, not a meaning
            dropped += 1
            continue
        out.append(m)
    if out:
        e["meanings"] = out

# cutting the example sentence can leave an unclosed bracket behind
closed = 0
for e in data:
    fixed = []
    for m in e["meanings"]:
        if m.count("(") > m.count(")"):
            m += ")"
            closed += 1
        if m.count("（") > m.count("）"):
            m += "）"
            closed += 1
        fixed.append(m)
    e["meanings"] = fixed

# a bare part-of-speech token left alone as a meaning, e.g. "(N/N)"
bare = 0
for e in data:
    out2 = []
    for m in e["meanings"]:
        if re.fullmatch(r"[（(]\s*[VNA][^)）]{0,12}[)）]", m.strip()):
            if not e.get("pos"):
                e["pos"] = m.strip(" ()（）")
            bare += 1
            continue
        out2.append(m)
    if out2:
        e["meanings"] = out2

empty = [e["word"] for e in data if not e["meanings"]]
print("brackets closed:", closed, "| bare POS meanings removed:", bare)
print("meanings rewritten:", changed_m, "| dropped:", dropped, "| hanviet fixed:", changed_hv)
print("entries with no meaning:", empty)
json.dump(data, open(V, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

for w in ["こぼす", "曇る", "削る", "好物", "始め", "解ける", "アップ", "仕方がない", "亡くなる"]:
    for e in data:
        if e["word"] == w:
            print(f"  {w} [{e['pos']}] {e['hanviet']!r} -> {e['meanings']}")
            break
