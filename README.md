# California Housing Lab

Project cuối học phần Học máy cơ bản nghiên cứu câu hỏi: Linear Regression và Gradient Descent giải thích được bao nhiêu biến thiên của giá trị nhà trung vị giữa các census block group trong dữ liệu California khoảng năm 1990?

Ứng dụng không định giá một căn nhà cụ thể và không phản ánh thị trường bất động sản hiện tại.

## Dataset

Project sử dụng duy nhất `fetch_california_housing(as_frame=True)` với 20.640 mẫu, tám feature và target `MedHouseVal`. Target có đơn vị 100.000 USD và bị chặn trên gần 5,0. Xem `data/README.md` và `data/data_dictionary.md`.

## Cài đặt

Yêu cầu Python 3.11 trở lên.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Tải dữ liệu

```powershell
.\.venv\Scripts\python.exe -m src.data
```

CSV và metadata được tạo trong `data/raw/`. Thư mục này không được commit vào Git.

## Train và evaluate

```powershell
.\.venv\Scripts\python.exe -m src.train
.\.venv\Scripts\python.exe -m src.evaluate
```

Quy trình:

1. Split 70% train, 15% validation, 15% test với `random_state=42` trước preprocessing.
2. Fit scaler/model trên train.
3. So sánh Mean Baseline, Linear Regression và SGDRegressor trên validation.
4. SGD thử bốn learning rate và ghi loss theo 80 epoch.
5. Chọn model bằng validation RMSE và ghi quyết định vào `model_selection.json`.
6. Refit model đã chọn trên train + validation.
7. Dùng test ở block đánh giá cuối và lưu artifact/figures thật.

Model được lưu tại `models/final_pipeline.joblib`. Web chỉ load model này; không train trong request.

## Chạy web và API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Mở <http://127.0.0.1:8000>. Các route:

- `/`: giới thiệu và phạm vi.
- `/estimate`: form tám feature.
- `/dashboard`: metric và biểu đồ thực tế.
- `/model-card`: intended use, prohibited use và limitation.
- `/docs`: tài liệu OpenAPI tự động.

### POST /api/estimate

Ví dụ request:

```json
{
  "MedInc": 3.5,
  "HouseAge": 28,
  "AveRooms": 5.4,
  "AveBedrms": 1.1,
  "Population": 1400,
  "AveOccup": 3.0,
  "Latitude": 34.1,
  "Longitude": -118.2
}
```

Ví dụ cấu trúc response:

```json
{
  "prediction": 2.1,
  "unit": "100,000 USD",
  "estimated_usd": 210000,
  "model": "linear_regression",
  "warning": "Đây là ước lượng cho một census block group dựa trên dữ liệu lịch sử..."
}
```

Con số trên chỉ minh họa cấu trúc response trong tài liệu. Kết quả thật phụ thuộc input và saved pipeline.

## Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Test bao phủ request hợp lệ, thiếu field, sai type, NaN, ngoài domain, thiếu model artifact, prediction và các trang web.

## Kết quả và tái lập

- Config: `config/project_config.json`.
- Metrics: `reports/results/metrics.json`.
- Loss history: `reports/results/sgd_history.json`.
- Model selection: `reports/results/model_selection.json`.
- Figures: `reports/figures/`.
- Phiên bản Python và thư viện: `reports/results/model_metadata.json`.

Không thay đổi model dựa trên final test. Nếu sửa pipeline/hyperparameter, phải chạy lại toàn bộ quy trình từ đầu và ghi rõ đây là một experiment mới.

## Giới hạn và đạo đức

- Dữ liệu khoảng năm 1990, không đại diện thị trường hiện tại.
- Một quan sát là census block group, không phải căn nhà.
- Target cap gần 5,0 làm biến dạng residual ở vùng giá cao.
- Quan hệ trong coefficient không chứng minh nhân quả.
- Địa lý có thể phản ánh bất bình đẳng lịch sử.
- Không dùng cho cho vay, tín dụng, thuế, giao dịch bất động sản, định giá tài sản thật hoặc quyết định ảnh hưởng trực tiếp tới con người.

## Thành viên nhóm

- Thành viên 1: bổ sung họ tên và mã sinh viên.
- Thành viên 2: bổ sung họ tên và mã sinh viên.

## Tài liệu tham khảo

- scikit-learn California Housing documentation.
- Pace, R. Kelley và Ronald Barry, *Sparse Spatial Autoregressions*, Statistics & Probability Letters, 1997.
