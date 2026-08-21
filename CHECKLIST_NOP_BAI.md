# Checklist nộp bài

## Các phần đã hoàn thành

- [x] Repo GitHub chứa code, DVC pointer, test và workflow CI/CD.
- [x] MLflow local có 8 runs, đủ nhiều cấu hình và đủ Accuracy/F1.
- [x] DVC remote trên S3 và S3 Object Versioning hoạt động.
- [x] GitHub Actions có đủ bốn job `Test`, `Train`, `Eval`, `Deploy` màu xanh.
- [x] Eval gate chặn model `0.656` và cho model `0.682` qua ngưỡng được phê
  duyệt `0.68`.
- [x] API FastAPI đang chạy trên EC2 và trả kết quả dự đoán.
- [x] Commit dữ liệu Phase 2 tự kích hoạt pipeline, đạt accuracy `0.746`.
- [x] Báo cáo ngắn: [`BAO_CAO.md`](BAO_CAO.md).

## Ảnh bạn cần tự chụp trước khi tắt AWS

Đặt tên ảnh theo thứ tự dưới đây để người chấm dễ đối chiếu:

1. `01-mlflow-runs.png`: chạy lệnh sau rồi mở `http://127.0.0.1:5000` và chụp
   bảng MLflow có ít nhất 3 runs cùng các cột tham số, Accuracy và F1.

   ```powershell
   .\.venv\Scripts\mlflow.exe ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```

2. `02-actions-phase1.png`: chụp
   [run #7](https://github.com/TimingTime/K3-Day21-Track2-NguyenMinhPhuong-2A202601947/actions/runs/32468250157)
   với cả bốn job màu xanh.
3. `03-eval-gate-block.png`: chụp
   [run #5](https://github.com/TimingTime/K3-Day21-Track2-NguyenMinhPhuong-2A202601947/actions/runs/32466134872)
   cho thấy Eval thất bại và Deploy bị bỏ qua khi accuracy là `0.656`.
4. `04-actions-phase2.png`: chụp
   [run #2](https://github.com/TimingTime/K3-Day21-Track2-NguyenMinhPhuong-2A202601947/actions/runs/32463770858)
   của commit thêm dữ liệu Phase 2, cả bốn job màu xanh.
5. `05-api-health-predict.png`: chụp terminal sau khi chạy:

   ```powershell
   curl.exe http://3.227.211.151:8000/health
   curl.exe -X POST http://3.227.211.151:8000/predict `
     -H "Content-Type: application/json" `
     -d '{\"features\":[7.4,0.7,0.0,1.9,0.076,11,34,0.9978,3.51,0.56,9.4,0]}'
   ```

6. `06-s3-data.png`: trong S3 Console, chụp bucket
   `k3-day21-mlops-432649418926`, gồm prefix `dvc/` và
   `models/latest/model.pkl`.
7. `07-s3-model-versions.png`: bật **Show versions** và chụp lịch sử các phiên
   bản của `models/latest/model.pkl`.

## Hạng mục gửi cho giảng viên

1. URL repo:
   `https://github.com/TimingTime/K3-Day21-Track2-NguyenMinhPhuong-2A202601947`
2. File [`BAO_CAO.md`](BAO_CAO.md) hoặc xuất file này thành PDF một trang.
3. Bảy ảnh theo thứ tự ở trên.
4. Nếu rubric gốc vẫn ghi gate `0.70`, đính kèm bằng chứng giảng viên đã phê
   duyệt đổi gate xuống `0.68`.

## Sau khi chụp xong

EC2 hiện vẫn phát sinh chi phí. Không destroy trước khi đủ ảnh. Sau khi nộp,
thực hiện theo [`tasks/aws-teardown.md`](tasks/aws-teardown.md). Nếu còn cần demo
trong vài ngày, có thể stop EC2 trước và chỉ terminate/destroy sau khi đã được
chấm xong.
