# GunGun N3 Trainer — Bàn giao & việc còn lại

> File này để mở session mới mà không mất ngữ cảnh. Cập nhật lần cuối: **14/09/2026**.
>
> Chỗ nào đánh dấu **❓CẦN BỔ SUNG** là thông tin chỉ người chủ dự án biết — điền vào giúp.

Repo: `emgaimua123/japanese-n3-learning` · nhánh chính `main` · thư mục làm việc trên máy:
`C:\Users\Admin\Coding\GitHub\japanese-n3-learning`

**Commit gần nhất**: `b56bdb0` (docs, **chưa push**) ← `0470467` ← `1e55f9b` (audio).

**Việc đang chờ ngay**: 35 câu nghe đã có audio nhưng **chưa có đáp án** nên chưa chấm điểm được —
xem **§6 việc 1**. Đáp án nhiều khả năng nằm ở cuối chính các file mp3 ("KEM" = kèm đáp án).

---

## 1. Ứng dụng là gì

App desktop Windows luyện thi JLPT N3 theo giáo trình GunGun Joutatsu, đóng gói thành exe + thư mục `resources/`.

- **Host**: `app.py` (450 dòng) — pywebview + WebView2, tray icon (pystray), thông báo Windows, auto-start, chấm dịch bằng Claude API.
- **Giao diện + toàn bộ logic**: `web/index.html` (một file, **2.930 dòng / 88 KB**, không framework, không build step).
- **Dữ liệu**: `vocab.json`, `kanji.json`, `grammar.json`, `reading.json`, `exams.json` — trích tự động từ PDF trong `C:\Users\Admin\Downloads` (xem §8).
- **Tiến trình người dùng**: localStorage của WebView2 **và** bản sao `%LOCALAPPDATA%\GunGunN3Trainer\state-backup.json` (lúc khởi động lấy bản mới hơn theo `savedAt`). Schema ở §4.
- **API key Claude**: lưu riêng ở `%LOCALAPPDATA%\GunGunN3Trainer\claude-api-key.txt` (plaintext), cố ý **không** nằm trong file backup tiến trình.

### Cài môi trường

```powershell
# chạy app + build exe
python -m pip install pywebview pyinstaller pystray pillow anthropic
# chỉ cần khi chạy lại pipeline trích PDF trong tools/
python -m pip install pdfplumber
```

Python đang dùng: `C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\python.exe`.

### Build lại exe

```powershell
python build.py
```

**Đổi kiến trúc đóng gói (14/09)**: exe **không còn nhúng tài nguyên**. Kết quả ra `dist\GunGunN3Trainer\`:
exe ~33.7 MB (chỉ Python runtime) + thư mục `resources\` (web/, 5 JSON, audio/, icon.ico) — tổng ~105 MB
do audio. Phát hành bằng cách nén cả thư mục thành zip.

- `app.py` tìm tài nguyên qua `res_base()`: bản đóng gói lấy `resources\` cạnh exe, không có thì lùi về
  `_MEIPASS` (exe bản cũ vẫn chạy), chạy từ source thì lấy thư mục repo.
- Thiếu file trong `resources\` → `_check_resources()` hiện MessageBox nói rõ thiếu gì, thay vì crash im lặng.
- Sửa dữ liệu / `web/index.html` thì **chỉ cần chép đè vào `resources\`**, không phải build lại exe.
- Phải **tắt app đang chạy** trước khi build (`build.py` báo lỗi rõ nếu exe bị khoá).
- `dist/` đã cho vào `.gitignore`; `dist/GunGunN3Trainer.exe` bản cũ đã `git rm --cached` (14/09) nên
  **repo không còn chứa exe** — phát hành bằng zip (GitHub Releases). File cũ vẫn còn trên đĩa máy này,
  xoá tay lúc nào cũng được.

### Test nhanh không cần build

`.claude/launch.json` có cấu hình `n3-trainer-web` chạy `python -m http.server 8123`; mở `http://localhost:8123/web/index.html`
(đường dẫn fetch là `../vocab.json`… nên **phải** serve từ thư mục gốc repo, không serve từ trong `web/`).

Giới hạn: khi không có pywebview, `App.loadData()` tự fetch 5 file JSON, còn `App.apiCall()` trả `null` cho mọi lời gọi → **không test được** ở chế độ này: chấm dịch bằng AI, tray, thông báo Windows, auto-start, backup ra file, hỏi khi bấm X.

