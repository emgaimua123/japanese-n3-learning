# -*- coding: utf-8 -*-
"""Parse GunGun N3 grammar PDF -> grammar.json (patterns + book answer keys)."""
import sys, io, json, re, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import unicodedata
import pdfplumber



def _plain(t):
    """bỏ dấu tiếng Việt + về chữ hoa, để so tên file bất kể NFC/NFD"""
    t = unicodedata.normalize("NFD", t)
    return "".join(c for c in t if not unicodedata.combining(c)).upper().replace("Đ", "D")


def _find_pdf(*keywords):
    for p in glob.glob(os.path.join(os.path.expanduser("~"), "Downloads", "*.pdf")):
        name = _plain(os.path.basename(p))
        if all(_plain(k) in name for k in keywords):
            return p
    raise SystemExit("Không tìm thấy PDF chứa: %s (trong Downloads)" % ", ".join(keywords))


PATH = _find_pdf("GUNGUN", "NGU PHAP")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "grammar.json")

MARK_P = "\u2776\u2777\u2778\u2779\u277a\u277b\u277c\u277d\u277e\u277f" \
         "\u278a\u278b\u278c\u278d\u278e\u278f\u2790\u2791\u2792\u2793"
MARK_V = "\u24f5\u24f6\u24f7\u24f8\u24f9\u24fa\u24fb\u24fc\u24fd\u24fe"
MARK_E = "\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468\u2469"
JP = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
LAT = re.compile(r"[0-9A-Za-z\u00c0-\u1ef9]")


def mark_index(ch):
    i = MARK_P.find(ch)
    return (i % 10) + 1 if i >= 0 else None


def tidy(t):
    t = re.sub(r"\s+", " ", t).strip()
    # the PDF glues Latin text onto Japanese quotes: put the space back
    t = re.sub(r"([0-9A-Za-z\u00c0-\u1ef9])([\u300c\u300e\uff08])", r"\1 \2", t)
    t = re.sub(r"([\u300d\u300f\uff09])([0-9A-Za-z\u00c0-\u1ef9])", r"\1 \2", t)
    t = re.sub(r"([,:;])([A-Za-z\u00c0-\u1ef9])", r"\1 \2", t)
    return t.strip()


def line_join(words, jp_mode=False):
    out, prev = "", None
    for w in sorted(words, key=lambda w: w["x0"]):
        t = w["text"]
        if not t:
            continue
        small = w["size"] < 10
        if prev is not None:
            gap = w["x0"] - prev["x1"]
            latin_edge = LAT.search(prev["text"][-1]) and LAT.search(t[0])
            if (not jp_mode and latin_edge) or gap > 4:
                out += " "
        out += t
        if small and not jp_mode:
            out += " "
            prev = None
        else:
            prev = w
    return tidy(out)


def group_lines(words, tol=5):
    lines = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        for ln in lines:
            if abs(ln["top"] - w["top"]) <= tol:
                ln["w"].append(w)
                break
        else:
            lines.append({"top": w["top"], "w": [w]})
    return lines


def parse_answer_page(body):
    """'Dap an tham khao phan dich' page -> {pattern_index: [japanese sentences]}"""
    out, cur = {}, None
    for ln in group_lines([w for w in body if w["size"] >= 10], tol=6):
        t = line_join(ln["w"], jp_mode=True).replace(" ", "")
        if not t:
            continue
        if t[0] in MARK_P:
            cur = mark_index(t[0])
            out.setdefault(cur, [])
            continue
        if cur is None:
            continue
        for seg in re.split("([" + MARK_V + "])", t):
            if not seg:
                continue
            if seg in MARK_V:
                out[cur].append("")
            elif out[cur]:
                out[cur][-1] += seg
    return {k: [s for s in v if JP.search(s)] for k, v in out.items()}


