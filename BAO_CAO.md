# BÁO CÁO LAB DAY 21 — CI/CD CHO AI SYSTEMS

**Sinh viên:** Nguyễn Minh Phương  
**Repository:** https://github.com/TimingTime/K3-Day21-Track2-NguyenMinhPhuong-2A202601947

## 1. Thực nghiệm và lựa chọn mô hình

Mô hình sử dụng `RandomForestClassifier`, dữ liệu Phase 1 gồm 2.998 mẫu và tập
đánh giá được giữ riêng. MLflow đã ghi 8 runs với đầy đủ `accuracy` và
`f1_score`. Ba cấu hình đại diện là:

| `n_estimators` | `max_depth` | `min_samples_split` | Accuracy | F1 |
|---:|---:|---:|---:|---:|
| 50 | 3 | 2 | 0.558 | 0.5185 |
| 100 | 5 | 2 | 0.564 | 0.5534 |
| 200 | 10 | 5 | 0.644 | 0.6417 |
| **300** | **None** | **2** | **0.682** | **0.6811** |

Cấu hình được chọn là `n_estimators=300`, `max_depth=None`,
`min_samples_split=2`, `random_state=42` vì cho kết quả Phase 1 tốt nhất trong
các cấu hình được chấp nhận. RandomizedSearchCV 5-fold tìm được cấu hình có CV
accuracy `0.6644`, nhưng chỉ đạt eval accuracy `0.656`; do đó cấu hình này bị
loại. Quality gate cuối cùng được phê duyệt là `0.68`, nên baseline `0.682`
được phép triển khai.

## 2. Pipeline và kết quả

DVC lưu dữ liệu trên Amazon S3; bucket đã bật Object Versioning. GitHub Actions
chạy tuần tự `Test → Train → Eval → Deploy`. Model chỉ được upload vào
`models/latest/model.pkl` và restart dịch vụ EC2 sau khi vượt gate. Run #7 hoàn
thành cả bốn job; API FastAPI trả `{"status":"ok"}` ở `/health` và trả dự đoán
hợp lệ ở `/predict`. S3 hiện giữ 5 phiên bản của model. Commit dữ liệu Phase 2
đã tự kích hoạt run #2, dùng 5.996 mẫu và tăng accuracy lên `0.746`, F1 lên
`0.7449`, chứng minh continuous training hoạt động.

## 3. Khó khăn và cách giải quyết

- DVC và S3 Object Versioning có vai trò khác nhau: DVC quản lý phiên bản dữ
  liệu theo Git, còn S3 Versioning giữ lịch sử object/model; vì vậy sử dụng cả
  hai thay vì thay thế lẫn nhau.
- API ban đầu sai tên feature so với mô hình (dấu cách trong tên cột). Đã đồng
  bộ đúng 12 feature và bổ sung unit test cho `/health`, `/predict`.
- Để tránh phát hành model kém, pipeline chỉ promote artifact lên S3 sau job
  Eval. Run #5 với accuracy `0.656` bị chặn, còn run #7 với `0.682` vượt gate
  được phê duyệt `0.68` và deploy thành công.

