# Đề thi — thiếu bài nào, câu số mấy

Cập nhật 14/09/2026. Số câu ghi ở đây là **số gốc in trên đề** (trường `label` trong `exams.json`),
không phải số thứ tự trong app. Nhập bổ sung qua `exams_manual.json` rồi chạy
`cd tools && python build_exams.py` — xem schema ở `HANDOFF.md` §7.

Phạm vi số câu của từng 問題 dưới đây đã **đối chiếu tận PDF gốc**, không suy từ cấu trúc chuẩn
(hai đề có cấu trúc lệch nhau, xem ghi chú ở cuối).

| Đề | Câu đã có | Chấm được | Còn thiếu |
|---|---|---|---|
| **2021-07** | 101 | **101** ✅ | — xong hẳn |
| **2022-07** | 100 | **100** ✅ | — xong hẳn |
| 2022-12 | 75 | 59 | 26 câu chưa nhập |
| **2023-07** | 101 | **101** ✅ | — xong hẳn |
| **2023-12** | 101 | **101** ✅ | — xong hẳn |

Tổng: **478/504 câu đã nhập**, trong đó **462 chấm được**. Bốn đề xong hẳn, chỉ còn 2022-12.

Kiểm tra dữ liệu bất cứ lúc nào bằng `cd tools && python check_exams.py [id đề]` — soi số câu so với
format JLPT, lựa chọn trống/trùng, đáp án ngoài khoảng, thiếu file ảnh/audio, số thứ tự không liên tục.

---

## 2022-07 — ✅ XONG (16/09)

Nhập lại toàn bộ từ `source-pdf/exams/2022-07-typed.docx` bằng `tools/parse_docx_typed.py`,
thay bản trích từ PDF (58 câu). **100/100 câu có đáp án** — đề này phần 文字・語彙 chỉ có 34 câu
(問題1 bảy câu), nên tổng là 100 chứ không phải 101.

Bản gõ lại này lệch chuẩn nhiều nhất, phải vá bốn chỗ trong bộ trích:

- `文法` và `読解` in thành hai tiêu đề nhưng là **một** phần thi — gặp tiêu đề thứ hai thì đi tiếp
  chứ không mở phần mới.
- 問題2 (dạng ★) bị chép nhầm thành **問題8**; 問題3 và 問題5 của phần từ vựng bị gõ thành **間題**
  (nhận dạng sai chữ 問).
- Phần nghe in tiêu đề 問題N **hai lần liền nhau** (dòng tiêu đề rồi dòng hướng dẫn).
- **Ô trống của câu ★ không phải ký tự nào cả** — chỉ là mấy khoảng trắng *có gạch chân*. Đọc bằng
  `.text` là mất sạch, không còn biết ★ ở ô thứ mấy, mà đáp án phụ thuộc đúng chỗ đó. `para_text()`
  giờ đổi mỗi đoạn trắng-gạch-chân thành một ô `＿＿＿`.

### Đáp án — 1 chỗ dùng khác bảng, 5 câu bảng không có

Đối chiếu chéo với 37 đáp án cũ do AI giải: **khớp 36, lệch 1**.

| Câu | Bảng ghi | Đang dùng | Vì sao |
|---|---|---|---|
| 文法 3 | 2 = すっかり | **4 = ちっとも** | 「のに（ ）面白くなかった」 — ちっとも mới đi với phủ định |

Bảng đáp án **không có 問題5 phần từ vựng (câu 30–34)**; năm câu đó dùng đáp án do AI giải
(2, 3, 4, 1, 1) và **chủ dự án đã kiểm lại, xác nhận đúng (16/09)**.

---

## 2022-12 — thiếu 42 câu

### 文字・語彙 (30 phút) — ✅ ĐỦ 35/35

