# -*- coding: utf-8 -*-
"""Sinh furigana cho đề thi (exams.json) theo đúng quy ước của đề gốc.

Đối chiếu 2 đề bản scan còn giữ furigana in trên giấy (7/2021, 12/2023) cho thấy:

  * Phần 文字・語彙 và 文法 gắn furigana cho *hầu như mọi* từ có kanji,
    kể cả từ khá dễ (部屋・服・林・森・番・線・次・箱・歯・塩・熱…).
  * Chỉ những chữ thuộc nhóm cơ bản nhất (mức N5) là để trần:
    今朝・急ぐ・家・電気・読書・友人・本・大学・一度・手・母・学校・顔・話…
  * Từ đang được hỏi (trong app là 【…】) KHÔNG bao giờ có furigana —
    furigana ở đó là lộ đáp án.
  * Đáp án của 問題1 (chọn cách đọc) và 問題2 (chọn cách viết) cũng không có,
    vì chính cách đọc là thứ đang hỏi.
  * Phần đọc hiểu (問題4 trở đi) trong đề thật hoàn toàn không có furigana.
    App vẫn gắn, nhưng có nút bật/tắt để ai muốn thi thử đúng thật thì tắt đi.

Cách đọc sinh bằng janome (bộ phân tích hình thái tiếng Nhật, thuần Python).
Kết quả ghi thẳng vào chuỗi theo cú pháp ``漢字《かんじ》`` để web/index.html
dựng thành thẻ <ruby>.
"""
import re

# Kanji mức cơ bản — đề gốc để trần, app cũng để trần cho đỡ rối mắt.
BASIC = set(
    "一二三四五六七八九十百千万円"
    "日月火水木金土曜年時分午前後毎週何今半間"
    "上下中外左右東西南北"
    "口目耳手足体力"
    "男女子人父母兄弟姉妹友先生学校"
    "語文字書読話聞見行来帰入出立休食飲買売店駅道車電気天空山川田花魚犬鳥雨"
    "白黒赤青長短高安新古多少大小早"
    "国会社事仕本"
    "朝昼夜急家思知終始送私顔度言持作待教用所物者方名"
)

KANJI_RE = re.compile(r"[一-鿿々]")
# 【…】 = từ đang được hỏi; giữ nguyên, không đụng vào.
KEEP_RE = re.compile(r"【[^】]*】")
DIGIT_RE = re.compile(r"[0-9０-９]")
# Chỉ ép furigana cho tên người khi có hậu tố/dấu ngoặc thoại đi kèm — nếu không,
# janome hay gán bừa cách đọc họ người Nhật cho địa danh bịa trong đề (日前→ひくま).
NAME_AFTER = ("さん", "くん", "ちゃん", "君", "様", "先生", "先輩", "「")

_tok = None


def _tokenizer():
    global _tok
    if _tok is None:
        from janome.tokenizer import Tokenizer
        _tok = Tokenizer()
    return _tok


def kata2hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


def _segments(surface):
    """Cắt bề mặt thành các đoạn kanji / không-kanji xen kẽ."""
    out, buf, cur = [], "", None
    for ch in surface:
        k = bool(KANJI_RE.match(ch))
        if cur is None or k == cur:
            buf += ch
        else:
            out.append((cur, buf))
            buf = ch
        cur = k
    if buf:
        out.append((cur, buf))
    return out


def _ruby(surface, reading):
    """Ghép furigana đúng phần kanji, chừa okurigana ra ngoài.

    忘れて + ワスレテ -> 忘《わす》れて
    Không khớp được thì trả về None để bỏ qua (thà thiếu còn hơn sai).
    """
    segs = _segments(surface)
    hira = kata2hira(reading)
    pat = ""
    for is_k, txt in segs:
        pat += "(.+?)" if is_k else re.escape(kata2hira(txt))
    m = re.fullmatch(pat, hira)
    if not m:
        return None
    out, gi = "", 0
    for is_k, txt in segs:
        if is_k:
            gi += 1
            out += "%s《%s》" % (txt, m.group(gi))
        else:
            out += txt
    return out


