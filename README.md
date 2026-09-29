# California Housing Lab

Project cuối học phần Học máy cơ bản nghiên cứu câu hỏi: Linear Regression và Gradient Descent giải thích được bao nhiêu biến thiên của giá trị nhà trung vị giữa các census block group trong dữ liệu California khoảng năm 1990?

Ứng dụng không định giá một căn nhà cụ thể và không phản ánh thị trường bất động sản hiện tại.

## Dataset

Project sử dụng duy nhất `fetch_california_housing(as_frame=True)` với 20.640 mẫu, tám feature và target `MedHouseVal`. Target có đơn vị 100.000 USD và bị chặn trên gần 5,0. Xem `data/README.md` và `data/data_dictionary.md`.

## Cài đặt

Môi trường đã kiểm chứng: CPython 3.14.7, Windows x64. Dùng cùng phiên bản scikit-learn để nạp artifact. Không nạp joblib không rõ nguồn gốc.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

## Tải dữ liệu

```powershell
.\.venv\Scripts\python.exe -m src.data
```

CSV và metadata được tạo trong `data/raw/`. Thư mục này không được commit vào Git.

Đặt file đã có vào `houses/cadata.txt`, chạy `python -m src.database` trong venv để tạo `data/california_housing.sqlite3`. Đã kiểm chứng 20.640 dòng sau quy đổi khớp hoàn toàn với sklearn (max difference = 0). Schema: `data/schema.sql`. File raw và SQLite không đưa lên Git. Không cần CSDL để chạy dự đoán từ artifact.

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
6. Lưu đúng candidate train-only đã chọn, không refit scaler/model trên validation hoặc test.
7. `src.evaluate` mặc định chỉ đọc kết quả frozen, không đánh giá test lại. `--reproduce` là hậu kiểm có chỉ định, không phải test độc lập mới.

**Truy vết sửa lỗi:** artifact web cũ đã refit scaler trên train + validation. Web hiện dùng đúng candidate LR train-only đã được chọn bằng validation từ lần đầu; không đổi thuật toán/hyperparameter theo test. Metric phục vụ là metric cũ của candidate đó. `pipeline_audit.json` và `reports/archive/initial/` giữ lịch sử đầy đủ. Test đã được quan sát nên hậu kiểm không được gọi là test độc lập mới.

Chạy `python -m src.eda` để tái tạo EDA train-only. Chạy `python -m src.evaluate --reproduce` rồi `python -m src.experiments` để tái tạo residual/biểu đồ theo đúng cấu hình đã chốt, không tuning bằng test.

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
- `/data`: CSDL SQLite, chỉ xem train và có phân trang.
- `/api/data?offset=0&limit=20`: JSON train, tối đa 100 dòng/lần.
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

API chỉ nhận số hữu hạn, đủ tám trường, không trường thừa. Population nguyên, AveBedrms ≤ AveRooms, từng biến trong min/max train. Không clipping. HTTP 422 cho input sai, 503 khi artifact thiếu/hỏng. Khi sửa input, form ẩn kết quả cũ.

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

Không thay đổi model dựa trên final test. Test hiện tại đã quan sát; chạy lại hoặc đổi seed không biến nó thành test độc lập mới. Đọc `docs/REPRODUCIBILITY.md`.

## Giới hạn và đạo đức

- Dữ liệu khoảng năm 1990, không đại diện thị trường hiện tại.
- Một quan sát là census block group, không phải căn nhà.
- Target cap gần 5,0 làm biến dạng residual ở vùng giá cao.
- Quan hệ trong coefficient không chứng minh nhân quả.
- Địa lý có thể phản ánh bất bình đẳng lịch sử.
- Không dùng cho cho vay, tín dụng, thuế, giao dịch bất động sản, định giá tài sản thật hoặc quyết định ảnh hưởng trực tiếp tới con người.

## Thành viên nhóm

- Nguyễn Văn Trường — 10123341.
- Trần Bình Dương — 10123072.

## Thành phần kỹ thuật bàn giao

- `notebooks/eda.ipynb`: EDA train-only.
- `docs/DEMO_VA_VAN_DAP.md`: demo và câu hỏi bảo vệ.
- `docs/TEAM_PLAN.md`: kế hoạch sáu tuần, mẫu nhật ký thực tế.
- `docs/REQUIREMENTS_CHECKLIST.md`: đối chiếu rubric, không tự chấm điểm.

Ngày nộp, nhật ký sáu tuần thực tế và commit từng người cần nhóm xác nhận. Không tạo giả tác giả/ngày commit. Giấy phép tái phân phối dataset cần kiểm chứng, xem `data/README.md`.

Báo cáo và slide do nhóm tự soạn theo yêu cầu mới. Thư mục `reports/results` và `reports/figures` là **kết quả kỹ thuật cho dashboard**, vẫn cần cho ứng dụng; không phải báo cáo Word/PDF.

## Chạy nhanh sau khi cài đặt

```powershell
.\run.ps1 -Port 8000
```

Nếu cổng 8000 đang dùng, chọn `-Port 8001`. Script không train, không tự cài dependency. MAE/RMSE/R² test đã lưu của pipeline hiện tại: **0.521043 / 0.721291 / 0.606552**.

## Tài liệu tham khảo

- scikit-learn California Housing documentation.
- Pace, R. Kelley và Ronald Barry, *Sparse Spatial Autoregressions*, Statistics & Probability Letters, 1997.
