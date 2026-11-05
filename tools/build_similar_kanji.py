# -*- coding: utf-8 -*-
"""Sinh similar_kanji.json: với mỗi kanji app dùng, các chữ DỄ NHẦM với nó.

Quiz dùng bảng này để dựng đáp án nhiễu kiểu JLPT (問題2 表記): giữ nguyên số
chữ kanji của từ, thay một chữ bằng chữ na ná — 招待 → 紹待 / 招持 / 照待.

    look  chữ trông giống: nhiều thành phần chung (RADKFILE), thành phần hiếm
          được tính nặng hơn — chung 寺 (待/持/特) đáng kể hơn chung 口; số nét gần nhau
    same  chữ cùng âm On (KANJIDIC2) — 制/製/正, 係/計/径

Nguồn (EDRDG, CC BY-SA 4.0 — https://www.edrdg.org/edrdg/licence.html), lấy
từ hai gói npm vì máy dựng không vào được edrdg.org. Chỉ ĐỌC file dữ liệu như
văn bản, không chạy code của gói:

    npm pack @johnmorrisdotca/bushu kanji.js
    tar -xzf johnmorrisdotca-bushu-*.tgz -C bushu && tar -xzf kanji.js-*.tgz -C kanjijs
    python tools/build_similar_kanji.py bushu/package/dist/data/radkfile.data.js \
        kanjijs/package/dist/kanji.js

similar_kanji.json là dữ liệu dẫn xuất nên giữ nguyên giấy phép CC BY-SA 4.0
(ghi trong khoá "_meta" của file).
"""
import sys, io, json, math, os, re
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "similar_kanji.json")

LOOK_MAX, SAME_MAX = 8, 8
LOOK_MIN_SIM = 0.34       # dưới mức này là chỉ chung vài nét vặt, không còn "na ná"
MAX_STROKE_GAP = 6        # 制 (8 nét) / 製 (14 nét) vẫn là cặp kinh điển
COMMON_FREQ = 2200        # chữ ngoài app chỉ nhận khi thuộc ~2200 chữ hay gặp nhất


def is_kanji(c):
    return "一" <= c <= "鿿" or c == "々"


def load_radk(path):
    """kanji -> tập thành phần (đảo ngược RADKFILE thành KRADFILE)."""
    text = open(path, encoding="utf-8").read()
    comp = defaultdict(set)
    for rad, kanji in re.findall(r'radical:\s*"([^"]+)",\s*strokes:\s*\d+,\s*kanji:\s*"([^"]*)"', text):
        for k in kanji:
            comp[k].add(rad)
    return comp


def load_kanjidic(path):
    """kanji -> {on: [...], strokes, freq, grade}; chỉ đọc các object literal."""
    text = open(path, encoding="utf-8").read()
    info = {}
    for m in re.finditer(r'\{([^{}]*?literal:"(.)"[^{}]*?)\}', text):
        body, lit = m.group(1), m.group(2)
        on = re.search(r'onyomi:\[([^\]]*)\]', body)
        sc = re.search(r'stroke_count:(\d+)', body)
        fq = re.search(r'freq:(\d+)', body)
        gr = re.search(r'grade:(\d+)', body)
        info[lit] = {
            "on": re.findall(r'"([^"]+)"', on.group(1)) if on else [],
            "strokes": int(sc.group(1)) if sc else 0,
            "freq": int(fq.group(1)) if fq else 99999,
            "grade": int(gr.group(1)) if gr else 0,
        }
    return info


def app_kanji():
    used = set()
    for e in json.load(open(os.path.join(ROOT, "vocab.json"), encoding="utf-8")):
        used.update(c for c in e["word"] if is_kanji(c))
    for k in json.load(open(os.path.join(ROOT, "kanji.json"), encoding="utf-8")):
        used.add(k["kanji"])
        for w in k["words"]:
            used.update(c for c in w["word"] if is_kanji(c))
    used.discard("々")
    return used


