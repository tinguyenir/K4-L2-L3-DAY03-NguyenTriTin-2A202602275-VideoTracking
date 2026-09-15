# Báo cáo Ngày 3 — Tracking Annotation

**Họ tên:** Nguyen Tri Tin
**MSSV:** 2A202602275
**Hình thức thực hiện:** Cá nhân (solo)
**Ngày:** 15/09/2026

> Báo cáo được tổng hợp từ annotation MOT 1.1, pre-gold snapshot, kết quả
> validator/evaluator và model outputs trong repository cá nhân.
> Các thông tin không được lưu trong artifact được ký hiệu **NR (Not Recorded)**
> thay vì suy đoán.

---

## Tóm tắt kết quả

Bài thực hành xây dựng và đánh giá annotation cho bài toán multi-object tracking
trên hai video `clip_02` và `clip_01`, sau đó so sánh hai pipeline tracking sử dụng
cùng detector input: **YOLO26 + ByteTrack** và **YOLO26 + BoT-SORT + ReID**.

Annotation cuối của `clip_01` gồm **576 bbox và 8 track trên 190 frame**. Khi so
với teaching reference, bản cuối đạt:

- **HOTA:** 0.708
- **IDF1:** 0.978
- **MOTA:** 0.956
- **MOTP:** 0.730
- **FP/FN/IDSW:** 14 / 11 / 0

Kết quả vượt toàn bộ cổng chất lượng của bài. So với snapshot pre-gold, FP và FN
cùng giảm 12, IDF1 tăng khoảng 0.021 và MOTA tăng khoảng 0.042. Tuy nhiên một số
sai khác localization vẫn tồn tại, chủ yếu ở track 5 và boundary của track 8.

Ở phần model, **BoT-SORT + ReID treatment đạt chất lượng tổng thể cao hơn
ByteTrack control trên clip này**, đặc biệt DetA, AssA, HOTA và IDF1 đều tăng,
trong khi FN giảm từ 54 xuống 26. Tuy vậy FP tăng nhẹ và cả hai tracker vẫn có
2 ID switch. Đây là **system-level comparison**, không phải ablation cô lập causal
effect của riêng ReID.

---

## 1. Quá trình gán nhãn

| Mục | Giá trị |
| --- | --- |
| Công cụ | CVAT — Rectangle Track Mode; export MOT 1.1 |
| Thời gian gán `clip_02` | NR — không có nhật ký thời lượng |
| Thời gian gán `clip_01` | NR — không có nhật ký thời lượng |
| Số track trong `clip_01` | 8 |
| Số bbox trong `clip_01` | 576 |
| Số frame `clip_01` | 190 |
| Số keyframe trung bình mỗi track | NR — MOT 1.1 không lưu metadata keyframe của CVAT |

`clip_02` có **239 bbox và 7 ID trên 60 frame**. Kết quả warm-up so với reference
đạt `IDF1 = 0.974`, `MOTA = 0.947`, `MOTP = 0.812`, `FP = 12`, `FN = 0`,
`IDSW = 0`. Reference có 6 track; vì vậy số ID trong MOT không được diễn giải
trực tiếp thành số vehicle hợp lệ.

### Ba vấn đề kỹ thuật nổi bật

Do không có nhật ký chủ quan về mức độ khó trong lúc annotation, ba trường hợp
dưới đây được xác định **hồi cứu từ artifact**.

1. **Bbox drift ở track 5.**
   So sánh pre-gold và final MOT cho thấy 13 bbox được thay đổi. Trong số đó,
   12 bbox chuyển từ trạng thái không đạt IoU 0.5 sang đạt ngưỡng matching.
   Điều này cho thấy interpolation giữa các keyframe có thể gây drift khi motion,
   scale hoặc visibility thay đổi.

2. **Track boundary ở ID 8.**
   Annotation ID 8 còn tồn tại tới frame 170 trong khi gold track tương ứng kết
   thúc ở frame 168. Đây là trường hợp cần kiểm tra chặt thời điểm đặt `Outside`
   và frame đầu tiên vehicle thực sự rời scene.

3. **Identity và coverage trong vùng occlusion/mất dấu.**
   Ở vùng frame 108–112, annotation vẫn giữ được correspondence ổn định với gold
   trong khi treatment chưa match được đầy đủ ngay từ đầu cửa sổ. Trường hợp này
   nhấn mạnh rằng identity phải được đánh giá theo trajectory và temporal
   continuity, không theo một frame đơn.

