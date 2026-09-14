# Đề thi — thiếu bài nào, câu số mấy

Cập nhật 14/09/2026. Số câu ghi ở đây là **số gốc in trên đề** (trường `label` trong `exams.json`),
không phải số thứ tự trong app. Nhập bổ sung qua `exams_manual.json` rồi chạy
`cd tools && python build_exams.py` — xem schema ở `HANDOFF.md` §7.

Phạm vi số câu của từng 問題 dưới đây đã **đối chiếu tận PDF gốc**, không suy từ cấu trúc chuẩn
(hai đề có cấu trúc lệch nhau, xem ghi chú ở cuối).

| Đề | Câu đã có | Chấm được | Còn thiếu |
|---|---|---|---|
| **2021-07** | 101 | **101** ✅ | — xong hẳn |
| 2022-07 | 50 | 34 | 50 câu chưa nhập |
| 2022-12 | 71 | 55 | 30 câu chưa nhập |
| 2023-07 | 67 | 51 | 34 câu chưa nhập |
| **2023-12** | 101 | **101** ✅ | — xong hẳn |

Tổng: **390/504 câu đã nhập**, trong đó **342 chấm được**.

Kiểm tra dữ liệu bất cứ lúc nào bằng `cd tools && python check_exams.py [id đề]` — soi số câu so với
format JLPT, lựa chọn trống/trùng, đáp án ngoài khoảng, thiếu file ảnh/audio, số thứ tự không liên tục.

---

## 2022-07 — thiếu 66 câu

### 文字・語彙 (30 phút) — ✅ ĐỦ 34/34
Đề này chỉ in **34 câu** (問題1 có 7 câu, không phải 8 như các đề khác). Không thiếu gì.

### 文法・読解 (70 phút) — ❌ MẤT TOÀN BỘ 38 câu
Parser tách section sai vì file này không in tên phần 「文法・読解」. Cần nhập lại tất cả:

| 問題 | Câu số | Cần nhập |
|---|---|---|
| 1 Ngữ pháp chọn đáp án | 1–13 | câu hỏi + 4 lựa chọn + đáp án |
| 2 Sắp xếp câu ★ | 14–18 | câu hỏi + 4 lựa chọn + **vị trí ô ★** + đáp án |
| 3 Ngữ pháp trong đoạn văn | 19–22 | đoạn văn (`passage`) + 4 câu + đáp án |
| 4 Đọc ngắn (4 bài) | 23–26 | 4 đoạn văn + 4 câu + đáp án |
| 5 Đọc trung | 27–32 | đoạn văn + 6 câu + đáp án |
| 6 Đọc dài | 33–36 | đoạn văn + 4 câu + đáp án |
| 7 Tìm kiếm thông tin | 37–38 | bảng thông tin (là ảnh) + 2 câu + đáp án |

Dữ liệu parser đọc được (dùng để gõ lại cho nhanh): `python tools/show_parsed.py 2022-07`.

### 聴解 (40 phút) — thiếu 28 câu
| 問題 | Câu số | Tình trạng |
|---|---|---|
| 1 課題理解 | 1–6 | có câu 2–6 (thiếu **câu 1**), cả 5 câu **chưa có đáp án** |
| 2 ポイント理解 | 1–6 | có đủ 6 câu, **chưa có đáp án** |
| 3 概要理解 | 1–3 | ❌ đề không in gì (ーメモー) — phải nghe rồi gõ lại |
| 4 発話表現 | 1–4 | ❌ **có hình vẽ**, 3 lựa chọn |
| 5 即時応答 | 1–9 | ❌ đề không in gì (ーメモー) |

---

## 2022-12 — thiếu 46 câu

### 文字・語彙 (30 phút) — ✅ ĐỦ 35/35

