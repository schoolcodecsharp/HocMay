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
