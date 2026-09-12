# Audio cho phần nghe hiểu (聴解)

Thả file mp3 vào đây, ví dụ: `audio/2022-12/q1.mp3`

Sau đó khai báo trong `exams_manual.json` (đường dẫn tính từ thư mục `web/`, nên bắt đầu bằng `../audio/`):

```json
[{
  "id": "2022-12",
  "sections": [{
    "key": "choukai",
    "mondai": [{
      "no": 1,
      "questions": [
        { "label": 1, "audio": "../audio/2022-12/q1.mp3", "answer": 3 }
      ]
    }]
  }]
}]
```

Rồi chạy `cd tools && python build_exams.py` — dữ liệu này được merge đè lên kết quả
trích từ PDF nên không bị mất khi chạy lại script.

Nhớ thêm `--add-data "audio;audio"` vào lệnh build exe (xem README chính).
