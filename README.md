# GunGun N3 Trainer

Ứng dụng desktop (Windows) luyện **từ vựng**, **kanji**, **ngữ pháp**, **đọc hiểu** và **thi thử đề JLPT N3** theo giáo trình GunGun Joutatsu N3.

[![Tải bản mới nhất](https://img.shields.io/github/v/release/emgaimua123/japanese-n3-learning?label=T%E1%BA%A3i%20b%E1%BA%A3n%20m%E1%BB%9Bi%20nh%E1%BA%A5t&style=for-the-badge&color=c2185b)](https://github.com/emgaimua123/japanese-n3-learning/releases/latest)
[![Lượt tải](https://img.shields.io/github/downloads/emgaimua123/japanese-n3-learning/total?label=L%C6%B0%E1%BB%A3t%20t%E1%BA%A3i&style=for-the-badge)](https://github.com/emgaimua123/japanese-n3-learning/releases)

## Tải về

**→ [Vào trang Releases để tải](https://github.com/emgaimua123/japanese-n3-learning/releases/latest)**, lấy file
`GunGunN3Trainer-v1.0-win64.zip` trong mục **Assets** (~140 MB). Hai file *Source code* bên dưới là mã nguồn,
người dùng bình thường không cần tải.

1. Giải nén — bên trong có sẵn `GunGunN3Trainer.exe` và thư mục `resources\`.
2. Chạy `GunGunN3Trainer.exe`. Không cần cài đặt gì thêm.
3. Giữ nguyên thư mục `resources\` cạnh file exe, đừng tách ra.

Yêu cầu: Windows 10/11 (WebView2 đã có sẵn trong máy). Lần đầu mở, Windows SmartScreen có thể cảnh báo vì
file chưa mua chứng chỉ ký số — bấm **More info → Run anyway**.

## Học gì trong app

**Từ vựng** — 2016 từ theo đúng thứ tự giáo trình. Mỗi session 10 từ mới: xem từng từ (kanji/kana, cách đọc,
âm Hán-Việt, từ loại, nghĩa) rồi làm quiz. Nhật → Việt là trắc nghiệm, Việt → Nhật là tự luận (gõ kanji hay
kana đều được). Sai câu nào giải thích ngay câu đó; hết quiz có thể ôn lại các từ sai hoặc làm lại từ đầu.

**Kanji** — 337 chữ kèm 1073 từ đi theo. Mỗi session 4–5 chữ: âm 訓/音, âm Hán-Việt, câu chuyện ghi nhớ, rồi
quiz kanji → hiragana và hiragana → kanji.

**Ngữ pháp** — 151 mẫu chia theo 26 bài của sách. Học từng mẫu (cấu trúc, giải thích, ví dụ, đáp án luyện dịch
của sách) rồi quiz dịch câu Nhật → Việt. Bài dịch chấm theo **nghĩa** chứ không khoá cứng một đáp án, nên diễn
đạt khác sách vẫn được tính đúng; đúng hay sai đều hiện lại mẫu ngữ pháp gắn với câu đó.

**Đọc hiểu** — 22 bài đọc luyện tập (chương 5–9). Mỗi câu có giải thích chi tiết, trích đúng câu chứa đáp án
trong bài, lý do từng đáp án sai và tip cho dạng bài đó.

**Đề thi JLPT N3** — 5 đề thật: 7/2021, 7/2022, 12/2022, 7/2023, 12/2023, đủ **504 câu** và chấm điểm được hết.

## Thi thử đề JLPT

Vào **Kiểm tra → Đề thi JLPT N3**. Đề chạy đúng cấu trúc và thời gian chuẩn: Từ vựng–Chữ Hán 30 phút ·
Ngữ pháp–Đọc hiểu 70 phút · Nghe hiểu 40 phút. Hết giờ tự chuyển sang phần tiếp theo; cuối bài có điểm từng
phần và bảng xem lại từng câu.

- **Bảng điều hướng** bên phải: câu đã làm, câu đánh dấu phân vân và câu chưa làm có màu khác nhau, bấm để nhảy tới.
- **Hai chế độ**: lần đầu vào thẳng *Kiểm tra*; từ lần thứ hai được chọn *Kiểm tra* hay *Luyện tập*.
  - *Kiểm tra*: băng nghe chạy một mạch từ đầu đến cuối, không dừng, không tua — như phòng thi thật.
  - *Luyện tập*: dừng, tua tới/lui 5 giây, đổi tốc độ thoải mái.
- **Phần nghe** có audio cho cả 5 đề kèm hình minh hoạ của từng câu. Băng dài hơn 40 phút thì thời gian làm bài
  lấy đúng bằng độ dài băng, không bị cắt giữa chừng.
- **Furigana**: các từ kanji trong đề có sẵn phiên âm, trừ từ đang được hỏi và đáp án của 問題1/問題2 (gắn vào
  là lộ đáp án). Bấm nút `ふりがな` trên thanh đề để tắt, khi đó đề giống hệt bản in.

## Theo dõi tiến độ

- **Dashboard**: số session đã học, số từ/kanji đã thuộc, tỷ lệ đúng quiz, biểu đồ kết quả theo session, lịch sử
  ôn tập và đồng hồ đếm ngược tới kỳ JLPT gần nhất (Chủ nhật đầu tiên của tháng 7 và tháng 12).
- **Kiểm tra bài cũ**: từ session thứ hai, trước khi vào bài mới app cho ôn lại một session ngẫu nhiên đã học.
- **Mục tiêu mỗi ngày**: mặc định app tự chia số session còn lại cho số ngày còn lại tới kỳ thi; muốn tự đặt thì
  đổi trong Cài đặt.
- **Học bù**: ngày nào không đạt mục tiêu sẽ bị ghi nợ, học thêm hôm sau là tự động trả nợ và tô đậm lại ngày đó.
- **Lịch học**: bấm vào dải checkpoint 7 ngày để mở lịch tháng, xem ngày nào đã học / học bù / chưa đủ / bỏ lỡ.
- **Ôn tập**: mọi session đã học nằm ở đây dạng thẻ, sắp xếp theo số session, tỷ lệ đúng hoặc ngày học.
- **Kiểm tra tổng hợp**: gom nhiều session ngẫu nhiên đã học thành một bài có đếm giờ, chấm điểm và giải thích
  toàn bộ ở cuối.

## Cài đặt trong app

Mở bằng nút **Cài đặt** ở thanh bên: đổi tên hiển thị, chọn 1 trong 5 giao diện (Sáng, Tối, 3 nền gradient động),
số từ/kanji mỗi session, số session mỗi bài kiểm tra, thời gian mỗi câu, mục tiêu session mỗi ngày, bật khởi động
cùng Windows và đặt giờ nhắc học.

**Nhắc học và chạy ngầm**: bấm X sẽ hỏi *chạy ngầm ở khay* hay *thoát hẳn* (ghi nhớ được lựa chọn). Chạy ngầm thì
app thu về biểu tượng 語 ở khay hệ thống — nhấn để hiện lại cửa sổ, chuột phải để thoát. Thông báo nhắc học vẫn
hoạt động khi chạy ngầm.

**Chấm dịch kỹ hơn bằng AI** (tuỳ chọn): phần quiz dịch mặc định dùng bộ chấm ngoại tuyến, miễn phí. Nếu muốn
nhận xét chi tiết hơn thì dán Claude API key của bạn vào Cài đặt rồi bấm nút 🤖 *Nhờ AI chấm kỹ* ở từng câu —
chỉ khi đó app mới gọi ra ngoài, và mỗi câu chỉ tính tiền một lần vì kết quả được nhớ lại. Không nhập key thì app
chạy hoàn toàn ngoại tuyến.

## Tiến trình của bạn được lưu ở đâu

Toàn bộ tiến trình nằm trên máy bạn, trong `%LOCALAPPDATA%\GunGunN3Trainer\`, gồm bản lưu chính và một bản sao
dự phòng dạng JSON — mất một bản thì app tự lấy bản còn lại, nên dọn dẹp trình duyệt hay cập nhật app đều không
làm mất dữ liệu học. Muốn chuyển sang máy khác thì chép nguyên thư mục đó. Gỡ app chỉ cần xoá thư mục đã giải
nén; xoá luôn thư mục trên nếu muốn xoá sạch tiến trình.

## Giấy phép

Mã nguồn phát hành theo [giấy phép MIT](LICENSE). Nội dung học (giáo trình GunGun Joutatsu N3, đề thi JLPT và
file nghe) thuộc bản quyền của các tác giả tương ứng, ở đây chỉ dùng cho mục đích học tập cá nhân.
