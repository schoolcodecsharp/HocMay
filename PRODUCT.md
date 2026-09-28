# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python, FastAPI, Jinja2, HTML, CSS và JavaScript thuần theo yêu cầu đề bài.

## Users

Hai sinh viên môn Học máy cơ bản dùng ứng dụng để thực hiện, giải thích và demo project cuối học phần. Người xem thứ hai là giảng viên cần kiểm tra quy trình dữ liệu, chống leakage, kết quả mô hình và giới hạn sử dụng.

## Product Purpose

Minh họa bằng dữ liệu thực tế mức độ Linear Regression và Gradient Descent giải thích biến thiên của giá trị nhà trung vị giữa các census block group trong California Housing. Thành công nghĩa là toàn bộ quy trình có thể chạy lại, các metric xuất phát từ code, và người xem không nhầm kết quả với giá nhà hiện tại hoặc giá của một căn nhà cụ thể.

## Positioning

Ứng dụng kết nối trực tiếp quy trình học máy có thể tái lập với ba bề mặt phục vụ học tập: phạm vi nghiên cứu, form ước lượng có kiểm tra nghiêm ngặt, và dashboard đọc artifact đánh giá thật.

## Operating Context

Project chạy local trong sáu tuần, được dùng khi phát triển, viết báo cáo và demo trực tiếp. Training chạy offline; web/API chỉ load pipeline đã lưu. Dữ liệu được tải lại bằng scikit-learn thay vì commit bản dữ liệu lớn vào Git.

## Capabilities and Constraints

- Dataset bắt buộc: `fetch_california_housing(as_frame=True)` với 20.640 mẫu, tám feature và target `MedHouseVal`.
- Dữ liệu lịch sử khoảng năm 1990; mỗi dòng là một census block group.
- Target có đơn vị 100.000 USD và bị chặn trên quanh 5,0.
- Split train, validation và test diễn ra trước mọi bước học từ dữ liệu.
- Validation dùng để chọn model; test chỉ dùng cho đánh giá cuối sau khi quyết định được đóng băng.
- Model bắt buộc gồm Mean Baseline, Linear Regression và SGDRegressor với ít nhất ba learning rate.
- Metric bắt buộc: MAE, RMSE và R²; residual được định nghĩa là `y_true - y_pred`.
- Website có ít nhất ba màn hình và endpoint `POST /api/estimate`.
- Không train hoặc fit preprocessing trong request web.
- Không tuyên bố quan hệ nhân quả từ coefficient.

## Brand Commitments

Tên sản phẩm là “California Housing Lab”. Giọng văn tiếng Việt rõ ràng, học thuật, trực tiếp và dễ trình bày với giảng viên.

## Evidence on Hand

- Đề bài chính thức: `Project_10_gia_tri_nha_california.docx`.
- Dataset đã tải và metadata tại `data/raw/`.
- Không có logo, ảnh thương hiệu, testimonial hoặc benchmark ngoài kết quả project; không được bịa thêm.

## Product Principles

- Kết quả thật, truy nguyên được đến artifact.
- Ranh giới train, validation và test phải nhìn thấy và giải thích được.
- Cảnh báo phạm vi sử dụng luôn gần prediction.
- Giao diện phục vụ việc học và demo, không giả dạng sản phẩm định giá thương mại.
- Mã nguồn đơn giản, tách trách nhiệm và có thể chạy từ máy mới.

## Accessibility & Inclusion

Giao diện phải dùng được bằng bàn phím, có focus rõ ràng, label đầy đủ, tương phản dễ đọc và không chỉ dựa vào màu sắc để truyền đạt trạng thái.
