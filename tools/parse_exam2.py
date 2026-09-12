# -*- coding: utf-8 -*-
"""Parse text-based JLPT N3 exam PDFs into structured JSON (answers filled in later)."""
import sys, io, json, os, re
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import pdfplumber
from clean_text import page_lines, FILES

here = os.path.dirname(os.path.abspath(__file__))
FW = str.maketrans("０１２３４５６７８９", "0123456789")

SEC_RX = [
    ("moji", re.compile(r"もじ・ごい|文字・語彙|文字語彙")),
    ("bunpou", re.compile(r"文法・読解|ぶんぽう・どっかい|文法.{0,2}読解")),
    ("choukai", re.compile(r"聴解|ちょうかい")),
]
HEADER = re.compile(r"日本語能力試験")
PAGENUM = re.compile(r"^\s*\d{1,3}\s*$")
MONDAI = re.compile(r"^(?:問題|間題)\s*([0-9０-９一二三四五六七])")
QOPEN = re.compile(r"^\s*([0-9０-９]{1,2})\s*[)）]\s*(.*)$")       # 12)
QOPEN_FW = re.compile(r"^\s*([０-９]{1,2})\s*(\S.*)$")             # ２３ ...
QBAN = re.compile(r"^\s*([0-9０-９]{1,2})\s*番\s*(.*)$")           # 3番
OPT_LINE = re.compile(r"^\s*([1-4１-４])\s*(\S.*)$")               # 1 xxx  (one per line)


def i(s):
    try:
        return int(str(s).translate(FW))
    except ValueError:
        return None


def all_four(line):
    """Split '1 a 2 b 3 c 4 d' (spaces optional) into four options, else None."""
    t = line.strip()
    if not re.match(r"^[1１]\s*\S", t):
        return None
    pos, frm = [], 0
    for n in range(1, 5):
        marks = "%d%s" % (n, chr(0xFF10 + n))
        found = -1
        for m in re.finditer(r"(?:(?<=^)|(?<=\s))[" + marks + r"]", t):
            if m.start() >= frm:
                found = m.start()
                break
        if found < 0:
            return None
        pos.append(found)
        frm = found + 1
    out = []
    for k in range(4):
        start = pos[k] + 1
        end = pos[k + 1] if k < 3 else len(t)
        out.append(t[start:end].strip())
    return out if all(out) else None


def parse(tag):
    with pdfplumber.open(FILES[tag]) as pdf:
        pages = [[l["text"] for l in page_lines(p)] for p in pdf.pages]

    # which section each page belongs to (header line of the page)
    sec_of_page, last = [], "moji"
    for lines in pages:
        head = " ".join(lines[:3])
        for key, rx in SEC_RX:
            if rx.search(head):
                last = key
                break
        sec_of_page.append(last)

    sections = {}
    order = []
    cur_m = cur_q = None
    cur_key = None
    for pi, lines in enumerate(pages):
        key = sec_of_page[pi]
        if key != cur_key:
            cur_key = key
            if key not in sections:
                sections[key] = {"key": key, "mondai": []}
                order.append(key)
            cur_m = cur_q = None
        sec = sections[key]
        for t in lines:
            if HEADER.search(t) or PAGENUM.match(t):
                continue
            # some papers print the section name in the body, not the page header
            inline = next((k for k, rx in SEC_RX if rx.search(t)), None) if len(t) < 20 else None
            if inline:
                if inline != cur_key:
                    cur_key = inline
                    if inline not in sections:
                        sections[inline] = {"key": inline, "mondai": []}
                        order.append(inline)
                    sec = sections[inline]
                    cur_m = cur_q = None
                continue
            m = MONDAI.match(t)
            if m:
                no = i(m.group(1)) or m.group(1)
                # some papers never print the section name: 問題 numbering
                # restarting at 1 marks the start of the next section
                if (no == 1 and sec["mondai"]
                        and isinstance(sec["mondai"][-1]["no"], int)
                        and sec["mondai"][-1]["no"] > 1):
                    nxt = {"moji": "bunpou", "bunpou": "choukai"}.get(cur_key)
                    if nxt:
                        cur_key = nxt
                        if nxt not in sections:
                            sections[nxt] = {"key": nxt, "mondai": []}
                            order.append(nxt)
                        sec = sections[nxt]
                cur_m = {"no": no, "instruction": t, "intro": [], "questions": []}
                sec["mondai"].append(cur_m)
                cur_q = None
                continue
            if cur_m is None:
                continue

            # 1) a line holding all four options
            four = all_four(t)
            if four and cur_q is not None and len(cur_q["opts"]) == 0:
                cur_q["opts"] = four
                continue
            # 2) one option per line, in order
            om = OPT_LINE.match(t)
            if om and cur_q is not None and i(om.group(1)) == len(cur_q["opts"]) + 1:
                cur_q["opts"].append(om.group(2).strip())
                continue
            # 3) a new question
            qm = QOPEN.match(t) or QBAN.match(t)
            if not qm and key != "moji" and (cur_q is None or len(cur_q["opts"]) >= 4):
                fw = QOPEN_FW.match(t)
                if fw and i(fw.group(1)) is not None:
                    qm = fw
            if qm:
                n, body = i(qm.group(1)), qm.group(2).strip()
                # a two-digit fullwidth number can split: "２７" -> "2) 7 ..."
                dm = re.match(r"^([0-9０-９])\s+(\S.*)$", body)
                if dm and n is not None and n <= 9:
                    joined = n * 10 + i(dm.group(1))
                    prev = cur_m["questions"][-1]["n"] if cur_m["questions"] else 0
                    if joined > (prev or 0):
                        n, body = joined, dm.group(2).strip()
                cur_q = {"n": n, "q": body, "opts": [], "page": pi + 1}
                cur_m["questions"].append(cur_q)
                continue
            # 4) continuation text
            if cur_q is not None and len(cur_q["opts"]) == 0:
                cur_q["q"] = (cur_q["q"] + " " + t).strip()
            else:
                cur_m["intro"].append(t)
    return [sections[k] for k in order]


if __name__ == "__main__":
    for tag in ["2022-07", "2022-12", "2023-07"]:
        secs = parse(tag)
        print("=" * 72)
        print(tag)
        for s in secs:
            qs = [q for m in s["mondai"] for q in m["questions"]]
            full = [q for q in qs if len(q["opts"]) == 4]
            print(f"  [{s['key']}] mondai={len(s['mondai'])} questions={len(qs)} complete={len(full)}")
            for m in s["mondai"]:
                bad = [q["n"] for q in m["questions"] if len(q["opts"]) != 4]
                print(f"      問題{m['no']}: {len(m['questions'])} câu | thiếu opts: {bad[:10]} | intro: {len(m['intro'])} dòng")
        json.dump(secs, open(os.path.join(here, "exam_parsed_%s.json" % tag), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
