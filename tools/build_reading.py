# -*- coding: utf-8 -*-
"""Build reading.json: cleaned passages + answers/explanations/tips written by hand."""
import sys, io, json, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reading_raw.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reading.json")

JUNK = re.compile(r"(ĐỌC HIỂU|DUNG MORI|CHUYÊN ĐỀ|KỸ NĂNG|TÀI LIỆU|GUNGUN)")

TYPES = {
    5: "Hỏi chi tiết・内容理解",
    6: "Hỏi lý do – nguyên nhân・理由",
    7: "Hỏi chỉ thị từ・指示語",
    8: "Hỏi ý tác giả・主張",
    9: "Thông báo & email・情報検索",
}

TIPS = {
5: [
 "Đề cho một từ khoá đã xuất hiện trong bài rồi hỏi giải thích về nó: 〜について、筆者はどのように考えているか / 筆者は〜について、どう述べているか.",
 "Bước 1: đọc kỹ câu hỏi, gạch chân đúng nội dung được hỏi (từ khoá).",
 "Bước 2: đọc lướt cả bài để nắm đề tài, khoanh vùng chỗ xuất hiện từ khoá đó.",
 "Bước 3: đọc thật kỹ vùng vừa khoanh — câu trả lời gần như luôn nằm trong 1–2 câu quanh từ khoá.",
 "Bước 4: so từng đáp án với vùng đó. Đáp án đúng thường diễn đạt lại (言い換え) chứ không chép nguyên văn.",
 "Mẹo loại trừ: đáp án sai hay thêm chi tiết lạ (mắt sáng hơn, ngón tay nhanh hơn…) hoặc đổi mức độ (少し違う → 全く違う).",
],
6: [
 "Câu hỏi có なぜ / どうして: lời giải thích thường nằm ngay cạnh chỗ chứa nội dung được hỏi.",
 "Bám vào các dấu hiệu chỉ nguyên nhân: 〜から、〜ので、〜ため（に）、〜ことから、〜おかげで (tích cực)、〜せいで (tiêu cực).",
 "Từ nối cần chú ý: なぜなら（ば）、というのは、なぜかというと、そのため、したがって.",
 "Cấu trúc hay gặp: 〜のは〜からだ / なぜなら〜からだ・ためだ / 〜によって・により.",
 "Luôn tự hỏi: điều này là tác giả viết trong bài, hay mình đang tự suy diễn?",
 "Đáp án sai thường: sai tiểu tiết, nội dung không hề có trong bài, hoặc mang tính suy diễn.",
],
7: [
 "Chỉ thị từ (指示語) thay thế cho nội dung đã nói trước đó — hoặc sẽ nói ngay sau đó.",
 "Quy trình: xác định vị trí chỉ thị từ → đọc lùi 1–3 câu → tìm nội dung nó thay thế → so đáp án ngay.",
 "Nếu chưa rõ, đọc thêm 1 câu phía sau: nhiều khi tác giả giải thích ngay sau đó.",
 "これ / このこと / こうした → gần như luôn chỉ ý vừa nói ngay trước.",
 "それ / そのこと / そうした → chỉ ý đã nói xa hơn, hoặc kết quả rút ra từ các câu trước.",
 "この場合 / このとき → tình huống cụ thể vừa mô tả; こういう＋danh từ → ví dụ/tình huống vừa nêu.",
 "Mẹo kiểm chứng: thay đáp án vào đúng vị trí chỉ thị từ, đọc lại câu xem có xuôi nghĩa không.",
],
8: [
 "Dạng hỏi thông điệp bao trùm: 筆者が最も言いたいことはどれか / 筆者の考えに合うのはどれか.",
 "Bước 1: đọc lướt toàn bài nắm đề tài, chú ý đặc biệt câu mở đoạn và đoạn kết.",
 "Bước 2: đọc kỹ chỗ có từ tổng hợp ý (要するに、つまり、このように、だから) và chỗ chuyển ý mạnh (しかし、ところが) — ý chính hay nằm sau khi tác giả bác bỏ quan điểm.",
 "Chú ý đuôi câu thể hiện chủ quan: 〜べきだ、〜たい、大切だ、重要だ、〜ではないだろうか.",
 "Bước 3: khái quát hoá — nếu bài có nhiều ví dụ thì các ví dụ đều phục vụ một luận điểm chung.",
 "Bước 4 (loại trừ): quá hẹp (chỉ 1 ví dụ), quá rộng (điều bài không nói), ngược ý, hoặc chỉ là chi tiết phụ.",
],
9: [
 "Dạng email/thông báo: mở đầu → nội dung chính → yêu cầu/hành động → lời kết.",
 "Bước 1: xác định người gửi – người nhận – bối cảnh (thường ở ngay đầu).",
 "Bước 2: tìm mục đích chính, bám các từ khoá ご案内、お知らせ、お願い、ご確認、ご提案、ご報告.",
 "Bước 3: gạch chân thông tin then chốt — ngày giờ, địa điểm, số lượng, điều kiện (thường nằm ở đoạn giữa).",
 "Bước 4: câu hỏi về việc cần làm thì bám các mẫu 〜てください、お願いします、〜ていただけませんか、可能でしょうか.",
 "Cẩn thận bẫy số liệu: ngày bắt đầu/kết thúc, giá gốc và giá đã giảm, phần nào được gia hạn và phần nào không.",
],
}

