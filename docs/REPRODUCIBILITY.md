# Tái lập và nghiệm thu

CPython 3.14.7, scikit-learn 1.9.1, numpy 2.5.3, pandas 3.0.6; đầy đủ ở `requirements-lock.txt`. Seed 42, split hai bước `src/split.py`. Windows x64 đã kiểm thử; chưa cam kết bitwise-equivalence mọi hệ điều hành/CPU.

Theo README tạo venv sạch, cài lock, tải dataset, nhập cadata. Train dựng candidate train/validation theo cấu hình cố định; artifact serving đã commit. `src.evaluate` xác minh checksum và đọc kết quả cũ, không tự chạy test khi train/khởi động web.

`python -m src.evaluate --reproduce` đối chiếu cấu hình chốt trên test **đã xem**, không phải test độc lập mới. Sau đó `python -m src.experiments` tái tạo figures. Receipt tránh đánh giá lặp. Candidate joblib không commit, tái tạo từ train/val. Archive chỉ để truy vết, không chạy script cũ để tuning.

## Tiêu chí

- `python -m pip check`: dependency hợp lệ.
- `python -m pytest -q`: API, model, split, scaler, nguồn/CSDL.
- Import20640dòng, max difference0, SQLite integrity ok.
- Health200, valid request200, invalid422, artifact thiếu/hỏng503.
- Data train-only, phân trang20, form ẩn prediction cũ khi input đổi.
- EDA train-only. Kiểm schema/kích thước nguồn được phép toàn dữ liệu.

## Kết quả kiểm chứng ngày 29/09/2026

Đã tạo venv mới, cài toàn bộ lock và chạy `pip check` thành công. Bộ kiểm thử đạt **41 passed**, không skip. Một cảnh báo deprecation của Starlette/httpx không làm test thất bại.

Bản sao project không có candidate joblib đã tái tạo candidate bằng train/validation, cho metric validation trùng lần đầu. Nhập CSDL vào file mới được 20.640 dòng, sai khác lớn nhất bằng 0. Lần kiểm chứng này dùng lại cache dataset chính thức đã tải, không được mô tả là kiểm thử tải lại qua mạng.

Notebook đã chạy toàn bộ code cell ở chế độ headless. Chrome đã kiểm prediction hợp lệ, lỗi input rỗng, ẩn kết quả cũ khi input thay đổi, menu ở viewport 390 × 844 và phân trang CSDL từ 1–20 sang 21–40. Dashboard tải đủ 11 ảnh, không tràn ngang toàn trang. Chưa kiểm trên thiết bị điện thoại vật lý. Receipt: `reports/results/verification.json`.

## Phạm vi phục vụ và lịch sử

Serving dùng candidate Linear Regression train-only đã chọn từ validation, không refit. Bản cũ refit train + validation được lưu riêng để truy vết; xem `pipeline_audit.json`. Metric test của serving ánh xạ tới metric LR train-only đã công bố ở lần chạy đầu. Không dùng kết quả test để đổi model/hyperparameter.

Báo cáo và slide do nhóm tự làm. `reports/results` và `reports/figures` chứa kết quả máy đọc và hình cho dashboard, vẫn thuộc mã nguồn ứng dụng.

Không đánh đồng pytest thành browser test, XML check thành render Word, hay PDF dựng riêng thành xác minh phân trang DOCX. Receipt ghi đúng phạm vi kiểm tra.