> `.claude/launch.json` hardcode đường dẫn python của máy hiện tại — sửa lại nếu chạy trên máy khác.

---

## 2. Hợp đồng giữa host (`app.py`) và UI (`index.html`)

JS gọi Python qua `App.apiCall("<tên hàm>", ...)`; hỏng một bên là gãy bên kia.

| Hàm `Api.*` | Vào | Ra | Việc |
|---|---|---|---|
| `get_data()` | — | `{vocab,kanji,grammar,reading,exams}` | đọc 5 file JSON trong `resources/` (xem `res_base()`) |
| `get_api_key()` / `set_api_key(key)` | key | bool / chuỗi | quản lý `claude-api-key.txt` |
| `grade_translation(payload)` | `{jp,user,pattern,meaning,notes}` | `{ok,score,correct,feedback,grammar_note,suggested}` hoặc `{ok:false,error:"no_key"\|"no_sdk"\|...}` | chấm dịch bằng Claude |
| `save_backup(text)` / `load_backup()` | JSON string | bool / chuỗi | ghi `state-backup.json` (ghi atomic qua file `.tmp` + `os.replace`) |
| `get_autostart()` / `set_autostart(enabled,hidden)` | bool | `{enabled,hidden}` | registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| `set_reminders(times)` | `["HH:MM", …]` | — | luồng nền kiểm tra mỗi 15 giây |
| `set_makeup(total,days)` | số | — | UI đẩy số session đang nợ xuống để đưa vào nội dung thông báo |
| `set_close_pref(action)` / `close_choice(action)` | `"ask"\|"tray"\|"quit"` | — | hành vi khi bấm nút X |
| `test_notification()` | — | — | bắn thử toast |

**Chiều ngược lại (Python → JS)**: `app.py:217` gọi `evaluate_js("App.askCloseAction()")` khi người dùng bấm X mà chưa chọn hành vi. Đổi tên hàm JS này là gãy.

Cơ chế Windows-only đang dùng:

- **Single instance**: mutex `GunGunN3Trainer_SingleInstance`; lần chạy thứ hai ghi file cờ `%LOCALAPPDATA%\GunGunN3Trainer\show.request` rồi thoát, bản đang chạy dò file này mỗi giây để hiện cửa sổ lại.
- **Toast**: dựng XML rồi chạy PowerShell ẩn với AppUserModelID mượn của PowerShell (`app.py:26`) — nhờ vậy app không cần đăng ký shortcut trong Start Menu.
- **Tray**: pystray chạy ở thread riêng; `--tray` ở dòng lệnh = khởi động ẩn.

---

## 3. Trạng thái các phần

### Nội dung học

| Phần | Trạng thái | Ghi chú |
|---|---|---|
| Từ vựng | ✅ 2016 từ | đã làm sạch lỗi nuốt câu ví dụ vào nghĩa |
| Kanji | ✅ 337 chữ + 1073 từ | quiz: kanji→hiragana (tự luận), hiragana→kanji (trắc nghiệm) |
| Ngữ pháp | ✅ 151 mẫu / 26 bài (9 chương) | quiz dịch Nhật→Việt, chấm bằng Claude API hoặc bộ chấm offline |
| Đọc hiểu | ✅ 22 bài / 31 câu (chương 5–9) | đáp án + câu chứa đáp án + giải thích + tips do Claude soạn |
| Đề thi JLPT | đủ 5/5 đề, 407/504 câu đã nhập, **359 chấm được**; hai đề 2021-07 và 2023-12 xong hẳn | chi tiết: `EXAM-GAPS.md` |
| Audio phần nghe | ⚠️ có file cho 3 đề, chưa có đáp án | mỗi đề 1 file dài cho cả phần, xem §6 việc 1 |
| Hình phần nghe | ✅ 17 hình đã cắt và gắn vào câu | `images/`, `tools/crop_images.py` |

### Tính năng hệ thống (đều đã chạy, đừng làm hỏng khi sửa)

