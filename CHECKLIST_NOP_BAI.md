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

## Ảnh minh chứng đã lưu trong repository

- [x] `evidence/01-mlflow-runs.png`: 8 matching runs; bảng nhìn thấy nhiều run
  cùng hai cột `accuracy` và `f1_score`.
- [x] `evidence/02-actions-overview.png`: lịch sử các workflow run.
- [x] `evidence/03-actions-phase1-green.png`: Phase 1 có đủ bốn job xanh.
- [x] `evidence/04-actions-phase2-green.png`: commit dữ liệu Phase 2 kích hoạt đủ
  bốn job xanh.
- [x] `evidence/05-eval-gate-blocked.png`: Eval thất bại và Deploy bị bỏ qua.
- [x] `evidence/06-s3-model.png`: model tại `models/latest/model.pkl`.
- [x] `evidence/07-s3-dvc-data.png`: object DVC dưới `dvc/files/md5/`.
- [x] `evidence/08-s3-cli-verification.png`: AWS CLI xác minh cả `dvc/` và model.
- [x] `evidence/09-api-predict-result.png`: API trả dự đoán hợp lệ.

## Ảnh nên chụp thêm trước khi tắt AWS

Đặt tên ảnh theo thứ tự dưới đây để người chấm dễ đối chiếu:

1. `10-api-health-predict.png`: chụp terminal sau khi chạy cả hai lệnh (ảnh
   `09-api-predict-result.png` hiện mới chỉ có JSON của `/predict`):

   ```powershell
   curl.exe http://3.227.211.151:8000/health
   curl.exe -X POST http://3.227.211.151:8000/predict `
     -H "Content-Type: application/json" `
     -d '{\"features\":[7.4,0.7,0.0,1.9,0.076,11,34,0.9978,3.51,0.56,9.4,0]}'
   ```

2. `11-s3-model-versions.png`: bật **Show versions** và chụp lịch sử các phiên
   bản của `models/latest/model.pkl`.

## Hạng mục gửi cho giảng viên

1. URL repo:
   `https://github.com/TimingTime/K3-Day21-Track2-NguyenMinhPhuong-2A202601947`
2. File [`BAO_CAO.md`](BAO_CAO.md) hoặc xuất file này thành PDF một trang.
3. Các ảnh trong thư mục `evidence/`; ưu tiên bổ sung hai ảnh còn thiếu ở mục
   trên nếu giảng viên yêu cầu minh chứng trực quan đầy đủ.
4. Nếu rubric gốc vẫn ghi gate `0.70`, đính kèm bằng chứng giảng viên đã phê
   duyệt đổi gate xuống `0.68`.

## Sau khi chụp xong

EC2 hiện vẫn phát sinh chi phí. Không destroy trước khi đủ ảnh. Sau khi nộp,
thực hiện theo [`tasks/aws-teardown.md`](tasks/aws-teardown.md). Nếu còn cần demo
trong vài ngày, có thể stop EC2 trước và chỉ terminate/destroy sau khi đã được
chấm xong.