### 文法・読解 (70 phút) — thiếu 18/38
| 問題 | Đề in câu | Thiếu |
|---|---|---|
| 1 Ngữ pháp chọn đáp án | 1–13 | **câu 8, 9, 12, 13** |
| 2 Sắp xếp câu ★ | 14–18 | **cả 5 câu** (mất vị trí ô ★ khi PDF bị làm phẳng) |
| 3 Ngữ pháp trong đoạn văn | 19–22 | **cả 4 câu** (đoạn văn là ảnh) |
| 4 Đọc ngắn (4 bài) | 23–26 | **câu 23, 25** (đoạn văn là ảnh/tờ rơi) |
| 5 Đọc trung | 27–32 | **câu 29** |
| 6 Đọc dài | 33–36 | ✅ đủ |
| 7 Tìm kiếm thông tin | 37–38 | **cả 2 câu** (bảng thông tin là ảnh) |

### 聴解 (40 phút) — thiếu 28 câu
| 問題 | Câu số | Tình trạng |
|---|---|---|
| 1 課題理解 | 1–6 | có đủ, **chưa có đáp án** |
| 2 ポイント理解 | 1–6 | có đủ, **chưa có đáp án** |
| 3 概要理解 | 1–3 | ❌ đề không in gì |
| 4 発話表現 | 1–4 | ❌ **có hình vẽ**, 3 lựa chọn |
| 5 即時応答 | 1–9 | ❌ đề không in gì |

---

## 2023-07 — thiếu 50 câu

### 文字・語彙 (30 phút) — thiếu 3/35
| 問題 | Đề in câu | Thiếu |
|---|---|---|
| 4 Từ đồng nghĩa | 26–30 | **câu 28, 29, 30** — 3 câu này in lựa chọn thành 2 cột nên parser bỏ qua |

Các 問題 còn lại (1–3, 5) đủ.

### 文法・読解 (70 phút) — thiếu 19/38
| 問題 | Đề in câu | Thiếu |
|---|---|---|
| 1 Ngữ pháp chọn đáp án | 1–13 | **câu 8, 9, 11, 12, 13** |
| 2 Sắp xếp câu ★ | 14–18 | **cả 5 câu** |
| 3 Ngữ pháp trong đoạn văn | 19–22 | **cả 4 câu** (đoạn văn là ảnh) |
| 4 Đọc ngắn (4 bài) | 23–26 | **câu 23, 25** |
| 5 Đọc trung | 27–32 | **câu 29** |
| 6 Đọc dài | 33–36 | ✅ đủ |
| 7 Tìm kiếm thông tin | 37–38 | **cả 2 câu** |

### 聴解 (40 phút) — thiếu 28 câu
Giống hệt 2022-12: 問題1 và 問題2 đủ câu nhưng **chưa có đáp án**; 問題3, 4, 5 chưa có câu nào.

---

## 2021-07 — ✅ XONG (14/09)

Chủ dự án cung cấp bản gõ lại đầy đủ kèm bảng đáp án:
`source-pdf/exams/2021-07-typed.docx` (PDF scan gốc vẫn giữ ở `source-pdf/exams/2021-07.pdf`).
`tools/parse_docx_2021.py` trích ra **101/101 câu có đáp án**, `check_exams.py` báo **0 lỗi, 0 nghi ngờ**.

- 文字・語彙 35 · 文法・読解 38 · 聴解 28 — đúng format JLPT.
- Giữ được dấu gạch chân của đề (từ đang hỏi bọc trong 【】) và **vị trí ô ★** của 問題2.
- 5 ảnh trong docx tách ra `images/2021-07/` (問題1 câu 4, 問題4 cả 4 câu).
- 問題3 (概要理解, 3 câu, 4 lựa chọn) và 問題5 (即時応答, 9 câu, 3 lựa chọn) đề **không in gì**,
  nhưng vẫn tạo đủ số câu với lựa chọn trống để nghe audio rồi chọn số — có đáp án nên **chấm điểm được**.
- Audio `audio/2021-07/choukai.mp3` gắn cho cả 28 câu.

## 2023-12 — đủ 101 câu, ❌ THIẾU TOÀN BỘ ĐÁP ÁN

Nhập từ bản gõ lại `source-pdf/exams/2023-12-typed.docx` bằng `tools/parse_docx_2023.py`
(PDF scan gốc vẫn ở `source-pdf/exams/2023-12.pdf`). `check_exams.py`: **0 lỗi, 0 nghi ngờ**.