# answers[(chapter, block_no)] = list of (answer_index, evidence_jp, why, [wrong notes])
A = {}

A[(5, 1)] = [(2,
  "そのため、子どもの集中力や想像力、思考力を育てる効果があるらしい。",
  "Câu này nói origami có tác dụng nuôi dưỡng khả năng tập trung, trí tưởng tượng và tư duy cho trẻ. Đáp án ③「形を想像したり、考えたりする力が身につく」chính là cách diễn đạt lại (言い換え) của 想像力・思考力を育てる.",
  ["① Bài chỉ nói origami dùng tay làm việc tỉ mỉ, không hề nói ngón tay cử động nhanh hơn.",
   "② Bài không nhắc gì đến mắt tốt lên — đây là thông tin hoàn toàn mới.",
   "④ 「世界に誇れる日本の文化」là tác giả khen origami là nét văn hoá đáng tự hào, không phải người chơi sẽ tự hào được với thế giới."])]

A[(5, 2)] = [(2,
  "写真で見た商品の色と実際の商品の色が少し違っていた。… でも、サイズも少し小さくてすぐに足が痛くなってしまった。",
  "Thất bại gồm hai điểm: màu thật khác ảnh và size hơi nhỏ. Đáp án ③ gộp đúng cả hai (màu và kích cỡ khác so với ảnh đã xem).",
  ["① Ngược lại: cuối bài tác giả khuyên nên mua loại đã từng mua rồi.",
   "② Bài nói rõ 返品はできる (trả lại được), chỉ không đổi được.",
   "④ Bài dùng 少し違って (hơi khác), còn đáp án này nói 全く違う色 (màu hoàn toàn khác) — sai mức độ."])]

A[(5, 3)] = [(1,
  "この時期は気温の変化が大きいので、風邪を引く人も多い。そのため、着るものや食べるものに注意して、体調に気をつける必要がある。",
  "そのため nối trực tiếp nguyên nhân (dễ cảm) với việc cần làm (chú ý sức khoẻ). Đáp án ② nêu đúng: vì có ngày ấm ngày lạnh nên phải giữ gìn để không bị cảm.",
  ["① Bài nói thay đổi trong một khoảng ngắn (mấy ngày trong tuần), không phải 1日の間 (trong một ngày).",
   "③ Bài chỉ nói chú ý đồ ăn/đồ mặc, không bắt mỗi ngày phải ăn đồ nóng và mặc áo khoác.",
   "④ Xem dự báo là để kiểm tra 気温 (nhiệt độ), không phải xem có mưa hay không."])]