---

## 2. Tự kiểm và kiểm chéo

Bài được thực hiện **cá nhân**, do đó không có partner để thực hiện peer review
hai chiều. Phần kiểm tra chất lượng được thực hiện dưới dạng **self-review kết hợp
validator/evaluator**.

### Self-QC

**Lượt 1 — Identity / timeline**

Mục tiêu là kiểm tra `track_id`, fragmentation và ID switch tại các vùng crossing
hoặc occlusion. Bản annotation cuối đạt **IDSW = 0** khi so với teaching reference,
không có ID switch được evaluator ghi nhận.

**Lượt 2 — Entry / exit / track boundary**

Mục tiêu là kiểm tra frame đầu, frame cuối và `Outside`. Audit hồi cứu phát hiện
boundary case của annotation ID 8 quanh frame 168–170, cho thấy bước kiểm tra
endpoint cần được thực hiện chặt hơn.

**Lượt 3 — Geometry / interpolation**

Mục tiêu là kiểm tra midpoint giữa các keyframe xa nhau. Diagnostics cuối vẫn
ghi nhận các bbox gần ngưỡng ở track 5, nổi bật tại frame 84, 89, 93, 94, 99,
105 và 109.

### Kiểm chéo

- **Peer reviewer:** Không áp dụng — bài thực hiện cá nhân.
- **Finding từ partner:** Không áp dụng.
- **Finding trên bài của partner:** Không áp dụng.
- **Bất đồng giữa hai annotator:** Không áp dụng.

`reports/review_partner.md` được sử dụng như **self-review record** thay vì tạo
một reviewer không tồn tại. Diagnostic từ evaluator/model không được trình bày
như peer-review finding.

Validator `tools/check_mot_labels.py` không phát hiện lỗi định dạng trong hai
file MOT. Các warning của validator chỉ được coi là tín hiệu cần kiểm tra thêm,
không tự động được coi là lỗi annotation.

---

## 3. Pre-gold lock và chấm trước/sau rework

### Pre-gold evidence

| Evidence | Giá trị |
| --- | --- |
| SHA-256 | `8473600f9d19e92dab3624f4c4a3f675b64c6da65beeef18a37ee7f226841831` |
| Thời điểm khóa | `2026-09-15T09:28:13.316436+00:00` UTC |
| Số row | 576 |
| Số frame | 190 |
| Số track | 8 |
| Track ID | 1–8 |

Snapshot và manifest được giữ nguyên sau khi khóa.

### Kết quả trước và sau rework

| | HOTA | DetA | AssA | LocA | IDF1 | MOTA | MOTP | FP | FN | IDSW |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pre-gold | 0.704 | 0.665 | 0.763 | 0.784 | 0.957 | 0.915 | 0.734 | 26 | 23 | 0 |
| Sau rework | 0.708 | 0.669 | 0.765 | 0.784 | 0.978 | 0.956 | 0.730 | 14 | 11 | 0 |
| Δ sau − trước | +0.004 | +0.004 | +0.003 | +0.001* | +0.021 | +0.042* | −0.004 | −12 | −12 | 0 |

> `*` Δ được tính từ giá trị số trong JSON trước khi hiển thị làm tròn 3 chữ số,
> nên có thể lệch 0.001 so với phép trừ trực tiếp hai ô đã làm tròn.

Cổng yêu cầu:

- `IDF1 >= 0.80`
- `MOTA >= 0.75`
- `MOTP >= 0.70`

**Kết quả cuối: ĐẠT**, với `IDF1 = 0.978`, `MOTA = 0.956`,
`MOTP = 0.730`.

### Các thay đổi quan sát được

| Loại lỗi | Frame | ID | Thay đổi |
| --- | --- | --- | --- |
| Bbox chưa khớp gold | 79, 80, 83 | annotation 5 ↔ gold 5 | Điều chỉnh geometry; frame 80 tăng IoU 0.494 → 0.590, frame 83 tăng 0.480 → 0.579 |
| Bbox drift | 90–94, 97–98 | annotation 5 ↔ gold 5 | 7 bbox chuyển qua ngưỡng IoU 0.5; frame 93: 0.403 → 0.504, frame 94: 0.409 → 0.511 |
| Bbox chưa khớp gold | 106–108 | annotation 5 ↔ gold 5 | IoU tăng 0.487 → 0.584, 0.435 → 0.537, 0.471 → 0.572 |