- 文字・語彙 35 · 文法・読解 38 · 聴解 28 — đúng format JLPT, đủ bài đọc và bảng giá của 問題7.
- 6 ảnh phần nghe ở `images/2023-12/` (問題1 câu 1 và 4; 問題4 cả 4 câu — ảnh gốc là ảnh chụp
  cả trang gồm hai câu nên script tự tách đôi theo khung tranh).
- Audio `audio/2023-12/choukai.mp3` gắn cho cả 28 câu.
- 問題3 (3 câu) và 問題5 (9 câu) phần nghe: đề không in gì, vẫn tạo đủ số câu với lựa chọn trống.

### Đáp án (15/09) — và 6 chỗ đã sửa khác bảng đáp án

Docx không kèm đáp án; chủ dự án gửi bảng đáp án riêng (ảnh chụp bảng của 芥末日语). Đã áp đủ 101 câu
vào `exams_manual.json`.

**Đã đối chiếu chéo 73/101 câu** bằng cách tự giải lại đề và so với scan gốc `source-pdf/exams/2023-12.pdf`:

| Phần | Kết quả |
|---|---|
| 読解 (23–38) | **16/16 khớp** |
| 文法 問題2 ★, 問題3 (14–22) | khớp hết (sau khi sửa lỗi ★ bên dưới) |
| 文字・語彙 (1–35) | 32 khớp, **3 vênh** |
| 文法 問題1 (1–13) | 10 khớp, **3 vênh** |
| 聴解 (28 câu) | không kiểm được — phải nghe audio |

**6 câu đang dùng đáp án khác bảng** (đã xác minh thứ tự lựa chọn trên scan gốc, nghĩa tiếng Nhật
không có chỗ tranh cãi). Muốn quay lại theo bảng thì sửa `exams_manual.json`:

| Câu | Bảng ghi | Đang dùng | Vì sao |
|---|---|---|---|
| 文字・語彙 2 | 2 = せんしゅう | **3 = せんしゅ** | 選手 đọc là せんしゅ |
| 文字・語彙 14 | 3 = 回費 | **2 = 会費** | かいひ viết là 会費; 回費 không phải từ |
| 文字・語彙 32 | 1 = 教師になるという行き先… | **3 = 次の旅行の行き先を…** | 行き先 = nơi đến, câu 1 phải là 目標 |
| 文法 9 | 3 = 踊れるようにして | **4 = 踊れるようになるのに** | 「…のに何年かかる」 mới đúng ngữ pháp |
| 文法 11 | 4 = でいらっしゃいます | **3 = でございます** | いらっしゃる dùng cho người, không dùng cho tầng lầu |
| 文法 13 | 3 = 思っていたからでした | **1 = 思っていたところでした** | 「ちょうど…しようと思っていたところ」 |

### Lỗi của bản gõ lại đã sửa

`文法 問題2 câu 14`: đề gốc để ★ ở **ô thứ nhất** (「彼女 ★ ＿ ＿ ＿ いないと思う」), docx chép thành ô
thứ hai. Sai vị trí ★ là sai luôn đáp án. Đã sửa theo scan; sau khi sửa thì đáp án của bảng (4 = ほど)
đúng.

---

## Hình minh hoạ — đã cắt xong (14/09)

`tools/crop_images.py` cắt 17 hình trong phần 聴解 ra `images/<id đề>/choukai-m<問題>-q<câu>.png`
(PNG xám 216 dpi, tổng 1,7 MB), đã gắn vào câu qua trường `img` trong `exams_manual.json`:

| Đề | 問題1 課題理解 | 問題4 発話表現 |
|---|---|---|
| 2022-07 | câu 1, câu 5 | 4 câu (đã tạo mới) |
| 2022-12 | câu 3 | 4 câu (đã tạo mới) |
| 2023-07 | câu 3, câu 4 | 4 câu (đã tạo mới) |

