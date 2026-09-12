# GunGun N3 Trainer — Bàn giao & việc còn lại

> File này để mở session mới mà không mất ngữ cảnh. Cập nhật lần cuối: 12/09/2026.

## 1. Ứng dụng là gì

App desktop Windows luyện thi JLPT N3 theo giáo trình GunGun Joutatsu, đóng gói 1 file `.exe`.

- **Host**: `app.py` — pywebview + WebView2, tray icon (pystray), thông báo Windows, auto-start, chấm dịch bằng Claude API.
- **Giao diện + toàn bộ logic**: `web/index.html` (một file, ~4.700 dòng, không framework).
- **Dữ liệu**: `vocab.json`, `kanji.json`, `grammar.json`, `reading.json`, `exams.json` — đều trích tự động từ PDF trong `C:\Users\Admin\Downloads`.
- **Tiến trình người dùng**: localStorage của WebView2 **và** bản sao `%LOCALAPPDATA%\GunGunN3Trainer\state-backup.json` (lúc khởi động lấy bản mới hơn theo `savedAt`).
- **API key Claude**: lưu riêng ở `%LOCALAPPDATA%\GunGunN3Trainer\claude-api-key.txt`, cố ý **không** nằm trong file backup tiến trình.

### Build lại exe

```powershell
python -m PyInstaller --noconfirm --onefile --windowed --name GunGunN3Trainer --icon icon.ico --add-data "web;web" --add-data "vocab.json;." --add-data "kanji.json;." --add-data "grammar.json;." --add-data "reading.json;." --add-data "exams.json;." --add-data "icon.ico;." --hidden-import pystray._win32 app.py
```

Phải tắt `GunGunN3Trainer.exe` trước khi build (nó khoá file trong `dist`). Python dùng: `C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\python.exe`.

### Test nhanh không cần build

`.claude/launch.json` có cấu hình `n3-trainer-web` chạy `python -m http.server 8123`; mở `http://localhost:8123/web/index.html`. Khi không có pywebview, `App.loadData()` tự fetch các file JSON, và các API host (`grade_translation`, tray, thông báo…) trả `null` nên UI vẫn chạy được.

## 2. Trạng thái các phần

| Phần | Trạng thái | Ghi chú |
|---|---|---|
| Từ vựng | ✅ 2016 từ | đã làm sạch lỗi nuốt câu ví dụ vào nghĩa |
| Kanji | ✅ 337 chữ + 1073 từ | quiz: kanji→hiragana (tự luận), hiragana→kanji (trắc nghiệm) |
| Ngữ pháp | ✅ 151 mẫu / 26 bài | quiz dịch Nhật→Việt, chấm bằng Claude API hoặc bộ chấm offline |
| Đọc hiểu | ✅ 22 bài (chương 5–9) | đáp án + câu chứa đáp án + giải thích + tips do Claude soạn |
| Đề thi JLPT | ⚠️ 3/5 đề, thiếu nhiều câu | xem mục 3 |

## 3. ĐỀ THI — những chỗ còn thiếu (phần cần bổ sung)

### 3.1 Hai đề chưa xử lý được: PDF là ảnh scan

| File | Trang | Vấn đề |
|---|---|---|
| `Đề thi JLPT N3 7_2021.pdf` | 16 trang, 43 ảnh | **Không có text**, toàn ảnh scan |
| `ĐỀ THI JLPT N3 12.2023.pdf` | 30 trang, 24 ảnh | **Không có text**, toàn ảnh scan |

Máy chưa có `tesseract` (và `pytesseract`/`pdf2image`/`fitz` cũng chưa cài). Hai cách:

1. Cài Tesseract + gói ngôn ngữ `jpn`, rồi OCR (chất lượng OCR tiếng Nhật với furigana thường kém, phải sửa tay nhiều).
2. **Cách nên dùng**: đọc từng trang bằng vision (công cụ `Read` với `pages:"n"`) rồi gõ lại câu hỏi + 4 lựa chọn vào JSON. ~46 trang.

### 3.2 Đề đã xử lý — số câu lấy được

| Đề | Từ vựng–Chữ Hán (30′) | Ngữ pháp–Đọc hiểu (70′) | Nghe hiểu (40′) |
|---|---|---|---|
| 7/2022 | 34 câu ✅ | **0 câu** ❌ | 11 câu (không chấm) |
| 12/2022 | 35 câu ✅ | 20 câu ✅ | 12 câu (không chấm) |
| 7/2023 | 32 câu ✅ | 19 câu ✅ | 12 câu (không chấm) |

Tổng đang dùng được: **140 câu có đáp án**.

### 3.3 Vì sao thiếu — theo từng nguyên nhân

**(a) Phần nghe hiểu 聴解 — thiếu audio và script (cả 5 đề)**
- PDF chỉ in 4 lựa chọn của mỗi câu, không có file mp3 cũng không có transcript.
- 問題3 và 問題5 trong đề còn ghi rõ「問題用紙に何もいんさつされていません」→ trên giấy không có gì.
- Hiện app vẫn hiển thị phần này (đúng cấu trúc, đếm giờ 40 phút) nhưng **không chấm điểm**, có banner giải thích.
- **Cần**: file audio + đáp án (hoặc transcript) cho từng đề.

**(b) Các câu sắp xếp ★ (問題2 phần ngữ pháp) — mất vị trí ô trống**
- Khi PDF bị làm phẳng thành text, chỉ còn **một** dấu ★ và mất các ô trống còn lại, nên không biết ★ nằm ở ô thứ mấy → không xác định được đáp án.
- Đang bị **loại bỏ** khỏi đề (mỗi đề 5 câu).
- **Cần**: gõ lại thủ công vị trí ★ hoặc bỏ hẳn dạng này.