Tổng cộng **13 dòng bbox được thay đổi**, không thêm/bớt detection, không đổi ID
và không thay đổi lifespan của track. Số true positive ở ngưỡng IoU 0.5 tăng
từ 550 lên 562; FP và FN cùng giảm 12.

Coverage của gold track 5 tăng từ **47/60 lên 59/60 frame**.

Rework cải thiện rõ matching và identity agreement, nhưng không loại bỏ hoàn toàn
localization discrepancy. Một số bbox track 5 vẫn nằm sát ngưỡng IoU 0.5.
MOTP giảm nhẹ 0.004, vì vậy không nên diễn giải rằng mọi bbox đều được cải thiện.

---

## 4. Kết quả model: ByteTrack control vs ReID treatment

### Cấu hình thực nghiệm

| Mục | Giá trị |
| --- | --- |
| Python | 3.13.15 |
| ultralytics | 8.4.145 |
| torch | 2.11.0+cu128 |
| lap | 0.5.13 |
| Detector weights | `yolo26n.pt` |
| Control tracker | `bytetrack.yaml` |
| Treatment tracker | `configs/trackers/botsort-reid.yaml` |
| Confidence threshold | 0.250 |
| IoU threshold | 0.700 |
| Image size | 960 |
| COCO classes | `[2, 5, 7]` = car, bus, truck |
| Device | CUDA device `0` |
| Persist tracker state | `true` |
| Số frame | 190 |

Hai pipeline sử dụng cùng detector configuration, thứ tự frame, image size,
confidence threshold, IoU threshold và COCO classes.

Control sinh **607 bbox / 16 model IDs**.
Treatment sinh **638 bbox / 16 model IDs**.

Số model ID không tương đương số vehicle thực tế vì fragmentation hoặc false
positive có thể tạo thêm ID.

### Kết quả định lượng

| So sánh | HOTA | DetA | AssA | LocA | IDF1 | MOTA | MOTP | FP | FN | IDSW |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Annotation vs gold | 0.708 | 0.669 | 0.765 | 0.784 | 0.978 | 0.956 | 0.730 | 14 | 11 | 0 |
| ByteTrack control vs gold | 0.709 | 0.649 | 0.776 | 0.846 | 0.875 | 0.749 | 0.823 | 88 | 54 | 2 |
| BoT-SORT + ReID vs gold | 0.764 | 0.711 | 0.820 | 0.872 | 0.900 | 0.792 | 0.860 | 91 | 26 | 2 |
| ReID treatment vs annotation | 0.657 | 0.583 | 0.756 | 0.793 | 0.880 | 0.750 | 0.744 | 102 | 40 | 2 |
| Δ treatment − control | +0.055 | +0.062 | +0.044 | +0.026 | +0.026 | +0.044 | +0.037 | +3 | −28 | 0 |

Treatment đạt kết quả cao hơn control ở HOTA, DetA, AssA, LocA, IDF1, MOTA và
MOTP. Cải thiện đáng chú ý nhất là **FN giảm từ 54 xuống 26**, trong khi FP tăng
nhẹ từ 88 lên 91. IDSW giữ nguyên ở 2.

Kết quả cho thấy **BoT-SORT + ReID treatment tốt hơn ByteTrack control ở cấp
hệ thống trên clip này**. Tuy nhiên thí nghiệm không cô lập tác động của riêng
ReID, vì ByteTrack và BoT-SORT khác cả implementation và association logic ngoài
appearance cue.

---

## 5. Phân tích — năm câu hỏi

### 1. MOTA của bạn cao hơn hay thấp hơn IDF1? Nếu MOTA cao mà IDF1 thấp thì điều đó nói gì?

Bản annotation cuối có:

- `MOTA = 0.956`
- `IDF1 = 0.978`

Do đó MOTA **thấp hơn IDF1 khoảng 0.022**. Kết quả hiện tại không thuộc trường
hợp “MOTA cao nhưng IDF1 thấp”.

MOTA chủ yếu phạt FP, FN và mỗi ID switch như một sự kiện. Ngược lại, IDF1 đánh
giá sự nhất quán identity trên toàn bộ trajectory. Vì vậy một track bị gán sai
identity trong một đoạn dài có thể làm giảm IDF1 đáng kể nhưng chỉ tạo một số ít
IDSW trong MOTA.

Trong bản cuối, `IDSW = 0`, nên không có evidence về identity switching nghiêm
trọng của annotation.

---

### 2. ByteTrack và BoT-SORT + ReID khác nhau thế nào về IDF1, AssA và IDSW?