| Tính năng | Nơi cài đặt |
|---|---|
| Chấm dịch: **mặc định bộ chấm offline (miễn phí)**, có nút 🤖 "Nhờ AI chấm kỹ" mới gọi API (model đổi được trong Cài đặt: haiku-4.5 / sonnet-5 mặc định / opus-5, danh sách trắng ở `app.py:37`; effort `medium`). Kết quả AI nhớ trong localStorage `gungun_n3_aigrade_v1` nên gõ lại y hệt thì không tốn tiền lần nữa | `app.py:263`, `index.html:2712` (`gradeTranslation`) và `index.html:2740` (`offlineGrade`) |
| Học bù / ghi nợ session, banner nhắc | `index.html` (`pushMakeupToHost`) + `app.py:376` |
| Mục tiêu tự động (chia số session còn lại cho số ngày tới kỳ thi) | `goalsCfg()` / `autoGoal()` |
| Lịch học tháng, checkpoint 7 ngày, đếm ngược JLPT | `renderDash()` và các hàm lịch |
| Chạy ngầm ở tray + nhắc giờ học bằng toast | `app.py:110` (`_reminder_loop`), `app.py:181` (`_start_tray`) |
| Màn Ôn tập (thẻ session đã học, sắp xếp/mở lại) | `index.html` |
| 5 theme (2 tĩnh + 3 gradient động) | `THEMES` (`index.html:726`) |

**Không có test tự động nào** trong repo — checklist kiểm tra tay ở §9.

---

## 4. Schema tiến trình người dùng (`state`)

Khoá localStorage: **`gungun_n3_state_v1`** (`index.html:723`). Nội dung y hệt được mirror sang `state-backup.json`.

```jsonc
{
  "name": "…", "theme": "light", "savedAt": 1757600000000,
  "vocab":   { "sessions": [], "reviews": [] },
  "kanji":   { "sessions": [], "reviews": [] },
  "grammar": { "sessions": [], "reviews": [] },
  "reading": { "done": [] },
  "exams":   { "done": [] },        // lượt làm đề thi JLPT: {id,title,c,t,dur,…}
  "settings": {                     // mặc định: CFG_DEFAULTS, index.html:724
    "vocabPerSession": 10, "kanjiPerSession": 4, "examSessions": 5,
    "mcSec": 15, "typedSec": 25, "remindTimes": [], "closeAction": "ask"
  },
  "goals": { "mode": "auto", "vocabPerDay": 1, "kanjiPerDay": 1 }   // GOAL_DEFAULTS
}
```

- `settings` và `goals` luôn đọc qua `App.cfg()` / `App.goalsCfg()` (có merge mặc định) → thêm khoá mới ở đây thì an toàn.
- Các nhánh còn lại **bị truy cập trực tiếp** → thêm khoá mới phải thêm dòng migration trong `App.boot()` (`index.html:760-767`), nếu không state cũ của người dùng sẽ crash.
- Sửa tay `state-backup.json` thì phải **tăng `savedAt`**, không thì localStorage cũ thắng lúc khởi động (`pickState`, `index.html:812`).

---

## 5. ĐỀ THI — những chỗ còn thiếu (phần cần bổ sung)

### 5.1 Hai đề chưa xử lý được: PDF là ảnh scan

| File (id dùng trong `exams.json`) | Trang | Vấn đề |
|---|---|---|
| `Đề thi JLPT N3 7_2021.pdf` → id **`2021-07`** | 16 trang, 43 ảnh | **Không có text**, toàn ảnh scan |
| `ĐỀ THI JLPT N3 12.2023.pdf` → id **`2023-12`** | 30 trang, 24 ảnh | **Không có text**, toàn ảnh scan |

Máy chưa có `tesseract` (và `pytesseract`/`pdf2image`/`fitz` cũng chưa cài). Hai cách:

1. Cài Tesseract + gói ngôn ngữ `jpn`, rồi OCR (chất lượng OCR tiếng Nhật với furigana thường kém, phải sửa tay nhiều).
2. **Cách nên dùng**: đọc từng trang bằng vision (công cụ `Read` với `pages:"n"`) rồi gõ lại câu hỏi + 4 lựa chọn vào JSON. ~46 trang.

⚠️ Đọc kỹ **§8 — cảnh báo ghi đè** trước khi nhập tay bất cứ thứ gì vào `exams.json`.

