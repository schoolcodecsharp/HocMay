# California Housing Dataset

## Nguồn dữ liệu

- Tên: California Housing.
- Nguồn tải: `sklearn.datasets.fetch_california_housing`.
- Tài liệu chính thức: <https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_california_housing.html>
- Mô tả nguồn StatLib: <https://www.dcc.fc.up.pt/~ltorgo/Regression/cal_housing.html>
- Ngày truy xuất của bản hiện tại: xem `data/raw/california_housing_metadata.json`.
- Phương thức: `fetch_california_housing(as_frame=True)`.
- Phiên bản thư viện và SHA-256 của CSV: xem file metadata được script sinh tự động.

Dataset được scikit-learn dẫn nguồn từ StatLib. Khi sử dụng cần ghi nguồn scikit-learn và nguồn gốc StatLib/Pace & Barry theo tài liệu dataset. Project không tái phân phối dataset qua Git; người dùng tự tải từ nguồn bằng script.

## Phạm vi

Đây là dữ liệu lịch sử dựa trên điều tra dân số California khoảng năm 1990. Một dòng là một census block group, không phải một căn nhà. Target `MedHouseVal` có đơn vị 100.000 USD và bị chặn trên gần 5,0.

Không được diễn giải prediction là giá thị trường hiện tại, giá chính xác của một căn nhà hoặc định giá tài sản dùng trong giao dịch.

## Cách tải lại

```powershell
.\.venv\Scripts\python.exe -m src.data
```

Script kiểm tra schema, kích thước 20.640 × 9, lưu CSV, metadata và checksum. `data/raw/` nằm trong `.gitignore` để tránh commit dữ liệu được tái tạo.

## CSDL từ cadata.txt

`python -m src.database` đọc `houses/cadata.txt`, tìm dòng đầu có chín số để bỏ header. Cột gốc: median_value_usd, median_income, housing_age, total_rooms, total_bedrooms, population, households, latitude, longitude. Dữ liệu giá trị là USD, không tự lấy log theo mô tả nghiên cứu trong header.

Schema `data/schema.sql` gồm `block_groups`, `source_metadata`, `split_membership`, view `housing_features`. AveRooms=total_rooms/households, AveBedrms=total_bedrooms/households, AveOccup=population/households, target=median_value_usd/100000. `row_id` là vị trí dòng 0-based, không phải mã địa lý chính thức. Import cùng checksum không tạo trùng; nguồn khác không tự ghi đè CSDL.

Kiểm chứng ngày 29/09/2026: 20640 dòng, sai khác lớn nhất 0 với sklearn sau quy đổi. SHA-256 cadata: `5e407d03adc03eb6aa34360c2976ee534d8309287dd49e3c22688630bddc9271`. Receipt `reports/results/database_manifest.json`. API dữ liệu chỉ đọc train, phân trang, SQL tham số.

## Quyền sử dụng

Header nguồn chưa có tuyên bố giấy phép rõ ràng. Giấy phép mã nguồn scikit-learn không tự động áp dụng cho dataset. Repo không tái phân phối cadata/cache/SQLite/raw CSV. Nhóm cần xác nhận điều khoản trước khi tái phân phối hoặc dùng ngoài học tập; ghi nguồn không thay thế quyền sử dụng. Nguồn gốc: Pace, R. Kelley và Ronald Barry (1997), *Sparse Spatial Autoregressions*, Statistics & Probability Letters, 33, 291–297.