A[(5, 4)] = [
 (3,
  "この時期は、公園の桜の木の下で飲んだり、食べたりしてパーティーをしている人がたくさんいます。",
  "そんな花見 chỉ ngược lại kiểu hanami vừa mô tả ở câu ngay trước: tụ tập ăn uống, mở tiệc dưới gốc anh đào. Đáp án ④「桜の花を見ながらみんなで食事をする」khớp đúng.",
  ["① Chỉ 見学する (tham quan ngắm) là thiếu phần ăn uống — điểm cốt lõi của そんな花見.",
   "② 休憩 (nghỉ ngơi) không phải nội dung được nói tới.",
   "③ Bài không hề nhắc đến hoà nhạc."]),
 (0,
  "桜を見ながら飲んだり、食べたりしなくても、きれいな桜の花を見ているだけで、春を感じることができます。",
  "Mẫu 〜だけで chỉ rõ điều kiện: chỉ cần ngắm hoa anh đào đẹp là đã cảm nhận được mùa xuân. Vậy hành động cần là 桜の花を見る → đáp án ①.",
  ["② Lái xe dạo chỉ là cách gia đình tác giả đi ngắm, bản thân việc lái xe không phải điều làm cảm nhận mùa xuân.",
   "③ 「トンネル」là hình ảnh ví von hàng cây tạo thành, không phải việc ai đó làm.",
   "④ Mang cơm hộp ra công viên là chuyện ở đoạn cuối, không phải câu trả lời cho (2)."])]

A[(6, 1)] = [(1,
  "実際に、そのめがねを買って、使ってみたら、目が疲れにくくなった。これがあったら、仕事も楽になりそうだ。",
  "Câu chứa đáp án đứng ngay trước 仕事も楽になりそうだ: nhờ kính mà mắt đỡ mỏi. Vậy lý do là 目が疲れにくいから → ②.",
  ["① Bài không nói giờ làm ngắn đi.",
   "③ Kính chống nắng chỉ là hình ảnh so sánh; kính này bảo vệ mắt khỏi ánh sáng máy tính, không phải ánh mặt trời.",
   "④ Khối lượng công việc dùng máy tính không hề giảm."])]

A[(6, 2)] = [(3,
  "しかし、日本人は目立つことがあまり好きではないため、スーツや制服のような黒や茶色、灰色などの服を選んでしまうのかもしれない。",
  "〜ため（に）là dấu hiệu chỉ nguyên nhân. Lý do người Nhật chọn màu tối là vì không thích nổi bật → ④.",
  ["① Mặc suit/đồng phục là ví dụ dẫn dắt, không phải lý do cho việc tự chọn quần áo màu tối.",
   "② Ngược với bài: suit và đồng phục vốn là màu tối.",
   "③ Bài không nói người Nhật ghét việc chọn quần áo."])]

A[(6, 3)] = [(2,
  "それでも、電車やバスがない田舎では買い物や病院に行くために、高齢者は車を運転しなければいけない。",
  "〜ために ở đây chỉ mục đích/lý do: ở nông thôn không có tàu xe nên phải lái xe để đi chợ, đi bệnh viện → ③.",
  ["① Mắt kém và phản xạ chậm là lý do người già NÊN ngừng lái, không phải lý do phải lái.",
   "② Bài không nhắc đến giá vé tàu xe, chỉ nói không có tàu xe.",
   "④ Suy diễn — bài không nói xã hội Nhật nguy hiểm."])]

A[(6, 4)] = [(0,
  "そのうえ、タオルよりも薄くて場所を取らないし、洗濯してもすぐに乾くので、とても便利だ。",
  "Lý do gồm: dùng thay khăn tắm/khăn quàng (nhiều công dụng) và mỏng, không chiếm chỗ, mau khô. Đáp án ① gói đúng hai ý đó: 薄くて、さまざまな使い方ができて便利.",
  ["② Bài không nói tenugui mềm; điểm mạnh là mỏng và nhanh khô.",
   "③ Chuyện màu không phai không hề được nhắc tới.",
   "④ Dùng thay khăn quàng là công dụng, không phải để làm đẹp thời trang."])]

A[(6, 5)] = [(2,
  "郵便局にはその時代や季節に合わせたすてきなデザインの切手が発売されていて、目を楽しませてくれる。… そんな切手を見ていると、楽しくなって欲しくなってしまう。",
  "Chuỗi nhân quả: tem có thiết kế hợp thời và hợp mùa → nhìn thấy thì thích → mua dù không cần. Vậy lý do là ③.",
  ["① Người sưu tầm tem giới hạn là 中には…人もいる (có những người khác), không phải tác giả.",
   "② Bài không so sánh tem mới đẹp hơn tem cũ.",
   "④ Ở cửa hàng tiện lợi tác giả nói rõ 買うことはない (không mua)."])]