def parse():
    items, answers, cur_key = [], {}, None
    with pdfplumber.open(PATH) as pdf:
        for pi, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["size"])
            if not words:
                continue
            head = " ".join(w["text"] for w in words if w["top"] < 45)
            m = re.search(r"B\u00c0I\s*(\d+)", head)
            chapter = next((int(w["text"]) for w in words
                            if w["size"] > 25 and w["x0"] < 40 and w["text"].isdigit()), None)
            if not m or chapter is None:
                continue
            lesson = int(m.group(1))
            body = [w for w in words if 45 < w["top"] < 800]
            flat = "".join(w["text"] for w in body).replace(" ", "")
            if "\u0110\u00e1p\u00e1ntham" in flat:
                # the answer page belongs to the lesson whose pattern pages
                # precede it - page 127 prints the wrong chapter in the book
                key = cur_key or (chapter, lesson)
                got = parse_answer_page(body)
                slot = answers.setdefault(key, {})
                for k, v in got.items():
                    slot.setdefault(k, []).extend(v)
                continue

            # a pattern headline always starts at the left margin; a centred
            # line that high up is the continuation of the previous pattern
            pat_words = [w for w in body if w["size"] >= 16 and 60 < w["top"] < 112 and w["x0"] < 250]
            pattern = line_join(pat_words)
            idx = mark_index(pattern[0]) if pattern else None
            if idx:
                pattern = pattern[1:].strip()
            # vài trang in dấu ☆ (vốn của dòng nghĩa) lọt lên dòng mẫu
            pattern = pattern.lstrip("☆").strip()
            mean_words = [w for w in body if w["size"] >= 16 and 112 <= w["top"] < 180 and w["x0"] < 340]
            meaning = line_join(mean_words).lstrip("\u2606").strip()

            div_top = None
            for ln in group_lines([w for w in body if 13.5 <= w["size"] < 16]):
                if "D\u1ecbch" in line_join(ln["w"]):
                    div_top = ln["top"]
                    break

            def above(w):
                return div_top is None or w["top"] < div_top - 5

            tbl = [w for w in body if w["x0"] >= 330 and above(w) and w["top"] > 110
                   and (13.5 <= w["size"] < 16 or 7.5 <= w["size"] < 10)]
            forms = [f for f in (line_join(l["w"]) for l in group_lines(tbl, tol=9)) if f]

            notes, drills = [], []
            for ln in group_lines([w for w in body if 12.5 <= w["size"] < 13.5 and w["x0"] < 560]):
                t = line_join(ln["w"])
                if not t or set(t) <= {".", " "}:
                    continue
                if div_top is not None and ln["top"] > div_top:
                    drills.append(t)
                else:
                    notes.append(t)
            merged = []
            for t in notes:
                if t.startswith("\u2756") or not merged:
                    merged.append(t.lstrip("\u2756").strip())
                else:
                    merged[-1] += " " + t
            notes = [tidy(t) for t in merged if t.strip()]

            dr = []
            for t in drills:
                t = t.strip(" .")
                if not t:
                    continue
                if t[0] in MARK_V or not dr:
                    dr.append(t.lstrip(MARK_V).strip())
                else:
                    dr[-1] += " " + t
            drills = [tidy(d) for d in dr if d.strip()]

            ex_words = [w for w in body if 10.5 <= w["size"] < 13 and w["x0"] >= 80 and above(w)]
            examples = []
            for ln in group_lines(ex_words, tol=6):
                t = line_join(ln["w"], jp_mode=True).replace(" ", "")
                if not t:
                    continue
                if t[0] in MARK_E:
                    examples.append(t[1:])
                elif examples:
                    examples[-1] += t
            examples = [e for e in examples if JP.search(e)]

            cur_key = (chapter, lesson)
            if not pattern:
                # continuation page: fold its content into the pattern before it
                if items and (items[-1]["chapter"], items[-1]["lesson"]) == cur_key:
                    prev = items[-1]
                    prev["notes"] += notes
                    prev["examples"] += [{"jp": e} for e in examples]
                    prev["drills"] += [{"vi": d} for d in drills]
                    prev["forms"] += forms
                continue
            items.append({"chapter": chapter, "lesson": lesson, "index": idx,
                          "pattern": pattern, "meaning": meaning, "forms": forms,
                          "notes": notes, "examples": [{"jp": e} for e in examples],
                          "drills": [{"vi": d} for d in drills], "page": pi + 1})

    seen = {}
    for it in items:
        key = (it["chapter"], it["lesson"])
        seen[key] = seen.get(key, 0) + 1
        if not it["index"]:
            it["index"] = seen[key]
        it["id"] = "c%db%dp%d" % (it["chapter"], it["lesson"], it["index"])
        ans = answers.get(key, {}).get(it["index"], [])
        for i, d in enumerate(it["drills"]):
            if i < len(ans):
                d["jp"] = ans[i]

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)

    lessons = sorted({(i["chapter"], i["lesson"]) for i in items})
    print("patterns:", len(items), "| lessons:", len(lessons),
          "| examples:", sum(len(i["examples"]) for i in items),
          "| drills:", sum(len(i["drills"]) for i in items),
          "| drills with answer:", sum(1 for i in items for d in i["drills"] if d.get("jp")))
    print("no examples:", [i["id"] for i in items if not i["examples"]][:10])
    print("no meaning :", [i["id"] for i in items if not i["meaning"]][:10])
    for i in items[:1] + items[51:52]:
        print("=" * 60)
        print("%s | %s | * %s (p%d)" % (i["id"], i["pattern"], i["meaning"], i["page"]))
        print("  forms:", " / ".join(i["forms"]))
        for n in i["notes"]:
            print("  note:", n[:110])
        for e in i["examples"]:
            print("  ex  :", e["jp"][:70])
        for d in i["drills"]:
            print("  drill:", d["vi"][:58], "->", (d.get("jp") or "(none)")[:52])


parse()
