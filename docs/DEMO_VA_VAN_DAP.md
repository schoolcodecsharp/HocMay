# Demo 5–7 phút

1. Giới thiệu (30 giây): block group, năm 1990, tám biến, target 100.000 USD và hạn chế dùng.
2. Dữ liệu (45 giây): cadata thành SQLite, 20.640 dòng khớp sklearn, chỉ xem 14.448 dòng train; giải thích chia households.
3. Dashboard (75 giây): baseline/LR/SGD, chọn bằng validation, loss 80 epoch, ba learning rate không ổn định.
4. Residual (45 giây): cap, nhóm giá cao và địa lý; không suy nhân quả.
5. Form (60 giây): nhập hợp lệ, predict và đọc đơn vị. Đổi input thì kết quả cũ ẩn. Xóa field thì báo lỗi.
6. OpenAPI (30 giây): gửi JSON hợp lệ, sau đó MedInc chuỗi hoặc thêm field để nhận 422. Không xóa artifact đang dùng để demo lỗi.
7. Model card (30 giây): checksum, kiểm thử, train-only serving và dấu vết test đã quan sát.

Trước demo: bật server, health trả 200, chạy pytest, CSDL sẵn. Web chạy offline sau khi đã tải dữ liệu/artifact. Không tải lần đầu trong buổi bảo vệ.

## Vấn đáp

**Một hàng là gì?** Census block group, không phải căn nhà. Tránh suy luận cá nhân từ dữ liệu tổng hợp.

**Tại sao baseline?** Mean train cho biết có học tốt hơn một hằng số hay không. Không dùng mean toàn dữ liệu.

**Tại sao split trước scaler?** Mean/std là tham số học. Dùng validation/test để tính chúng lộ phân phối. Candidate và serving hiện tại đều train-only; artifact refit cũ đã được lưu riêng, không phục vụ nữa.

**Gradient?** J=Σ(yhat−y)²/(2m), gradient w=Xᵀ(Xw+b−y)/m, gradient b=Σ(Xw+b−y)/m. SGD: w←w−eta·error·x, b←b−eta·error.

**SGD khác LR?** LR giải least squares bằng bộ giải số. SGD tối ưu lặp hữu hạn, nhạy eta/scale/thứ tự. Không gọi sklearn LR là tự cài phương trình chuẩn.

**Learning rate lớn?** Có thể dao động/phân kỳ, nhất là tỷ lệ cực trị. eta≥.001 có loss rất lớn. Không kết luận .0001 quá nhỏ: nó tốt nhất trong lưới đã thử.

**MAE/RMSE/R²?** RMSE phạt lỗi lớn mạnh hơn, cùng đơn vị target. R² so với mean tập đánh giá, không phải phần trăm accuracy. R² âm hợp lệ.

**Tại sao không chọn SGD dù test thấp hơn?** Quyết định đã chốt bằng validation. Chọn lại bằng test biến test thành tuning.

**Coefficient chuẩn hóa?** Thay đổi prediction khi tăng một độ lệch chuẩn train, giữ biến khác cố định. Đồng tuyến tính/yếu tố nhiễu khiến dấu không chứng minh nhân quả.

**Outlier?** Tỷ lệ cao có thể do households nhỏ, không nhất thiết sai. Ghi cờ, giữ dữ liệu và công bố tác động.

**Target cap?** Giá trị vượt trần bị gom ở 5.00001, mất thông tin và tạo cấu trúc residual. Không coi đó là giá thị trường hiện tại.

**Địa lý?** Vùng gần nhau tương tự, random split có thể lạc quan cho vùng mới. Spatial holdout là hướng tương lai, không thay split sau xem test.

**API train không?** Không, chỉ checksum/load/predict trusted pipeline. Test chặn fit trong request.

**CSDL thêm gì?** Schema/ràng buộc/provenance/split và phân trang. View quy đổi không tạo dataset khác.

**Chưa chứng minh gì?** Lịch sử sáu tuần của mỗi người và giấy phép tái phân phối. Sửa phạm vi scaler của serving không biến test đã xem thành một test độc lập mới.