A[(7, 1)] = [(0,
  "駅に見たことがある顔の人がいました。高校の同級生か、それとも塾に行っていたときの知り合いかと、その時私はしばらく考えました。",
  "Đọc lùi lại ngay trước その時: tác giả nhìn thấy một người quen mặt ở ga và đang đoán xem đó là ai. Đáp án ① diễn đạt đúng tình huống đó.",
  ["② Bài không kể lúc đang đi học thêm cùng người quen.",
   "③ Lúc đó tác giả chưa biết là ai, chưa hề gặp lại bạn cấp ba.",
   "④ Là ở 駅 (nhà ga), không phải trên tàu."])]

A[(7, 2)] = [(1,
  "酸っぱくて好きじゃないという人もいる。酸っぱくて食べにくいと感じるのは、キウイフルーツが甘くなる前に食べてしまっているのかもしれない。",
  "そういう人 chỉ nhóm người vừa nhắc: thấy kiwi chua nên không thích, thấy khó ăn. Đáp án ②「味があまり好きではない人」khớp đúng.",
  ["① Ngược ý: đây là nhóm người thích vì ngọt.",
   "③ Chuyện ăn vỏ nằm ở đoạn sau そういう人, không phải nội dung nó thay thế.",
   "④ Bài không nói họ không muốn ăn lúc quả còn cứng — chính họ đã lỡ ăn khi chưa chín."])]

A[(7, 3)] = [(0,
  "「何が食べたい？」と聞いたら、「何でもいいよ。」と友人は言いました。…「何でもいいよ。」と言ったのに、実際にはそうではない人がときどきいます。",
  "そう thay cho 「何でもいい」. そうではない人 = người miệng nói 'gì cũng được' nhưng thực tế lại không phải vậy — như người bạn trong bài: bác bỏ hết đề xuất và mãi không quyết được ăn gì → ①.",
  ["② Đây là LÝ DO được giải thích ở câu sau (調べてみると…), trả lời cho なぜでしょうか chứ không phải nội dung mà そう thay thế. Bẫy rất hay gặp: đáp án đúng về nội dung nhưng trả lời sai câu hỏi.",
   "③ Bài không nói bạn ấy kén ăn nhiều thứ.",
   "④ Bạn ấy không phủ định gay gắt mà chỉ nêu lý do nhẹ nhàng (辛いのは苦手、昨日食べたばかり)."])]

A[(7, 4)] = [(3,
  "母は父を心配していましたが、とてもがっかりしていました。そんな様子を見て、私が母と山に行くことにしました。",
  "Đọc lùi đúng một câu: người mẹ rất thất vọng vì chuyến leo núi với bố bị lỡ. そんな様子 chính là dáng vẻ tiếc nuối ấy → ④.",
  ["① Bài không tả bố nằm mệt; chỉ nói bố bị cảm.",
   "② Người phân vân/tiếc là mẹ, không phải bố.",
   "③ Việc mẹ đi bộ mỗi sáng là thông tin nền ở đầu bài, không phải 様子 vừa được nhắc."])]

A[(7, 5)] = [(1,
  "妹は、自分が食べているお菓子があっても、私が食べているものを食べたいと言いました。使っていないおもちゃも、私が使い出すとすぐに「ちょうだい」と言ってきました。そんな時、母はいつも「お姉ちゃんなんだから、我慢しなさい。」と言いました。",
  "そんな時 gom lại hai tình huống vừa kể: em gái đòi đúng thứ mà 'tôi' đang ăn, đang dùng → ②「妹が「私」のものを欲しがった時」.",
  ["① Người lấy đồ chơi ra dùng trước là 'tôi', và vấn đề là em đòi lại.",
   "③ Ngược chiều: em đòi đồ của 'tôi', không phải 'tôi' ăn bánh của em.",
   "④ Lúc bị mẹ nhắc là lúc em ĐÒI, chưa phải lúc em đang dùng."])]