### 文法・読解 (70 phút) — thiếu 18/38
| 問題 | Đề in câu | Thiếu |
|---|---|---|
| 1 Ngữ pháp chọn đáp án | 1–13 | **câu 8, 9, 12, 13** |
| 2 Sắp xếp câu ★ | 14–18 | **cả 5 câu** (mất vị trí ô ★ khi PDF bị làm phẳng) |
| 3 Ngữ pháp trong đoạn văn | 19–22 | **câu 21, 22** (19, 20 đã lấy lại 15/09) |
| 4 Đọc ngắn (4 bài) | 23–26 | **câu 23, 25** |
| 5 Đọc trung | 27–32 | **câu 29** |
| 6 Đọc dài | 33–36 | ✅ đủ |
| 7 Tìm kiếm thông tin | 37–38 | ✅ đủ (lấy lại 15/09) |

### 聴解 (40 phút) — thiếu 28 câu
| 問題 | Câu số | Tình trạng |
|---|---|---|
| 1 課題理解 | 1–6 | có đủ, **chưa có đáp án** |
| 2 ポイント理解 | 1–6 | có đủ, **chưa có đáp án** |
| 3 概要理解 | 1–3 | ❌ đề không in gì |
| 4 発話表現 | 1–4 | ❌ **có hình vẽ**, 3 lựa chọn |
| 5 即時応答 | 1–9 | ❌ đề không in gì |

---

## 2023-07 — ✅ XONG (16/09)

Nhập lại toàn bộ từ bản gõ lại `source-pdf/exams/2023-07-typed.docx` bằng `tools/parse_docx_typed.py`,
thay cho bản trích từ PDF trước đây (chỉ được 72 câu). **101/101 câu có đáp án**,
`check_exams.py` báo 0 lỗi.

- 文字・語彙 35 · 文法・読解 38 · 聴解 28 — đủ cả 5 câu ★ của 問題2 (có vị trí ô ★) và
  bốn đoạn đọc riêng của 問題4.
- 6 ảnh phần nghe ở `images/2023-07/` (問題1 câu 3–4, 問題4 cả 4 câu), lấy thẳng từ docx.
- Audio `audio/2023-07/choukai.mp3` gắn cho cả 28 câu.

### Đáp án — 3 chỗ dùng khác bảng

Chủ dự án gửi bảng đáp án riêng (ảnh chụp bảng của Sei Japanese Centre). **Đối chiếu chéo với 56 đáp án
cũ do AI giải: khớp 53, lệch 3.** Ba chỗ lệch đều là nội dung đề nói rõ về một phía nên dùng đáp án
theo đề — **chủ dự án đã duyệt (16/09)**, đừng sửa lại cho khớp bảng:

| Câu | Bảng ghi | Đang dùng | Vì sao |
|---|---|---|---|
| 文法 7 | 2 = 点で | **4 = せいで** | 「電車が遅れたせいで遅刻した」 — 点で không ghép được vào câu |
| 読解 24 | 4 = ずっとなりたいと思い続けていた | **2 = 自分でも忘れていた夢** | bài đọc ghi rõ 「すっかり忘れていた」 |
| 読解 37 | 3 = ③と④ | **4 = ③** | ④ là 「教師や関係者のための食堂、学生は利用できません」 |

Bảng đánh số phần 読解 lại từ 1–16 (không nối tiếp 23–38) và phần 聴解 từ 1–28 (không quay về 1 ở mỗi
問題) — đã quy đổi khi nhập.

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

## 2023-12 — ✅ XONG (15/09)

Nhập từ bản gõ lại `source-pdf/exams/2023-12-typed.docx` bằng `tools/parse_docx_typed.py`
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

**6 câu dùng đáp án khác bảng** — đã xác minh thứ tự lựa chọn trên scan gốc, và **chủ dự án đã duyệt
(15/09)**. Đây là đáp án chính thức của app; đừng "sửa lại cho khớp bảng" nếu sau này có ai đối chiếu:

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

## ✅ Bài đọc "là ảnh" — ĐÃ SỬA (15/09)

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