**(c) Bài đọc nằm trong PDF dưới dạng ảnh**
- Các bài đọc sau đây không có text nên câu hỏi tương ứng bị loại:
  - 問題3 (điền từ vào đoạn văn, 4 câu/đề) — đoạn văn là ảnh.
  - 問題4 (1) tờ rơi/thông báo — ảnh.
  - 問題7 (tìm kiếm thông tin, 2 câu/đề) — bảng thông tin là ảnh.
- **Cần**: đọc ảnh và gõ lại đoạn văn/bảng.

**(d) Đề 7/2022 mất toàn bộ phần ngữ pháp**
- File này in số câu và số lựa chọn ở layer riêng, cộng với việc không in tên phần 「文法・読解」 nên parser tách section sai; phần ngữ pháp bị gộp nhầm rồi bị loại khi lọc.
- **Cần**: viết nhánh parser riêng cho file này, hoặc gõ tay ~30 câu.

**(e) Đáp án do AI giải, chưa đối chiếu đáp án chính thức**
- 5 PDF **không kèm đáp án**. Toàn bộ 140 đáp án hiện có do Claude tự giải khi đọc đề.
- Độ tin cậy cao với 文字・語彙 và 文法, nhưng **nên đối chiếu lại với đáp án chính thức** khi có.
- File đáp án: `exam_answers.json` (key dạng `đề/phần/số-câu`, giá trị 1–4).

## 4. Nhiệm vụ tiếp theo (ưu tiên từ trên xuống)

1. **Bổ sung phần nghe**: nhận file audio + đáp án từ người dùng → thêm trường `audio` cho từng câu trong `exams.json`, thêm player vào màn hình thi (`drawPaper`), bỏ banner "không chấm điểm".
2. **Đề 7/2022 – phần ngữ pháp**: xử lý parser riêng hoặc nhập tay.
3. **Hai đề scan (7/2021, 12/2023)**: đọc ảnh → nhập JSON theo đúng schema ở mục 5.
4. **Khôi phục các bài đọc là ảnh** (問題3, 問題4(1), 問題7) cho 3 đề đã có.
5. **Đối chiếu lại 140 đáp án** với đáp án chính thức.
6. Cân nhắc: cho phép nộp sớm và xem lại bài trước khi hết giờ từng phần (hiện chỉ nộp rồi mới xem).

## 5. Schema `exams.json`

```jsonc
[{
  "id": "2022-12",
  "title": "Đề thi tháng 12/2022",
  "sections": [{
    "key": "moji",                         // moji | bunpou | choukai
    "name": "Từ vựng – Chữ Hán",
    "jp": "言語知識（文字・語彙）",
    "minutes": 30,                         // 30 / 70 / 40 theo chuẩn JLPT N3
    "mondai": [{
      "no": 1,
      "instruction": "問題 1 ＿＿＿の言葉の…",
      "passage": "",                       // bài đọc chung của mondai (nếu có)
      "questions": [{
        "n": 1,                            // số thứ tự liên tục trong phần (dùng cho navigator)
        "label": 1,                        // số câu gốc in trên đề
        "q": "この店では、いろいろな容器を売っています。",
        "opts": ["ようぎ", "ようき", "どうぐ", "どうく"],
        "answer": 2                        // 1-based; null = không chấm (phần nghe)
      }]
    }]
  }]
}]
```

Quy ước: `answer: null` → câu vẫn hiển thị, có đếm giờ, nhưng không tính điểm.

## 6. Pipeline trích xuất (trong `scratchpad/`)

Đã copy vào repo: thư mục **`tools/`**. Đáp án nằm ở **`exam_answers.json`** (thư mục gốc repo).

| Script | Việc |
|---|---|
| `resolve.py` | dò đường dẫn 5 PDF đề thi → `exam_files.json` (tên file có Unicode tổ hợp, phải glob chứ không hardcode) |
| `clean_text.py` | trích text đã lọc watermark ("Tôi Yêu Ngoại Ngữ Group / Yuuki Bùi": font Helvetica, màu `(0.0,)`, cỡ >15.5) |
| `parse_exam2.py` | text → cấu trúc phần / 問題 / câu / 4 lựa chọn |
| `build_exams.py` | ghép với `exam_answers.json` → `exams.json` (loại câu ★, câu không có đáp án, mondai trùng số) |
| `show_parsed.py` | in đề ra để giải đáp án bằng tay |
| `parse_grammar2.py`, `build_reading.py`, `parse_kanji.py`, `parse_vocab.py` | pipeline của 4 phần dữ liệu còn lại |

Chạy lại toàn bộ đề thi: `cd tools && python resolve.py && python build_exams.py`
(`resolve.py` phải chạy trước vì nó dò lại đường dẫn 5 PDF trong Downloads).

## 7. Những cái bẫy đã gặp (đừng lặp lại)

- **Không dùng heredoc bash** cho script chứa ký tự Unicode đặc biệt (⓵, ❶, ★…) — Git Bash lỗi "unexpected EOF". Dùng công cụ Write để tạo file.
- Tên PDF tiếng Việt dùng Unicode tổ hợp → `open()` với chuỗi hardcode sẽ `FileNotFoundError`. Luôn `glob`.
- `state-backup.json` sửa tay thì phải **tăng `savedAt`**, nếu không localStorage cũ sẽ thắng lúc khởi động.
- Khi thêm khóa mới vào state (vd `exams`), phải thêm migration trong `App.boot()` — dữ liệu cũ của người dùng không có khóa đó và sẽ crash.
- Người dùng giao tiếp bằng **tiếng Việt**; mọi chuỗi trong UI đều tiếng Việt.