def annotate(text):
    """Gắn furigana cho một chuỗi; phần trong 【】 giữ nguyên."""
    if not text or not KANJI_RE.search(text):
        return text
    parts, pos = [], 0
    for m in KEEP_RE.finditer(text):
        parts.append((True, text[pos:m.start()]))
        parts.append((False, m.group(0)))
        pos = m.end()
    parts.append((True, text[pos:]))

    out, prev = "", ""
    for do, chunk in parts:
        if not do or not KANJI_RE.search(chunk):
            out += chunk
        else:
            # janome nuốt khoảng trắng và xuống dòng, nên chỉ đưa cho nó
            # những mẩu không có khoảng trắng, còn lại trả nguyên văn.
            for piece in re.split(r"(\s+)", chunk):
                if not piece or piece.isspace():
                    out += piece
                else:
                    out += _annotate_piece(piece, prev)
                    prev = piece[-1]
        if chunk.strip():
            prev = chunk.rstrip()[-1]
    return out


def _annotate_piece(piece, prev):
    out, i = "", 0
    toks = list(_tokenizer().tokenize(piece))
    for ti, t in enumerate(toks):
        s = t.surface
        before = piece[i - 1] if i else prev
        i += len(s)
        if not KANJI_RE.search(s):
            out += s
            continue
        pos = t.part_of_speech.split(",")
        nxt = toks[ti + 1].surface if ti + 1 < len(toks) else piece[i:i + 1]
        # Tên người (中山・田中・川井…) luôn có furigana trong đề gốc, dù từng
        # chữ đều cơ bản — cách đọc tên không đoán được.
        named = pos[1] == "固有名詞" and pos[2] == "人名" and nxt.startswith(NAME_AFTER)
        if pos[1] == "固有名詞" and not named:
            out += s  # địa danh/tên bịa trong đề: thà không có còn hơn đọc sai
            continue
        if not named and all(c in BASIC or not KANJI_RE.match(c) for c in s):
            out += s
            continue
        # Lượng từ đứng sau số (5 歳・3 枚) hay bị gán nhầm âm訓 → bỏ qua.
        if len(s) == 1 and DIGIT_RE.match(before or ""):
            out += s
            continue
        r = getattr(t, "reading", "*")
        out += (_ruby(s, r) if r and r != "*" else None) or s
    return out


def strip(text):
    """Gỡ markup furigana — dùng khi cần so khớp/đếm chữ trên văn bản gốc."""
    return re.sub(r"《[^》]*》", "", text or "")


def annotate_exam(ex):
    """Gắn furigana cho cả một đề (sửa tại chỗ). Trả về số chuỗi đã gắn."""
    n = 0

    def go(s):
        nonlocal n
        a = annotate(s)
        if a != s:
            n += 1
        return a

    for sec in ex.get("sections", []):
        vocab = sec.get("name", "").startswith("Từ vựng")
        for m in sec.get("mondai", []):
            if m.get("passage"):
                m["passage"] = go(m["passage"])
            # 問題1 (chọn cách đọc) / 問題2 (chọn cách viết): đáp án để trần,
            # gắn furigana vào là lộ luôn đáp án.
            leak = vocab and m.get("no") in (1, 2)
            for q in m.get("questions", []):
                if q.get("q"):
                    q["q"] = go(q["q"])
                if q.get("passage"):
                    q["passage"] = go(q["passage"])
                if not leak and q.get("opts"):
                    q["opts"] = [go(o) for o in q["opts"]]
    return n


def main():
    import io, json, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(root, "exams.json")
    exams = json.load(io.open(p, encoding="utf-8"))
    for ex in exams:
        print("%s: %d chuỗi có furigana" % (ex["id"], annotate_exam(ex)))
    tmp = p + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(exams, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, p)
    print("-> exams.json")


if __name__ == "__main__":
    main()
