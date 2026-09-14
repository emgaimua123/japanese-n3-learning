# GunGun N3 Trainer

Ứng dụng desktop (Windows) luyện **từ vựng**, **kanji**, **ngữ pháp**, **đọc hiểu** và **thi thử đề JLPT N3** theo giáo trình GunGun Joutatsu N3.

## Chạy ứng dụng

Giải nén file zip phát hành rồi chạy `GunGunN3Trainer.exe` (không cần cài đặt gì thêm — chỉ cần Windows 10/11
có WebView2, mặc định đã có sẵn). Nhớ giữ nguyên thư mục `resources\` cạnh file exe.

## Tính năng

- **Session từ vựng**: mỗi session học 10 từ mới (theo thứ tự giáo trình) → ôn tập từng từ (kanji/kana, cách đọc, âm Hán-Việt, từ loại, nghĩa) → quiz.
- **Session kanji**: mỗi session 4–5 chữ kanji kèm toàn bộ từ vựng đi theo chữ đó (âm 訓/音, Hán-Việt, câu chuyện ghi nhớ).
- **Quiz**: Nhật → Việt là trắc nghiệm 4 đáp án; Việt → Nhật là tự luận (chấp nhận kanji hoặc kana). Chấm ngay từng câu kèm giải thích chi tiết.
- Sau quiz: ôn lại các từ sai / làm lại quiz / kết thúc session.
- **Kiểm tra bài cũ**: từ session thứ 2, trước khi vào bài mới sẽ có quiz ôn một session ngẫu nhiên trong quá khứ.
- **Dashboard**: số session, số từ/kanji đã học, tỷ lệ đúng quiz, tỷ lệ thuộc bài cũ, biểu đồ kết quả theo session, checkpoint mục tiêu ngày (7 ngày gần nhất), lịch sử ôn tập (ngày giờ, thời lượng, điểm), đồng hồ trực tiếp.
- **Session ngữ pháp**: mỗi bài của sách là một session — học từng mẫu (cấu trúc, giải thích y hệt sách, ví dụ, đáp án luyện dịch của sách), rồi quiz dịch câu ví dụ Nhật → Việt. Bài dịch được chấm theo **nghĩa**, không khoá cứng một đáp án: ưu tiên Claude API (nhập key trong Cài đặt), nếu không có key thì dùng bộ chấm ngoại tuyến đối chiếu ý với từ điển trong app. Dù đúng hay sai đều hiện lại cấu trúc ngữ pháp gốc gắn với câu đó.
- **Đọc hiểu** (Học → Luyện đọc hiểu): 22 bài đọc luyện tập từ chương 5 đến 9. Làm xong mỗi câu có giải thích chi tiết, trích đúng câu chứa đáp án trong bài, lý do từng đáp án sai, và tip & trick cho dạng bài đó.
- **Đề thi JLPT** (Kiểm tra → Đề thi JLPT N3): thi thử đề thật theo đúng cấu trúc và thời gian chuẩn (Từ vựng–Chữ Hán 30 phút · Ngữ pháp–Đọc hiểu 70 phút · Nghe hiểu 40 phút). Có bảng điều hướng câu hỏi bên phải (đã làm / đánh dấu phân vân / chưa làm đổi màu khác nhau), đồng hồ đếm ngược, hết giờ tự chuyển sang phần tiếp theo; cuối bài có điểm từng phần và bảng xem lại từng câu.
- **Kiểm tra tổng hợp** (sidebar → Kiểm tra): gom tối đa N session ngẫu nhiên đã học thành bài kiểm tra có đếm giờ, không chấm từng câu — chấm điểm và giải thích toàn bộ ở cuối.
- **Ôn tập** (sidebar): tất cả session đã học dạng thẻ, sắp xếp theo số session / tỷ lệ đúng / ngày học; mở ra xem lại toàn bộ nội dung và làm quiz ôn tập.
- **Cài đặt** (sidebar, pop-up): đổi tên, giao diện, số từ/kanji mỗi session, số session mỗi bài kiểm tra, thời gian mỗi câu, mục tiêu session/ngày, khởi động cùng Windows, giờ nhắc học (thông báo Windows).
- Đếm ngược tới kỳ thi JLPT kế tiếp (Chủ nhật đầu tiên của tháng 7 và tháng 12) ngay dưới đồng hồ.
- **Học bù**: ngày không đạt mục tiêu được ghi nợ; học thêm vào ngày sau sẽ tự động trả nợ và tô đậm lại ngày đó (dấu ↻). App nhắc học bù bằng thông báo Windows (1 lần/ngày) và banner trên trang chính.
- **Chạy ngầm**: bấm X sẽ hỏi *Chạy ngầm ở khay* hay *Thoát hẳn* (có thể ghi nhớ lựa chọn). Khi chạy ngầm, app thu về biểu tượng 語 ở khay hệ thống — nhấn biểu tượng (hoặc mở lại shortcut) để hiện cửa sổ, chuột phải để thoát. Thông báo nhắc học vẫn hoạt động khi chạy ngầm.
- **Mục tiêu tự động**: mặc định app tự tính số session cần học mỗi ngày = số session chưa học ÷ số ngày còn lại tới kỳ JLPT, tính lại mỗi ngày một lần (chuyển sang tự đặt trong Cài đặt).
- **Lịch học**: bấm vào checkpoint 7 ngày để mở lịch tháng đánh dấu ngày đã học / học bù / chưa đủ / bỏ lỡ, chuyển được giữa lịch Từ vựng và Kanji.
- 5 theme: Sáng / Tối / 3 gradient động (Aurora đổi màu liên tục).
- Tiến trình lưu cục bộ (localStorage của WebView2 + bản sao JSON tại `%LOCALAPPDATA%\GunGunN3Trainer\`).

## Cấu trúc

| File | Vai trò |
|---|---|
| `app.py` | Host desktop (pywebview + WebView2) |
| `web/index.html` | Toàn bộ giao diện + logic (1 file) |
| `vocab.json` | 2016 từ vựng trích từ PDF "GG N3 - TỪ VỰNG TỔNG HỢP" |
| `kanji.json` | 337 kanji + 1073 từ đi kèm trích từ PDF "GUNGUN N3 - KANJI" |
| `grammar.json` | 151 mẫu ngữ pháp (26 bài) + 462 câu ví dụ + 462 câu luyện dịch kèm đáp án, trích từ PDF "GUNGUN N3 - NGỮ PHÁP" |
| `reading.json` | 22 bài đọc (chương 5–9) + 31 câu hỏi kèm đáp án, câu chứa đáp án, giải thích và tips |
| `exams.json` | 3 đề thi JLPT thật (7/2022, 12/2022, 7/2023) — 140 câu có đáp án. **File thành phẩm, sinh ra bởi `tools/build_exams.py`** |
| `exam_answers.json` | đáp án đề thi (key `<id đề>/<phần>/<số câu gốc>`), dùng khi dựng lại `exams.json` |
| `exams_manual.json` | dữ liệu đề thi nhập tay (đề scan, audio, bài đọc là ảnh) — được merge đè lên kết quả trích từ PDF |
| `tools/` | pipeline trích dữ liệu từ PDF (xem `HANDOFF.md` §8) |
| `EXAM-GAPS.md` | đề nào thiếu 問題 nào, câu số mấy — danh sách để nhập bổ sung |
| `audio/` | file nghe phần 聴解 — `audio/<id đề>/choukai.mp3`, mỗi đề một file dài cho cả phần |
| `source-pdf/` | toàn bộ PDF gốc (5 đề thi + 4 giáo trình) mà pipeline trích dữ liệu ra |
| `images/` | hình minh hoạ phần nghe cắt từ PDF (`tools/crop_images.py`) |

## Build lại exe

```powershell
python -m pip install pywebview pyinstaller pystray pillow anthropic
python build.py
```

Kết quả nằm ở `dist\GunGunN3Trainer\`:

```
GunGunN3Trainer.exe      ~34 MB — chỉ có Python runtime + pywebview + pystray
resources\
  web\index.html         giao diện
  vocab.json …           5 file dữ liệu
  audio\<id đề>\*.mp3    file nghe phần 聴解
  icon.ico