A[(8, 1)] = [
 (1,
  "私の住んでいる町は都会で、夜でも星があまり見えません。それは、電気の光が明るくて、空が暗くならないからです。… きれいな星を見たいなら、都会から離れなければいけません。",
  "〜からです chỉ rõ nguyên nhân: thành phố nhiều ánh đèn nên trời không đủ tối, không nhìn được sao; muốn ngắm sao đẹp phải rời thành phố → đó là lý do tham gia tour → ②.",
  ["① Bài không nói quê tác giả hay có thời tiết xấu.",
   "③ Chính tác giả rủ bạn đi (友人を誘って), không phải bị rủ.",
   "④ Chòm sao mùa hè chỉ là nội dung cuốn sách được tặng, không phải động cơ tham gia."]),
 (3,
  "「今日は月が明るくて、星が少し見えにくいですね。」… 私は電気の明かりが少なくても、月の光で星は見えにくくなるのか、と驚きました。",
  "Câu ngay sau それを聞いて nêu đúng điều khiến tác giả bất ngờ: ngay cả khi ít ánh đèn thì ánh trăng vẫn làm sao khó nhìn → ④.",
  ["① Tác giả không bất ngờ vì đèn ít — đó là điều đã biết trước khi đi.",
   "② Ngược ý: rời thành phố vẫn nhìn được nhiều sao hơn (都会よりきれいな星をたくさん見ることができました).",
   "③ Câu 'ít sao hơn tưởng' là lời của người bạn, còn điều khiến TÁC GIẢ ngạc nhiên là nguyên nhân do mặt trăng."]),
 (2,
  "季節ごとで星座は変わるので、今度は違う季節に来てみようと思いました。",
  "Câu kết bài thể hiện thái độ của tác giả: sẽ quay lại vào mùa khác để xem chòm sao khác → ③.",
  ["① Ngược ý: tác giả vẫn xem được nhiều sao và muốn quay lại.",
   "② Bài không đặt điều kiện 'trăng sáng thì không đi'.",
   "④ Sai chi tiết: tác giả không hề nói không tìm thấy chòm sao nào."])]

A[(8, 2)] = [
 (0,
  "建物が壊れたり、自動車などの重いものが飛ばされたりするなどの被害が出ている。その被害は台風被害と似ている。",
  "Câu nói rõ điểm giống nhau nằm ở THIỆT HẠI do gió mạnh gây ra (nhà cửa hỏng, vật nặng bị thổi bay) → ①.",
  ["② Đây là đặc điểm riêng của vòi rồng (xảy ra quanh năm khắp nơi), không phải điểm giống bão.",
   "③ Phạm vi hẹp, thời gian ngắn chính là 違う点 (điểm KHÁC) mà bài nêu ngay sau đó.",
   "④ Thông tin cảnh báo là chuyện khác, không phải điểm tương đồng về thiệt hại."]),
 (1,
  "注意情報が出たときに外にいる場合は、建物の中に入って、窓がない部屋や地下室に避難しよう。",
  "Bài hướng dẫn rất rõ: đang ở ngoài thì vào trong nhà, trú ở phòng không cửa sổ hoặc tầng hầm → ②.",
  ["① Ngược ý: trong xe cũng không an toàn, phải rời xe ngay.",
   "③ Ngược ý hoàn toàn: đang ở trong nhà thì không được chạy ra ngoài.",
   "④ Phải TRÁNH XA cửa sổ vì kính có thể vỡ."]),
 (3,
  "山のような形の雲の近づいてきて、空が急に暗くなったり、冷たい風が吹いてきたり、雷が聞こえたりした時は竜巻が近くまで来ている。",
  "そのような時 gom các dấu hiệu vừa liệt kê ở câu trước: mây hình núi, trời tối sầm, gió lạnh, có sấm. Đáp án ④ nêu đúng hai dấu hiệu trong đó.",
  ["① Ngược ý: trời tối sầm chứ không sáng lên.",
   "② Bài nói trời tối nhưng không nhắc tới mưa — chi tiết thêm vào.",
   "③ Ngược ý: gió LẠNH thổi tới và mây kéo đến, không phải gió ấm và mây tan."]),
 (3,
  "山のような形の雲の近づいてきて、空が急に暗くなったり、冷たい風が吹いてきたり、雷が聞こえたりした時は竜巻が近くまで来ている。",
  "Câu này cho biết có thể nhận ra vòi rồng đang tới gần qua trạng thái bầu trời và gió → ④ là mô tả đúng.",
  ["① Ngược ý: thiệt hại của vòi rồng tương đương bão (台風と同じような被害).",
   "② Bài không nói hễ có cảnh báo là chắc chắn xảy ra vòi rồng.",
   "③ Sai: phạm vi của vòi rồng hẹp hơn bão, đó là 違う点 bài đã nêu."])]

