# PDF nguồn

Toàn bộ PDF gốc mà pipeline trong `tools/` trích dữ liệu ra. Trước đây chỉ nằm ở
`C:\Users\Admin\Downloads`, không có backup — xoá Downloads là mất nguồn vĩnh viễn.
Nay đưa hẳn vào repo.

Tên file đã đổi sang ASCII: tên gốc tiếng Việt dùng **Unicode tổ hợp**, mở bằng chuỗi
hardcode là `FileNotFoundError` (bẫy đã gặp, xem `README.md` §11). Bảng đối chiếu tên
gốc ở [`_manifest.md`](_manifest.md).

| Thư mục | Nội dung | Sinh ra |
|---|---|---|
| `exams/` | 5 đề thi JLPT N3 thật | `exams.json` (qua `tools/build_exams.py`) |
| `textbook/` | 4 PDF giáo trình GunGun N3 | `vocab.json`, `kanji.json`, `grammar.json`, `reading.json` |

`exams/2021-07.pdf` và `exams/2023-12.pdf` là **bản scan, không có lớp text** — đó là lý do
hai đề này chưa vào `exams.json`.

> ⚠️ Các script trong `tools/` **vẫn đang đọc PDF từ `~/Downloads`**, chưa trỏ vào thư mục này.
> Muốn chạy pipeline trên máy khác thì phải sửa `_find_pdf` / `resolve.py` cho trỏ về `source-pdf/`.

Audio phần nghe nằm ở `audio/<id đề>/choukai.mp3` (ngoài repo này, cùng nhóm dữ liệu nguồn).
