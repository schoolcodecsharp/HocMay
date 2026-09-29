# Data Dictionary

| Variable | Data type | Meaning | Unit | Role | Thời điểm có sẵn |
|---|---|---|---|---|---|
| MedInc | float | Thu nhập trung vị của khu vực | Chục nghìn USD | Feature | Khi hồ sơ tổng hợp điều tra khu vực có sẵn |
| HouseAge | float | Tuổi nhà trung vị | Năm | Feature | Khi hồ sơ nhà ở tổng hợp có sẵn |
| AveRooms | float | Số phòng trung bình mỗi hộ | Phòng/hộ | Feature | Khi hồ sơ nhà ở tổng hợp có sẵn |
| AveBedrms | float | Số phòng ngủ trung bình mỗi hộ | Phòng ngủ/hộ | Feature | Khi hồ sơ nhà ở tổng hợp có sẵn |
| Population | float | Dân số block group | Người | Feature | Khi hồ sơ dân số tổng hợp có sẵn |
| AveOccup | float | Số người cư trú trung bình mỗi hộ | Người/hộ | Feature | Khi hồ sơ dân số và hộ gia đình có sẵn |
| Latitude | float | Vĩ độ của khu vực | Độ | Feature | Khi xác định vị trí block group |
| Longitude | float | Kinh độ của khu vực | Độ | Feature | Khi xác định vị trí block group |
| MedHouseVal | float | Giá trị nhà trung vị của khu vực | 100.000 USD | Target | Sau khi tổng hợp giá trị nhà lịch sử cho khu vực |

Project giả định tám feature đều có sẵn tại thời điểm tạo ước lượng minh họa cho một census block group lịch sử. Không có ID riêng trong dataset scikit-learn này.