def main(radk_path, kanjidic_path):
    comp = load_radk(radk_path)
    info = load_kanjidic(kanjidic_path)
    used = app_kanji()
    # Ứng viên thay thế: chữ trong app + chữ thường dùng (常用, grade 1-8). Không
    # lấy chữ hiếm — đáp án nhiễu phải là chữ người học có thể đã gặp.
    pool = sorted(c for c in (used | {k for k, v in info.items()
                                      if 1 <= v["grade"] <= 8 and v["freq"] <= COMMON_FREQ})
                  if c in comp and c in info)
    n = len(pool)
    df = defaultdict(int)
    for c in pool:
        for r in comp[c]:
            df[r] += 1
    w = {r: math.log(n / df[r]) for r in df}

    def look_sim(a, b):
        A, B = comp[a], comp[b]
        inter = sum(w[r] for r in A & B)
        if not inter:
            return 0.0
        return inter / sum(w[r] for r in A | B)

    # Chỉ âm On ĐẦU TIÊN: KANJIDIC liệt kê cả âm hiếm (確 カク, コウ) — lấy hết thì
    # 確 lại "đồng âm" với 行/後/高, chẳng ai nhầm cả.
    on1 = {c: (info[c]["on"][0] if info[c]["on"] else None) for c in pool}
    by_on = defaultdict(list)
    for c in pool:
        if on1[c]:
            by_on[on1[c]].append(c)

    # chữ gần với chữ khác qua thành phần hiếm nhất của nó — đỡ phải so mọi cặp
    by_comp = defaultdict(list)
    for c in pool:
        for r in comp[c]:
            by_comp[r].append(c)

    rank = lambda c: (info[c]["freq"], c)   # chữ thông dụng trước
    out = {}
    missing = []
    for c in sorted(used):
        if c not in comp or c not in info:
            missing.append(c)
            continue
        cands = set()
        for r in comp[c]:
            if df[r] <= 400:                  # bỏ nét vặt có ở khắp nơi (一, 口, 丶…) khi gom ứng viên
                cands.update(by_comp[r])
        cands.discard(c)
        sc = info[c]["strokes"]
        look = []
        for b in cands:
            if abs(info[b]["strokes"] - sc) > MAX_STROKE_GAP:
                continue
            # chữ chỉ là MỘT PHẦN của c (寺 trong 待, 言 trong 計, 主 trong 注) thì trông
            # như bộ thủ đứng riêng, không ai chọn nhầm — loại
            if comp[b] < comp[c] and info[b]["strokes"] <= sc - 2:
                continue
            s = look_sim(c, b)
            if s >= LOOK_MIN_SIM:
                # chung âm On mà còn trông giống (制/製, 招/紹) là nhiễu tốt nhất
                bonus = 0.25 if on1[c] and on1[b] == on1[c] else 0.0
                look.append((-round(s + bonus, 3), info[b]["freq"], b))
        look = [b for _, _, b in sorted(look)[:LOOK_MAX]]
        same = set(by_on[on1[c]]) if on1[c] else set()
        same.discard(c)
        # đồng âm: chữ trông giống xếp trước, rồi tới chữ thông dụng
        same = sorted(same, key=lambda b: (-look_sim(c, b), info[b]["freq"], b))[:SAME_MAX]
        if look or same:
            out[c] = {"look": "".join(look), "same": "".join(same)}

    data = {
        "_meta": {
            "about": "Kanji dễ nhầm cho đáp án nhiễu của quiz: look = trông giống (chung thành phần), "
                     "same = cùng âm On. Sinh bởi tools/build_similar_kanji.py.",
            "source": "KANJIDIC2, RADKFILE/KRADFILE — Electronic Dictionary Research and Development Group "
                      "(EDRDG), https://www.edrdg.org/edrdg/licence.html",
            "license": "CC BY-SA 4.0",
        },
        "kanji": out,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print("kanji trong app: %d · có dữ liệu: %d · thiếu: %d %s" % (len(used), len(out), len(missing), "".join(missing)))
    print("pool ứng viên: %d chữ · file: %s (%.1f KB)" % (n, OUT, os.path.getsize(OUT) / 1024))
    for c in "招待計画制度注意確認持特週曜復側績険末晴試験":
        if c in out:
            print("  %s  look=%-9s same=%s" % (c, out[c]["look"], out[c]["same"]))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