📋 **Danh sách thiếu chi tiết tới từng câu: `EXAM-GAPS.md`** — phạm vi số câu của mỗi 問題 đã đối
chiếu tận PDF gốc (hai đề có cấu trúc lệch nhau, đừng áp một khuôn cho cả 5 đề).

### 5.2 Đề đã xử lý — số câu lấy được

| Đề | Từ vựng–Chữ Hán (30′) | Ngữ pháp–Đọc hiểu (70′) | Nghe hiểu (40′) |
|---|---|---|---|
| 7/2022 | 34 câu ✅ | **0 câu** ❌ | 11 câu — có audio 🎧, chưa có đáp án |
| 12/2022 | 35 câu ✅ | 20 câu ✅ | 12 câu — có audio 🎧, chưa có đáp án |
| 7/2023 | 32 câu ✅ | 19 câu ✅ | 12 câu — có audio 🎧, chưa có đáp án |

Tổng đang dùng được: **140 câu có đáp án** (đã kiểm lại bằng script, khớp với `exams.json`).

### 5.3 Vì sao thiếu — theo từng nguyên nhân

**(a) Phần nghe hiểu 聴解 — thiếu audio và script (cả 5 đề)**
- PDF chỉ in 4 lựa chọn của mỗi câu, không có file mp3 cũng không có transcript.
- 問題3 và 問題5 trong đề còn ghi rõ「問題用紙に何もいんさつされていません」→ trên giấy không có gì.
- Hiện app vẫn hiển thị phần này (đúng cấu trúc, đếm giờ 40 phút) nhưng **không chấm điểm**, có banner giải thích.
- ✅ **Audio đã có (14/09)** cho 3 đề đang dùng — một file dài cho cả phần, player sticky ngoài `#paperBody`,
  banner "không có audio" tự ẩn. Chi tiết ở §6 việc 1.
- ❌ **Vẫn thiếu đáp án và transcript** → 35 câu nghe chưa chấm điểm được.

**(b) Các câu sắp xếp ★ (問題2 phần ngữ pháp) — mất vị trí ô trống**
- Khi PDF bị làm phẳng thành text, chỉ còn **một** dấu ★ và mất các ô trống còn lại, nên không biết ★ nằm ở ô thứ mấy → không xác định được đáp án.
- Đang bị **loại bỏ** khỏi đề ở `tools/build_exams.py:47` (mỗi đề 5 câu).
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
- File đáp án: `exam_answers.json` ở thư mục gốc repo. Giá trị 1–4.
  🔑 **Key có dạng `<id đề>/<key phần>/<số câu GỐC in trên đề>`** — tức là ứng với trường **`label`** trong `exams.json`, **không phải `n`**.
  (Kiểm chứng: khớp theo `label` = 140/140, khớp theo `n` = 112/140. Lý do: `build_exams.py:57` tính key *trước* vòng đánh số lại ở dòng 72–75.)
- Cùng nhóm rủi ro: phần giải thích/đáp án của `reading.json` cũng do Claude soạn, **không có script hay prompt lưu lại** → không tái tạo và chưa được đối chiếu.

---

## 6. Nhiệm vụ tiếp theo (ưu tiên từ trên xuống)

> Việc 1–4 đều đụng `exams.json`. **Không sửa tay `exams.json`** — nó là file thành phẩm,
> bị ghi đè mỗi lần chạy `build_exams.py`. Nhập vào `exams_manual.json` rồi build lại (§8).

### 1. Gắn audio cho phần nghe hiểu 聴解 — ✅ ĐÃ XONG (14/09), còn thiếu đáp án

Audio lấy từ `C:\Users\Admin\Downloads` (5 file `YTDown.com_…CHOUKAI-JLPT-N3-<kỳ>-KEM….mp3`,
mỗi file là **một bản dài cho cả phần nghe**, ~35 phút). Đã chép 3 file ứng với 3 đề đang có:
`audio/2022-07/choukai.mp3`, `audio/2022-12/choukai.mp3`, `audio/2023-07/choukai.mp3`.
`exams_manual.json` gán file đó cho **cả 35 câu** 聴解 → `build_exams.py` đã merge.

Phía UI (`web/index.html`): vì một file dùng chung cho cả phần, player **không** nằm trong
`#paperBody` (drawPaper vẽ lại mỗi lần đổi câu → audio sẽ nhảy về đầu). Thay vào đó:

- `<div id="paperAudio">` nằm ngay dưới `.paperbar`, sticky, ngoài vùng bị vẽ lại;
- `syncPaperAudio(q, sec)` chỉ `load()` lại khi **đổi file** (so bằng `getAttribute("src")`);
- `show(id)` pause player khi rời `scr-paper` — không thì audio chạy tiếp ở màn khác.

Đã kiểm: phát → chuyển câu → vẫn đúng phần tử cũ, vẫn chạy, không mất vị trí; sang phần không có
audio thì ẩn hẳn và dừng; thoát màn thi thì dừng.

**Còn thiếu**: 35 câu nghe vẫn `answer: null` → nghe được nhưng **không chấm điểm**. Tên file có chữ
"KEM" (kèm đáp án) nên đáp án nhiều khả năng nằm ở cuối mỗi bản ghi — cần nghe rồi điền `answer`
vào `exams_manual.json` (hoặc `exam_answers.json` với key `<id>/choukai/<label>`).

Còn lại:
- 2 file audio của `2021-07` và `2023-12` vẫn nằm ở Downloads, chờ khi nào nhập xong 2 đề scan (§6.3).
- ❓ **Transcript**: app vẫn chưa hiển thị. Cách làm: thêm trường `script` cho câu, render ở bảng
  "Xem lại từng câu" trong `finishPaper()`.
- 問題3 và 問題5 của phần nghe **không in gì trên đề** (chỉ có ーメモー) nên `exams.json` hiện
  không có câu nào của hai 問題 này, dù audio có đọc. Muốn có thì phải nhập cả câu hỏi +
  4 lựa chọn vào `exams_manual.json` như đề mới (schema §7).

### 2. Đề 7/2022 — phần ngữ pháp bị mất (~30 câu)

`tools/parse_exam2.py` tách sai section vì file này không in tên phần 「文法・読解」 và in số câu
ở layer riêng. Hai hướng:

- Sửa parser: thêm nhánh riêng cho `2022-07` (nhận diện phần ngữ pháp theo 問題 numbering
  restart, hiện heuristic này đã có nhưng chưa đủ với layout đó).
- Hoặc nhập tay qua `exams_manual.json` (chắc ăn hơn): dùng
  `python tools/show_parsed.py 2022-07` để xem những gì parser đã đọc được.

Sau khi có câu hỏi thì **vẫn phải tự giải đáp án** (xem §5.3e) và thêm vào `exam_answers.json`
với key `2022-07/bunpou/<số câu gốc>`.

### 3. Hai đề scan 7/2021 và 12/2023 (~46 trang ảnh)

Không có text, máy chưa cài Tesseract. Cách nên dùng: đọc ảnh bằng vision
(`Read` với `pages:"n"`, tối đa 20 trang/lần) rồi gõ lại vào `exams_manual.json` theo schema §7.
Id đề: `2021-07`, `2023-12`. Đề mới **không cần** thêm vào `TAGS` của `build_exams.py`.

Khối lượng lớn → nên làm từng phần một (mỗi lần một 問題), commit dần.

### 4. Khôi phục các bài đọc đang là ảnh (3 đề đã có)

問題3 (điền từ vào đoạn văn, 4 câu/đề), 問題4 (1) (tờ rơi), 問題7 (bảng thông tin, 2 câu/đề).
Đọc ảnh → điền `passage` cho 問題 tương ứng + thêm lại các câu đã bị loại, qua `exams_manual.json`.

### 5. Đối chiếu 140 đáp án với đáp án chính thức

Toàn bộ đáp án hiện do AI giải (§5.3e). Nếu tìm được đáp án chính thức thì sửa
`exam_answers.json` rồi chạy lại `build_exams.py`. Nhớ: **key theo `label`** (số câu gốc in trên
đề), không phải `n`.

### 6. Việc nhỏ / nice-to-have

- Cho phép **nộp sớm và xem lại bài** trước khi hết giờ từng phần (hiện nộp xong mới xem được).
- Câu sắp xếp ★ (問題2) đang bị loại vì mất vị trí ô trống — nếu muốn có, phải nhập tay cả câu
  lẫn vị trí ★.