```

Tài nguyên **để ngoài exe** (kiểu `resources/` của app thường gặp) nên:
- exe nhẹ, build nhanh; audio ~73 MB không làm phình exe;
- sửa dữ liệu hay `web/index.html` thì chỉ cần chép đè vào `resources\`, **không phải build lại**;
- phát hành: nén cả thư mục `dist\GunGunN3Trainer` thành một file zip.

Lưu ý khi build:
- Phải **tắt app đang chạy** trước (exe bị khoá file) — `build.py` sẽ báo nếu gặp.
- Thiếu file trong `resources\` thì app hiện hộp thoại nói rõ thiếu gì (trước đây crash im lặng do `--windowed`).
- App vẫn chạy được với exe bản cũ (tài nguyên nhúng sẵn bên trong) — `res_base()` trong `app.py` tự nhận biết.

## Dựng lại dữ liệu từ PDF

```powershell
python -m pip install pdfplumber
cd tools
python parse_vocab.py; python fix_vocab2.py   # vocab.json
python parse_kanji.py                          # kanji.json
python parse_grammar2.py                       # grammar.json
python resolve.py; python build_exams.py       # exams.json (gộp exams_manual.json)
```

Các script tự tìm PDF trong `C:\Users\Admin\Downloads`. Riêng `reading.json` cần `tools/reading_raw.json` (xem `HANDOFF.md` §8).