Control:

- `IDF1 = 0.875`
- `AssA = 0.776`
- `IDSW = 2`

Treatment:

- `IDF1 = 0.900`
- `AssA = 0.820`
- `IDSW = 2`

Treatment tăng IDF1 khoảng **0.026** và AssA **0.044**, nhưng không làm giảm số
ID switch.

Diagnostics ghi nhận:

| Hệ thống | Frame | Gold track | Model ID |
| --- | ---: | ---: | --- |
| ByteTrack | 59 | 4 | 14 → 15 |
| ByteTrack | 94 | 5 | 23 → 32 |
| Treatment | 87 | 5 | 17 → 18 |
| Treatment | 113 | 6 | 24 → 31 |

Một sequence minh họa rõ lợi thế coverage là **frame 108–112, gold track 7**:

| Frame | ByteTrack | Treatment | Annotation |
| ---: | --- | --- | --- |
| 108 | Không match | ID 29, IoU 0.497 — chưa match | ID 6, IoU 0.722 |
| 109 | Không match | ID 29, IoU 0.532 | ID 6, IoU 0.727 |
| 110 | Không match | ID 29, IoU 0.576 | ID 6, IoU 0.769 |
| 111 | Không match | ID 29, IoU 0.735 | ID 6, IoU 0.727 |
| 112 | ID 52, IoU 0.822 | ID 29, IoU 0.840 | ID 6, IoU 0.728 |

Treatment match **4/5 frame**, trong khi control chỉ match **1/5 frame**.
Sequence này giải thích một phần việc FN của treatment thấp hơn.

Tuy nhiên đây chủ yếu là evidence về **coverage**, không chứng minh treatment đã
loại bỏ ID switch. IDF1 và AssA toàn clip tăng nhưng IDSW vẫn bằng 2.

---

### 3. DetA, FP và FN thay đổi thế nào? Lỗi còn lại thuộc detector hay association?

Từ control sang treatment:

- DetA: `0.649 → 0.711`
- FP: `88 → 91`
- FN: `54 → 26`
- AssA: `0.776 → 0.820`
- IDSW: `2 → 2`

FN giảm 28 cho thấy treatment giữ được nhiều valid detection/trajectory segment
hơn. Tuy vậy FP vẫn cao và tăng nhẹ 3.

AssA tăng cho thấy association ở cấp hệ thống cũng tốt hơn, nhưng IDSW vẫn còn
2 và diagnostics vẫn xuất hiện fragmented tracks.

Vì vậy lỗi còn lại là sự kết hợp của:

1. **detection/coverage error**;
2. **localization error**;
3. **association/fragmentation error**.

Không có raw detector-only output độc lập nên không thể quy từng FN cụ thể cho
YOLO detector hay tracker association.

---

### 4. Một chỗ annotation đúng và ReID treatment sai

Chọn **frame 110–112**, gold track 6 ↔ annotation ID 7 ↔ treatment candidate ID 31.

| Frame | Annotation ID 7 / IoU | Treatment ID 31 / IoU | Kết luận |
| ---: | ---: | ---: | --- |
| 110 | 0.725 | 0.395 | Annotation match; treatment không match |
| 111 | 0.801 | 0.427 | Annotation match; treatment không match |
| 112 | 0.818 | 0.464 | Annotation match; treatment không match |

Annotation ID 7 còn match gold tại frame 108–109 với IoU lần lượt khoảng
0.642 và 0.574. Treatment ID 31 chỉ bắt đầu đạt ngưỡng với gold track này ở
frame 113.

Teaching reference vì vậy ủng hộ annotation về coverage và continuity trong
cửa sổ 110–112. Trường hợp này minh họa rõ rằng model output không được dùng
trực tiếp làm ground truth.

---

### 5. Một chỗ ReID treatment làm tôi xem lại annotation

Vùng **frame 167–170**, gold track 8 ↔ annotation ID 8 ↔ treatment ID 34.

| Frame | Annotation / IoU | Treatment / IoU | Kết quả |
| ---: | ---: | ---: | --- |
| 167 | ID 8 / 0.585 | ID 34 / 0.773 | Cả hai match |
| 168 | ID 8 / 0.493 | ID 34 / 0.676 | Chỉ treatment match |

Tại frame 168, treatment định vị tốt hơn annotation theo IoU với gold.
Teaching reference kết thúc track tại frame 168, trong khi cả annotation ID 8
và treatment ID 34 vẫn còn bbox tại frame 169–170.