- ~~Cân nhắc bỏ `dist/GunGunN3Trainer.exe` khỏi git.~~ **Đã gỡ (14/09)** — phát hành bằng zip
  (exe + `resources/`) qua GitHub Releases.

---

## 7. Schema `exams.json`

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
      "passage": "",                       // bài đọc chung của mondai (nếu có), tối đa 2600 ký tự
      "questions": [{
        "n": 1,                            // đánh số lại 1..n trong phần, dùng cho navigator
        "label": 1,                        // số câu GỐC in trên đề — khớp với key trong exam_answers.json
        "q": "この店では、いろいろな容器を売っています。",
        "opts": ["ようぎ", "ようき", "どうぐ", "どうく"],
        "answer": 2                        // 1-based; null = không chấm (phần nghe)
      }]
    }]
  }]
}]
```

Quy ước: `answer: null` → câu vẫn hiển thị, có đếm giờ, nhưng không tính điểm.

---

## 8. Pipeline trích xuất (`tools/`)

| Script | Việc | Trạng thái |
|---|---|---|
| `resolve.py` | dò đường dẫn 5 PDF đề thi trong `Downloads` → `exam_files.json` (tên file có Unicode tổ hợp, phải glob chứ không hardcode) | ✅ trong repo |
| `clean_text.py` | trích text đã lọc watermark ("Tôi Yêu Ngoại Ngữ Group / Yuuki Bùi": font Helvetica, màu `(0.0,)`, cỡ >15.5) | ✅ |
| `parse_exam2.py` | text → cấu trúc phần / 問題 / câu / 4 lựa chọn | ✅ |
| `build_exams.py` | ghép với `exam_answers.json` → `exams.json` (loại câu ★, câu không có đáp án, mondai trùng số) | ✅ |
| `show_parsed.py` | in đề ra để giải đáp án bằng tay | ✅ |
| `crop_images.py` | cắt hình minh hoạ phần nghe ra `images/` + sinh đoạn JSON để gộp | ✅ **thêm 14/09** |
| `parse_docx_2021.py` | trích đề 2021-07 từ bản gõ lại .docx (cả đáp án + ảnh) | ✅ **thêm 14/09** |
| `parse_docx_2023.py` | trích đề 2023-12 từ bản gõ lại .docx (bố cục khác hẳn, tự tách ảnh hai câu một trang) | ✅ **thêm 15/09** |
| `check_exams.py` | soi lỗi `exams.json`: số câu so với format JLPT, lựa chọn trống/trùng, thiếu ảnh/audio | ✅ **thêm 14/09** |
| `parse_vocab.py` + `fix_vocab2.py` | PDF từ vựng → `vocab.json` (parse rồi dọn nghĩa lẫn câu ví dụ) | ✅ **đã bổ sung 13/09** |
| `parse_kanji.py` | PDF kanji → `kanji.json` | ✅ **đã bổ sung 13/09** |
| `parse_grammar2.py` | PDF ngữ pháp → `grammar.json` | ✅ |
| `parse_reading2.py` + `build_reading.py` | PDF đọc hiểu → `reading_raw.json` → `reading.json` | ✅ |

Cần `pdfplumber`. Chạy lại đề thi: `cd tools && python resolve.py && python build_exams.py`
(`resolve.py` phải chạy trước vì nó dò lại đường dẫn 5 PDF trong Downloads).

### ⚠️ Cảnh báo ghi đè — đọc trước khi nhập tay

✅ **ĐÃ XỬ LÝ (13/09) — chọn phương án (B).**

`build_exams.py` vẫn ghi đè `exams.json` từ PDF, **nhưng** trước khi ghi nó gộp thêm `exams_manual.json`
(hàm `merge_manual`). Vì vậy **dữ liệu nhập tay không còn bị mất** khi chạy lại script.

Cách dùng `exams_manual.json` (nằm ở thư mục gốc repo, mặc định là `[]`):

- Khớp theo **`id` đề → `key` phần → `no` của 問題 → `label` của câu**.
- Có sẵn thì **cập nhật từng trường** (trường không nhắc tới vẫn giữ nguyên); chưa có thì **thêm mới**.
- Thêm cả đề mới cũng được — cứ đặt một object đề đầy đủ theo schema §7.
- Sau khi gộp, số `n` được đánh lại 1..n cho mỗi phần nên navigator vẫn đúng.

Ví dụ gắn audio + đáp án cho một câu nghe:

```json
[{ "id": "2022-12",
   "sections": [{ "key": "choukai",
     "mondai": [{ "no": 1,
       "questions": [{ "label": 1, "audio": "../audio/2022-12/q1.mp3", "answer": 3 }] }] }] }]