A[(8, 3)] = [
 (0,
  "ビタミンCは、病気の予防や美容にいいと言われている。",
  "Câu hỏi hỏi người muốn đẹp da (肌をきれいにしたい) nên nạp chất nào; bài gắn 美容 (làm đẹp) với vitamin C → ①.",
  ["② たんぱく質 dùng để tạo cơ thể (体をつくる).",
   "③ マグネシウム làm chắc xương và răng.",
   "④ 鉄分 vận chuyển oxy đi khắp cơ thể."]),
 (3,
  "つぼみが柔らかくなくて、しっかりと集まっているものがいい。最後に、茎の中に隙間がないかを見よう。",
  "Bông cải tươi = nụ hoa khít chặt, không mềm + thân không có lỗ rỗng (tức thân chắc) → ④.",
  ["① Sai ở つぼみが広がった: nụ phải khít lại, không được xoè ra.",
   "② Sai màu: phải chọn xanh đậm, không phải vàng nhạt.",
   "③ Sai cả hai: thân có lỗ rỗng là bông đã già, và màu vàng là dấu hiệu không tươi."]),
 (0,
  "ブロッコリーはあまり調理しすぎると、栄養がなくなってしまう。できるだけ、短い時間で調理した方がいい。お湯で調理すると栄養が湯に流れ出してしまう。",
  "Nấu quá kỹ hoặc luộc sẽ mất chất, nên nấu nhanh (khuyên dùng lò vi sóng) → ① 短時間で、栄養が逃げない方法.",
  ["② Ngược ý: nấu lâu làm mất chất chứ không giữ được chất.",
   "③ Ngược ý: mục tiêu là giữ chất trong rau, không phải chiết chất ra.",
   "④ Nấu nướng không làm dinh dưỡng tăng lên."]),
 (2,
  "成長しすぎたブロッコリーは固くなって、味も少し悪くなる。",
  "Câu hỏi yêu cầu chọn ý KHÔNG khớp với bài. Bài nói bông cải già thì CỨNG lại, còn ③ nói mềm đi → đây là đáp án cần chọn.",
  ["① Khớp: ở Nhật bông cải là rau vụ đông.",
   "② Khớp: bài hướng dẫn xem màu, nụ và thân.",
   "④ Khớp: nấu không đúng cách thì dinh dưỡng mất đi."])]

A[(9, 1)] = [(2,
  "申し訳ありませんが、明日のミーティングを違う日に変えていただけませんか。",
  "Mẫu 〜ていただけませんか là lời nhờ vả — chính là mục đích của email: xin đổi lịch họp sang ngày khác → ③.",
  ["① Nakamura là người phải đi công tác, không nhờ ai đi thay.",
   "② Có đề xuất cả thứ Tư/thứ Năm tuần này lẫn tuần sau, nên không phải 'muốn dời sang tuần sau'.",
   "④ Trưởng phòng chỉ yêu cầu đi công tác, không hề huỷ cuộc họp."])]

A[(9, 2)] = [(2,
  "注文した商品は黒いペン10本、赤いペン5本、コピー用紙3箱でしたが、黒、赤、青のペンが5本ずつとコピー用紙3箱が届きました。",
  "Đối chiếu con số: đặt bút đen 10 → nhận 5 (thiếu 5); bút đỏ 5 → nhận 5 (đúng); bút xanh không đặt → nhận 5 (thừa). Vậy ③ đúng.",
  ["① Tổng số bút vẫn là 15 cây, không thiếu về tổng số — chỉ sai chủng loại.",
   "② Ngược ý: bút đen bị THIẾU chứ không thừa.",
   "④ Bút đỏ nhận đúng 5 cây như đặt, còn bút xanh là thừa chứ không thiếu."])]

A[(9, 3)] = [(1,
  "休館中はCD／DVDの返却期間が延長されますので、返却日を確認してください。",
  "Trong thời gian đóng cửa, hạn trả CD/DVD được gia hạn — tức không phải trả trong lúc đó → ②.",
  ["① Chỉ CD/DVD được gia hạn; sách vẫn phải trả vào thùng ブックポスト.",
   "③ Không bắt buộc trả hết trước khi đóng cửa: sách trả qua thùng, CD/DVD được gia hạn.",
   "④ Sai: CD/DVD dễ hỏng nên KHÔNG được bỏ vào thùng sách."])]

