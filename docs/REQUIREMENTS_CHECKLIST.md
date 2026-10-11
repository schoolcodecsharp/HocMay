# Đối chiếu đề gốc, không tự chấm điểm

Nguồn: `Project_10_gia_tri_nha_california.docx`. Điểm do giảng viên đánh giá.

| Hạng mục | Điểm | Minh chứng | Trạng thái / lưu ý |
|---|---:|---|---|
| Bài toán/phạm vi | 8 | README, báo cáo, giới thiệu | Block group lịch sử1990, giới hạn sử dụng |
| Dữ liệu/EDA | 12 | src.data/database/eda, notebook, dictionary | Đúng dataset, cadata khớp tuyệt đối; giấy phép tái phân phối cần xác nhận |
| Split/leakage/tái lập | 15 | split, features, frozen_manifest, lock | Candidate/serving hiện tại train-only. Artifact refit cũ lưu riêng và audit. Test đã quan sát, không tuyên bố hậu kiểm là đánh giá độc lập mới |
| Mô hình/thí nghiệm | 18 | train, experiments, loss80epoch, coefs | Mean, LR, SGD4learning rates, bốn phân tích |
| Đánh giá/lỗi | 18 | metrics, residual_groups, evaluate | Giữ kết quả gốc, hậu kiểm gắn nhãn, không chọn lại bằng test |
| Web/API | 12 | 5trang, OpenAPI, service, tests | Saved pipeline, strict JSON/domain, 422/503, cảnh báo |
| Code/bàn giao | 7 | README, lock, tests, docs | Xem REPRODUCIBILITY, Git không chứa raw |
| Báo cáo/trình bày/nhóm | 10 | Nhóm tự soạn báo cáo/slide theo yêu cầu mới | Có tên/MSSV; nhật ký và commit mỗi người cần xác nhận |
| Tổng | 100 | Không tự chấm | Không cam kết100/100 |

Đề có điều kiện giới hạn điểm khi không tái lập được, không có test độc lập hoặc leakage nghiêm trọng. Ngoại lệ cần trình bày với giảng viên. Sửa tài liệu không làm test đã xem trở thành chưa xem. Spatial split/mô hình phi tuyến là hướng tương lai, không tiếp tục tuning trên test hiện tại.