```

Đã kiểm thử: thêm đề mới, sửa câu cũ, gắn audio — dữ liệu trích tự động vẫn nguyên vẹn.

### Những chỗ hardcode trong `tools/`

✅ **Đã dọn (13/09)**: mọi script ghi ra JSON bằng đường dẫn tương đối (`os.path.join(here, "..", …)`),
và tìm PDF bằng **so khớp không dấu** (`_find_pdf`) nên không còn trượt vì tên file Unicode tổ hợp.

Còn lại (cố ý giữ):

- Các script tìm PDF trong `~/Downloads` — đổi chỗ để PDF thì phải sửa.
- `build_exams.py` — `TAGS` liệt kê 3 đề trích được text; thêm đề mới (trích được text) phải thêm vào đây.
  Đề nhập tay thì **không cần** đụng `TAGS`, cứ bỏ vào `exams_manual.json`.

### Nguồn dữ liệu

✅ **Đã hết rủi ro mất trắng (14/09)**: toàn bộ PDF gốc và 5 file audio đã được commit vào repo
(~160 MB). Trước đó chỉ nằm ở `Downloads`, không có backup.

| Bộ dữ liệu | Nguồn trong repo |
|---|---|
| `vocab.json` | `source-pdf/textbook/vocab.pdf` |
| `kanji.json` | `source-pdf/textbook/kanji.pdf` |
| `grammar.json` | `source-pdf/textbook/grammar.pdf` |
| `reading.json` | `source-pdf/textbook/reading.pdf` (chương 5–9) |
| `exams.json` | `source-pdf/exams/<id đề>.pdf` — 5 đề |
| audio phần nghe | `audio/<id đề>/choukai.mp3` — 5 file, mỗi file cả phần |

Tên file đã đổi sang ASCII (tên gốc dùng Unicode tổ hợp, xem §11); bảng đối chiếu ở
`source-pdf/_manifest.md`. ⚠️ Các script trong `tools/` **vẫn đọc PDF từ `~/Downloads`**, chưa trỏ
về `source-pdf/` — việc nên làm tiếp nếu muốn chạy pipeline trên máy khác.

✅ **Đã xong (13/09)**: `parse_grammar2.py`, `build_reading.py`, `parse_reading2.py`, `fix_vocab2.py` lấy lại được từ scratchpad; `parse_vocab.py` và `parse_kanji.py` đã **mất hẳn nên được viết lại**. Đã kiểm chứng: chạy lại toàn bộ pipeline tái tạo **đúng 100%** cả 5 file JSON đang dùng (vocab 2016 / kanji 337 / grammar 151 / reading 22 / exams 3 — 0 mục sai lệch).

`build_reading.py` cần `tools/reading_raw.json` (đã có trong repo); muốn dựng lại file này từ PDF thì chạy `parse_reading2.py`.

---

## 9. Checklist kiểm tra tay (không có test tự động)

Sau khi sửa `web/index.html` — chạy ở chế độ web (`localhost:8123`) là đủ cho nhóm 1:

1. Vào tên mới → dashboard hiện đúng; học 1 session từ vựng → quiz → kết thúc; F5 lại thấy tiến trình còn.
2. Session kanji, session ngữ pháp (kiểm tra cả nhánh chấm offline khi không có key), 1 bài đọc hiểu.
3. Mở 1 đề thi JLPT → đếm giờ chạy → nộp → xem điểm; kiểm tra tổng hợp.
4. Đổi qua cả 5 theme; mở Cài đặt sửa số từ/session rồi học thử.
5. Màn Ôn tập: mở lại 1 session cũ, làm quiz ôn tập.

Sau khi sửa `app.py` — phải build exe hoặc chạy `python app.py` trên Windows:

6. Bấm X → hộp hỏi "chạy ngầm / thoát hẳn"; chọn chạy ngầm → có icon 語 ở khay, bấm vào hiện lại cửa sổ.
7. Mở exe lần thứ hai → không mở 2 cửa sổ, cửa sổ cũ hiện lên.
8. Cài đặt → "Thử thông báo" → toast hiện; đặt giờ nhắc trước 1 phút → đợi toast.
9. Bật/tắt khởi động cùng Windows → kiểm tra khoá `Run` trong registry.
10. Nhập API key → làm 1 câu dịch → thấy nhận xét của Claude (`source` khác `"offline"`).
11. Tắt app → mở lại → tiến trình còn nguyên; thử xoá localStorage để chắc chắn `state-backup.json` khôi phục được.

---

## 10. Lỗi đã biết / nợ kỹ thuật

- ~~`App.resetAll()` dựng lại state thiếu khoá `exams` → crash màn Kiểm tra sau khi "Đặt lại toàn bộ dữ liệu" nếu chưa khởi động lại app.~~ **Đã sửa** (13/09/2026): object trong `resetAll()` giờ có đủ mọi nhánh mà `boot()` bảo đảm. Nếu sau này thêm nhánh mới vào `boot()`, nhớ thêm cả ở đây — đúng kiểu bẫy mô tả ở §11.
- ~~`README.md` mô tả tính năng đã cũ hơn thực tế.~~ **Đã cập nhật (13/09)**: thêm mục đề thi JLPT, `exams.json` / `exam_answers.json` / `exams_manual.json` / `tools/` / `audio/` vào bảng cấu trúc, lệnh build có `--add-data "audio;audio"`, và thêm mục "Dựng lại dữ liệu từ PDF".
- ~~Exe 35 MB commit thẳng vào git~~ **Đã xong (14/09)**: `dist/` vào `.gitignore`, exe cũ đã
  `git rm --cached`. Repo không còn chứa exe; phát hành bằng zip.
- Lịch sử git vẫn giữ các blob exe cũ nên `.git` **không tự nhỏ lại** (~301 MB, gồm cả PDF + audio mới
  thêm). Muốn thu gọn thật sự thì phải viết lại lịch sử (`git filter-repo`) và force-push — chỉ nên làm
  khi thấy nặng thật, vì nó phá mọi bản clone đang có.

---

## 11. Những cái bẫy đã gặp (đừng lặp lại)

- **Không dùng heredoc bash** cho script chứa ký tự Unicode đặc biệt (⓵, ❶, ★…) — Git Bash lỗi "unexpected EOF". Dùng công cụ Write để tạo file.
- Tên PDF tiếng Việt dùng Unicode tổ hợp → `open()` với chuỗi hardcode sẽ `FileNotFoundError`. Luôn `glob`.
- `state-backup.json` sửa tay thì phải **tăng `savedAt`**, nếu không localStorage cũ sẽ thắng lúc khởi động.
- Khi thêm khóa mới vào state (vd `exams`), phải thêm migration trong `App.boot()` — dữ liệu cũ của người dùng không có khóa đó và sẽ crash.
- Lệnh build thiếu một `--add-data` JSON → exe mở lên là crash, không có thông báo lỗi (vì `--windowed`).
- `build_exams.py` ghi đè `exams.json`, xem §8 (đã có cơ chế merge nên an toàn hơn).
- **Chạy script pipeline để debug là ghi đè luôn file JSON thật.** Đã có lần chạy thử `parse_grammar2.py` lúc nó còn lỗi → `grammar.json` bị ghi thành mảng rỗng. Khi thử nghiệm, hãy sao lưu file trước (xem cách làm trong `verify_*.py` ở scratchpad) hoặc kiểm tra lại bằng `git diff --stat` ngay sau khi chạy.
- **Đừng sửa file bằng `io.open(p, "w")` rồi mới encode chuỗi.** Mở chế độ `w` là file bị cắt sạch
  ngay lập tức; nếu lệnh `write()` sau đó ném lỗi (ví dụ chuỗi chứa surrogate do viết emoji bằng
  `📋`) thì file còn lại 0 byte. Đã làm mất `HANDOFF.md` đúng kiểu này (14/09, khôi phục
  được bằng `git show <sha>:HANDOFF.md`). Dùng công cụ Edit, hoặc ghi ra file tạm rồi `os.replace`.
- Người dùng giao tiếp bằng **tiếng Việt**; mọi chuỗi trong UI đều tiếng Việt.