- 問題1: hình chính là 4 lựa chọn (tranh đánh số 1–4, hoặc sơ đồ ア/イ/ウ/エ) — gắn vào câu có sẵn.
  Câu 1 của đề 2022-07 trước đây thiếu hẳn, nay đã thêm cùng hình.
- 問題4 発話表現: tranh **chính là** đề bài, đề không in chữ nào. Đã tạo mới 4 câu mỗi đề,
  mỗi câu 3 lựa chọn trống — app hiện ①②③ kèm dòng "Đề không in lựa chọn — nghe audio rồi chọn số".
- Cả 17 câu này **vẫn chưa có đáp án**, phải nghe audio mới điền được.

Phần 文法・読解 **không cần hình**: xem mục dưới.

## ⚠️ Bài đọc "là ảnh" thực ra là text bị lọc nhầm

Kiểm lại tận PDF: các trang 問題3 / 問題4 / 問題7 **có đủ text**. Ví dụ trang 9 đề 12/2022 có 649 ký
tự, nhưng `tools/clean_text.py` chỉ giữ 127 — 479 ký tự bài đọc 京都旅行 (font `…giKyokashoNK-R`
12pt) bị vứt vì luật lọc watermark `non_stroking_color == "(0.0,)"` quá rộng. Watermark thật
("Tôi Yêu Ngoại Ngữ Group / Yuuki Bùi") dùng font Helvetica-BoldOblique nên **đã bị luật font bắt
rồi**, luật màu là thừa.

Nới luật đó lại là lấy về được: bài đọc 問題3, các đoạn 問題4 còn thiếu, bảng thông tin 問題7 —
khoảng **30 câu** trên 2 đề, dưới dạng text đàng hoàng chứ không phải ảnh. Việc này **chưa làm**
vì đụng vào pipeline trích xuất, cần chạy lại và đối chiếu kỹ kẻo hỏng dữ liệu đang tốt.

## Chỗ nên đối chiếu lại với đề gốc

`check_exams.py` báo 0 lỗi trên cả 4 đề. Còn lại mấy chỗ **nghi ngờ**, không phải lỗi chắc chắn:

| Chỗ | Vấn đề | Nên làm |
|---|---|---|
| 2022-07 問題2 câu 13 | lựa chọn 2 và 4 **giống hệt nhau** (đều là 図面) | đọc lại đề gốc — gần như chắc parser đọc nhầm một lựa chọn |
| 2022-07 文字・語彙 問題1 | 7 câu thay vì 8 | đề này in đúng 7 câu, **không phải lỗi** |
| các đề 2022/2023 | số câu ít hơn format | đúng như bảng thiếu ở trên |

## Ghi chú kỹ thuật khi bổ sung

- **Số câu khác nhau giữa các đề**: 2022-07 phần 文字・語彙 chỉ có 34 câu (問題1 = 7 câu);
  2022-12 và 2023-07 có 35 câu (問題1 = 8 câu). Đừng áp một khuôn cho cả 5 đề.
- **問題4 phần nghe (発話表現) có hình vẽ** — thí sinh nhìn tranh rồi chọn câu nói phù hợp.
  `exams.json` hiện **không có trường ảnh** cho câu hỏi, muốn làm phần này phải thêm.
- **問題4 và 問題5 phần nghe chỉ có 3 lựa chọn**, không phải 4. UI render theo độ dài `opts`
  nên không cần sửa code, chỉ cần nhập đúng 3 phần tử.
- **Đáp án**: nhập kèm trong `exams_manual.json` (trường `answer`), hoặc bỏ vào `exam_answers.json`
  với key `<id đề>/<phần>/<số câu gốc>` — ví dụ `2022-12/bunpou/8`. Phần nghe dùng key
  `<id đề>/choukai/<số câu trong 問題 đó>`, nhưng vì 問題1 và 問題2 đều đánh số 1–6 nên
  **nhập qua `exams_manual.json` sẽ an toàn hơn** (khớp theo cả `no` của 問題).
- Toàn bộ 140 đáp án hiện có là **do Claude tự giải**, chưa đối chiếu đáp án chính thức.