Do đó vùng này cần được xem lại ở hai khía cạnh:

- **geometry tại frame 168**;
- **thời điểm kết thúc track / Outside tại frame 169–170**.

Treatment hữu ích trong việc chỉ ra vùng cần audit, nhưng không phải đáp án:
ở frame 169–170 cả annotation và treatment đều tồn tại bbox vượt quá boundary
của gold.

---

## 6. Nếu phải gán thêm 10 clip nữa

Từ các lỗi quan sát được, quy trình nên được cải thiện theo bốn điểm:

1. **Keyframe thích ứng theo chuyển động.**
   Tăng mật độ keyframe khi vehicle thay đổi scale, hướng, tốc độ, visibility
   hoặc bị occlusion; không sử dụng một khoảng frame cố định cho mọi track.

2. **Midpoint QC bắt buộc.**
   Mỗi khoảng keyframe dài cần kiểm tra ít nhất một frame ở giữa để phát hiện
   interpolation drift sớm.

3. **Boundary QC riêng.**
   Kiểm tra frame đầu, frame cuối, frame ngay sau occlusion và thời điểm `Outside`
   cho từng track.

4. **Ghi log ca mơ hồ tại thời điểm annotation.**
   Mỗi case nên lưu:
   `clip → frame → ID → rule → decision → reason → closure`.
   Đồng thời ghi thời lượng annotation và keyframe statistics nếu rubric yêu cầu.

Các luật identity cốt lõi vẫn giữ nguyên:

- occlusion dưới 25 frame: giữ ID cũ;
- vehicle đã rời hẳn khung rồi quay lại: track mới;
- vehicle nhỏ/mờ: bắt đầu từ frame đầu tiên có thể xác định hợp lý là xe bốn bánh;
- model chỉ dùng sau pre-gold lock để diagnostic;
- không sửa trực tiếp file MOT để cải thiện validator/metric.

---

## 7. Tệp đã nộp

### Artifact bắt buộc

- [x] `annotations/clip_01/gt.txt`
- [x] `annotations/clip_02/gt.txt`
- [x] `evidence/pre-gold/clip_01/gt.txt`
- [x] `evidence/pre-gold/clip_01/manifest.json`
- [x] `GUIDELINE_MINI.md`
- [x] `outputs/eval_pre_gold.json`
- [x] `outputs/eval_vs_gold.json`
- [x] `outputs/model_bytetrack_clip_01.txt`
- [x] `outputs/model_reid_clip_01.txt`
- [x] `outputs/model_run_config.json`
- [x] `outputs/eval_bytetrack_vs_gold.json`
- [x] `outputs/eval_reid_vs_gold.json`
- [x] `outputs/eval_reid_vs_me.json`
- [x] `reports/review_partner.md` — self-review record do bài thực hiện cá nhân
- [x] `reports/REPORT.md`

### Artifact hỗ trợ tái lập

- `outputs/eval_clip_02.json`
- `reports/report_evidence.json`
- `tools/audit_report_evidence.py`

### Không đưa vào submission

- teaching reference / gold của `clip_01`;
- `data/gold/`;
- model weights `*.pt`;
- ZIP/RAR trung gian;
- `outputs/vis_*`;
- temporary/stress experiment outputs không thuộc kết quả cuối.

`TEAM.md` **không áp dụng**, vì bài được thực hiện cá nhân.

---

## Kết luận

Annotation cuối đạt cổng chất lượng với **IDF1 0.978, MOTA 0.956 và MOTP 0.730**.
Rework chủ yếu cải thiện bbox matching của track 5, làm FP và FN cùng giảm 12,
nhưng vẫn còn một số localization và boundary discrepancies cần được lưu ý.

Trong thí nghiệm model, **BoT-SORT + ReID treatment đạt kết quả tổng thể tốt hơn
ByteTrack control trên `clip_01`**, với HOTA, DetA, AssA và IDF1 đều cao hơn và
FN giảm đáng kể. Tuy nhiên FP tăng nhẹ và IDSW không thay đổi. Vì hai tracker
khác implementation và association logic, kết quả chỉ được diễn giải ở cấp
hệ thống, không được dùng để khẳng định ReID riêng lẻ là nguyên nhân của toàn bộ
mức cải thiện.

Kết quả bài thực hành cho thấy ba yếu tố cần được kiểm soát đồng thời trong
tracking annotation: **detection coverage, localization accuracy và temporal
identity consistency**.