A[(9, 4)] = [(0,
  "今日の夜から明日の朝にかけて、県内に最接近することが予想されています。そのため、明日9月18日(水)の午前中は休校にします。",
  "Ngày mai là thứ Tư 18/9, nên hôm nay là thứ Ba — bão áp sát từ tối nay, tức từ tối thứ Ba phải đề phòng → ①.",
  ["② Chỉ nghỉ buổi sáng; buổi chiều sẽ thông báo sau, chưa chắc nghỉ.",
   "③ Ngược ý: thông báo dặn ở yên trong nhà, hạn chế ra ngoài.",
   "④ Thông báo về tiết chiều sẽ đăng trên trang web (ホームページ), không phải gửi email."])]

A[(9, 5)] = [(3,
  "もしマリアさんが参加するなら、私が一緒に申し込みをしておきますよ。申し込みは来週の水曜日までなので、その前に返事をください。",
  "Takako sẽ đăng ký giúp, hạn đăng ký là thứ Tư tuần sau → ④ khớp đúng.",
  ["① Maria mới chỉ được rủ, chưa trả lời nên chưa thể nói là sẽ tham gia.",
   "② Maria từng đi năm ngoái nên được giảm 5.000 yên, tức 25.000 chứ không phải 30.000.",
   "③ Trại từ 10/8 đến 12/8 là 3 ngày, không phải 2 ngày."])]


def clean_lines(lines):
    return [l for l in lines if l and not JUNK.search(l)]


def main():
    blocks = json.load(open(RAW, encoding="utf-8"))

    # chapter 9: 練習❺ was swallowed by the last option of block 4 - split it out
    # (must run before cleaning, which would strip the swallowed text away)
    for b in list(blocks):
        if not (b["chapter"] == 9 and b["no"] == 4):
            continue
        for q in b["questions"]:
            for i, o in enumerate(q["opts"]):
                if "練習❺" not in o:
                    continue
                head, tail = o.split("練習❺", 1)
                q["opts"][i] = head.split("お知らせ（")[0].strip()
                tail = tail.split("この文の内容について")[0]
                blocks.append({"chapter": 9, "no": 5, "label": "練習❺",
                               "passage": [tail],
                               "questions": [b["questions"].pop()] if len(b["questions"]) > 1 else [],
                               "tips_raw": []})
                break

    for b in blocks:
        b["passage"] = clean_lines(b["passage"])
        for q in b["questions"]:
            q["q"] = JUNK.split(q["q"])[0].strip()
            # two question lines can end up glued together - keep the first
            m = re.match(r"^(.+?か。)(?=.*か。)", q["q"])
            if m:
                q["q"] = m.group(1)
            # an option may have swallowed the next block's heading or question
            q["opts"] = [re.split(r"練習|この文の内容|このお知らせの内容|お知らせ（",
                                  JUNK.split(o)[0])[0].strip() for o in q["opts"]]

    out = []
    for b in sorted(blocks, key=lambda x: (x["chapter"], x["no"])):
        key = (b["chapter"], b["no"])
        ans = A.get(key, [])
        qs = []
        for qi, q in enumerate(b["questions"]):
            a = ans[qi] if qi < len(ans) else None
            if not a:
                print("!! missing answer for", key, "Q", qi + 1)
                continue
            idx, ev, why, wrong = a
            qs.append({"q": q["q"], "opts": q["opts"], "answer": idx,
                       "evidence": ev, "why": why, "wrong": wrong})
        if not qs:
            continue
        out.append({"id": "r%d-%d" % (b["chapter"], b["no"]),
                    "chapter": b["chapter"], "no": b["no"],
                    "type": TYPES[b["chapter"]],
                    "passage": "".join(b["passage"]),
                    "questions": qs, "tips": TIPS[b["chapter"]]})

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("readings:", len(out), "| questions:", sum(len(r["questions"]) for r in out))
    for ch in sorted({r["chapter"] for r in out}):
        rs = [r for r in out if r["chapter"] == ch]
        print("  ch%d (%s): %d bài, %d câu" % (ch, TYPES[ch], len(rs), sum(len(r["questions"]) for r in rs)))
    # sanity: every option list must have 4 entries and the answer must exist
    for r in out:
        for q in r["questions"]:
            if len(q["opts"]) != 4:
                print("!! %s has %d options: %s" % (r["id"], len(q["opts"]), q["q"][:40]))
            if not (0 <= q["answer"] < len(q["opts"])):
                print("!! %s answer out of range" % r["id"])


main()
