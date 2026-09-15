# Mini annotation guideline — Ngày 3 (tracking)

Tên theo repository: `NguyenTriTin — 2A202602275`; nhóm: NR.
Clip: `clip_01`, `clip_02`.

Bản hoàn thiện tài liệu ngày 2026-09-15. Tệp trước audit còn là template; không có nhật ký ca mơ hồ trong lúc gán. NR = không được ghi nhận trong bằng chứng hiện có. Các ca mục 4 là **đối chiếu hồi cứu**, không phải quyết định cá nhân hoặc finding peer review được tái dựng.

## 1. Phạm vi: gán cái gì, không gán cái gì

Một lớp duy nhất: **`vehicle`** — xe bốn bánh.

| Gán | Không gán |
| --- | --- |
| Xe con, SUV, taxi, xe bán tải, van, minivan | Người đi bộ, xe đạp, xe máy / mô tô |
| Xe buýt, minibus, xe tải, xe đầu kéo | Xe trong ảnh quảng cáo, gương hoặc phản chiếu |

Bổ sung riêng của nhóm trong lúc gán: NR. Áp dụng phạm vi mặc định của GUIDE.

## 2. Luật ID — phần quan trọng nhất

| Tình huống | Luật của nhóm | Vì sao |
| --- | --- | --- |
| Xe bị che rồi hiện lại sau dưới 25 frame | Giữ ID cũ theo luật lab | Che tạm thời không tạo xe mới |
| Xe bị che hơn 25 frame | Mở track mới theo GUIDE; đúng 25 frame cần ghi ca và nhờ Lab Coach làm rõ | GUIDE nêu dưới/quá 2 giây; không tự đặt ngưỡng khác |
| Xe rời khung hình rồi quay lại | Track mới | Ra khỏi ảnh kết thúc track theo lab |
| Hai xe cắt nhau / chồng lên nhau | Theo từng xe qua các frame, giữ ID riêng | Identity gắn với xe qua thời gian |

Đây là luật mặc định và hướng dẫn áp dụng; luật riêng nhóm đã dùng trước lock: NR. Khi so các MOT, dùng ghép bbox và continuity; không yêu cầu ID số học bằng nhau.

## 3. Luật bbox

| Tình huống | Luật của nhóm |
| --- | --- |
| Xe bị cắt bởi rìa ảnh | Bbox chạm đúng rìa, không đoán phần ngoài ảnh |
| Xe bị xe khác che một phần | Bbox ôm phần nhìn thấy được |
| Xe vừa xuất hiện, còn rất nhỏ / rất mờ | Bắt đầu ở frame đầu tiên xác định chắc là xe bốn bánh; không đặt thêm ngưỡng pixel |
| Xe đang đỗ, không di chuyển | Vẫn gán khi xe hiện diện; bbox đứng im chỉ là cảnh báo cần kiểm tra |
| Keyframe đặt dày ở đâu | Khi scale, hướng, phần nhìn thấy hoặc occlusion thay đổi; luôn kiểm tra midpoint giữa hai keyframe xa nhau |
| Biên track | Kiểm tra frame đầu/cuối và frame đầu sau occlusion; Outside đúng lúc xe rời khung |

## 4. Ít nhất ba ca mơ hồ đã gặp thật

**Nhật ký trong lúc gán: NR.** Ba ca dưới đây tồn tại trong artifact và được kiểm tra hồi cứu khi lập báo cáo; không xác nhận người gán đã xử lý chúng lúc làm bài. Nguồn: `reports/report_evidence.json` và các JSON evaluator.

### Ca 1

- Clip / frame / ID: `clip_01`, 93–94, annotation 5 ↔ gold 5.
- Tình huống: bbox pre-gold không khớp; IoU 0.403 và 0.409.
- Quyết định: MOT cuối đã đổi bbox, IoU thành 0.504 và 0.511; thao tác người gán: NR.
- Lý do: vượt ngưỡng evaluator nhưng còn bbox trôi; cần kiểm tra nội suy và phần nhìn thấy, không coi vừa qua ngưỡng là bbox hoàn hảo.

### Ca 2

- Clip / frame / ID: `clip_01`, 110–112, gold 6 ↔ annotation 7; treatment candidate 31.
- Tình huống: annotation khớp liên tục (IoU 0.725, 0.801, 0.818), model chưa khớp (0.395, 0.427, 0.464).
- Quyết định: gold ủng hộ annotation trong cửa sổ này; không sửa nhãn theo model.
- Lý do: model không phải đáp án; cần ghép theo thời gian, không so ID nguyên giữa các file.

### Ca 3

- Clip / frame / ID: `clip_01`, 167–170, gold 8 ↔ annotation 8 ↔ treatment 34.
- Tình huống: tại 168, IoU annotation 0.493, treatment 0.676; gold kết thúc ở 168 nhưng cả annotation và treatment còn bbox đến 170, không khớp gold tại 169–170.
- Quyết định: đề xuất xem lại hình học ở 168 và biên kết thúc ở 169–170; chưa sửa nhãn trong lần lập báo cáo.
- Lý do: cần kiểm tra hình ảnh theo luật phần nhìn thấy/Outside rồi sửa trong CVAT và export lại, không sửa trực tiếp MOT.

## 5. Sửa gì sau khi chấm với gold và sau khi kiểm chéo

- Làm rõ nội suy: tăng mật độ keyframe khi chuyển động/visibility thay đổi, kiểm tra midpoint và biên track. Đây là đề xuất dựa trên sai khác track 5 và 8.
- Ghi ca ngay lúc gặp với frame, ID, rule, quyết định và lý do; lưu riêng reviewer, thời điểm và closure. Finding kiểm chéo hiện tại: NR.
- Giữ luật occlusion dưới 25 frame, rời ảnh mở track mới và bắt đầu khi nhận diện chắc xe bốn bánh. Không đổi reference hoặc snapshot đã khóa.
