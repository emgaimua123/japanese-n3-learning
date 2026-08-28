# GunGun N3 Trainer

Ứng dụng desktop (Windows) luyện **từ vựng** và **kanji** JLPT N3 theo giáo trình GunGun Joutatsu N3.

## Chạy ứng dụng

Chạy file `dist\GunGunN3Trainer.exe` (không cần cài đặt gì thêm — chỉ cần Windows 10/11 có WebView2, mặc định đã có sẵn).

## Tính năng

- **Session từ vựng**: mỗi session học 10 từ mới (theo thứ tự giáo trình) → ôn tập từng từ (kanji/kana, cách đọc, âm Hán-Việt, từ loại, nghĩa) → quiz.
- **Session kanji**: mỗi session 4–5 chữ kanji kèm toàn bộ từ vựng đi theo chữ đó (âm 訓/音, Hán-Việt, câu chuyện ghi nhớ).
- **Quiz**: Nhật → Việt là trắc nghiệm 4 đáp án; Việt → Nhật là tự luận (chấp nhận kanji hoặc kana). Chấm ngay từng câu kèm giải thích chi tiết.
- Sau quiz: ôn lại các từ sai / làm lại quiz / kết thúc session.
- **Kiểm tra bài cũ**: từ session thứ 2, trước khi vào bài mới sẽ có quiz ôn một session ngẫu nhiên trong quá khứ.
- **Dashboard**: số session, số từ/kanji đã học, tỷ lệ đúng quiz, tỷ lệ thuộc bài cũ, biểu đồ kết quả theo session.
- Tiến trình lưu cục bộ (localStorage của WebView2 + bản sao JSON tại `%LOCALAPPDATA%\GunGunN3Trainer\`).

## Cấu trúc

| File | Vai trò |
|---|---|
| `app.py` | Host desktop (pywebview + WebView2) |
| `web/index.html` | Toàn bộ giao diện + logic (1 file) |
| `vocab.json` | 2016 từ vựng trích từ PDF "GG N3 - TỪ VỰNG TỔNG HỢP" |
| `kanji.json` | 337 kanji + 1073 từ đi kèm trích từ PDF "GUNGUN N3 - KANJI" |

## Build lại exe

```powershell
python -m pip install pywebview pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name GunGunN3Trainer --icon icon.ico --add-data "web;web" --add-data "vocab.json;." --add-data "kanji.json;." app.py
```

Kết quả nằm ở `dist\GunGunN3Trainer.exe`.
