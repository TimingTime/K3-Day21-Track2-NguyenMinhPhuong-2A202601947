# AWS Setup Cho Phần Base

Code trong repository đã được cấu hình cho Amazon S3 và EC2. Các bước dưới
đây cần thực hiện bằng tài khoản AWS của người học.

## 1. Tạo S3 bucket và bật versioning

Chọn một tên bucket duy nhất và region gần Việt Nam:

```bash
export CLOUD_BUCKET=<TEN_BUCKET_DUY_NHAT>
export AWS_DEFAULT_REGION=us-east-1

aws s3api create-bucket \
  --bucket "$CLOUD_BUCKET" \
  --region "$AWS_DEFAULT_REGION"

aws s3api put-bucket-versioning \
  --bucket "$CLOUD_BUCKET" \
  --versioning-configuration Status=Enabled
```

Kiểm tra:

```bash
aws s3api get-bucket-versioning --bucket "$CLOUD_BUCKET"
```

## 2. Cấu hình DVC và upload dữ liệu

Trên máy local, sau khi kích hoạt `.venv`:

```bash
dvc remote add --force -d myremote "s3://$CLOUD_BUCKET/dvc"
dvc add data/train_phase1.csv data/eval.csv data/train_phase2.csv
dvc push
```

Commit các file DVC, không commit CSV:

```bash
git add .dvc .dvcignore data/*.dvc
git commit -m "data: track Wine Quality datasets with DVC"
```

## 3. Quyền AWS

IAM principal dùng bởi GitHub Actions cần tối thiểu:

- `s3:ListBucket` trên bucket;
- `s3:GetObject` và `s3:PutObject` trên `bucket/*`.

EC2 nên dùng IAM role thay cho access key. Role của EC2 chỉ cần
`s3:GetObject` đối với:

```text
arn:aws:s3:::<TEN_BUCKET>/models/latest/model.pkl
```

## 4. Chuẩn bị EC2

Tạo Ubuntu EC2 instance, gắn IAM role ở trên và mở:

- TCP 22 cho SSH/deploy;
- TCP 8000 để gọi API trong phạm vi phù hợp với bài lab.

SSH vào instance rồi chạy:

```bash
sudo apt-get update
sudo apt-get install -y git python3-venv curl
git clone <URL_REPOSITORY> "$HOME/mlops-lab"
cd "$HOME/mlops-lab"
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

Sao chép service mẫu và sửa `User`, đường dẫn home, bucket nếu EC2 không dùng
user `ubuntu`:

```bash
sudo cp deploy/mlops-serve.service.example /etc/systemd/system/mlops-serve.service
sudo nano /etc/systemd/system/mlops-serve.service
sudo systemctl daemon-reload
sudo systemctl enable mlops-serve
```

Cho phép user deploy restart và xem trạng thái đúng một service mà không cần
nhập mật khẩu. Chạy `sudo visudo -f /etc/sudoers.d/mlops-serve` và thêm:

```text
ubuntu ALL=(root) NOPASSWD: /bin/systemctl restart mlops-serve, /bin/systemctl status mlops-serve
```

## 5. GitHub Secrets

Tạo năm repository secrets:

| Secret | Giá trị |
|---|---|
| `CLOUD_CREDENTIALS` | JSON AWS ở định dạng bên dưới |
| `CLOUD_BUCKET` | Tên S3 bucket, không gồm `s3://` |
| `VM_HOST` | Public IP hoặc DNS của EC2 |
| `VM_USER` | Thường là `ubuntu` |
| `VM_SSH_KEY` | Toàn bộ private key dùng để SSH vào EC2 |

Định dạng `CLOUD_CREDENTIALS`:

```json
{
  "aws_access_key_id": "REPLACE_ME",
  "aws_secret_access_key": "REPLACE_ME",
  "region": "us-east-1"
}
```

Không commit access key hoặc SSH private key vào Git.

## 6. Chạy pipeline base

Push code và các file `.dvc` lên nhánh `main`. Workflow thực hiện:

```text
Test -> Train -> Eval (accuracy >= 0.68) -> Deploy
```

Với threshold được phê duyệt là `0.68`, baseline phase 1 đạt `0.682` và được
deploy. Cấu hình tuning chỉ đạt `0.656` nên vẫn bị eval gate chặn.

## 7. Continuous training với phase 2

Chỉ thực hiện sau khi dữ liệu phase 1 đã được upload và workflow ban đầu đã
được quan sát:

```bash
python add_new_data.py
dvc add data/train_phase1.csv
dvc push
git add data/train_phase1.csv.dvc
git commit -m "data: add 2998 phase-2 training samples"
git push origin main
```

Luôn chạy `dvc push` trước `git push` để runner có thể tải đúng dữ liệu mới.

## 8. Xác minh API

```bash
curl http://<EC2_PUBLIC_IP>:8000/health

curl -X POST http://<EC2_PUBLIC_IP>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[7.4,0.70,0.00,1.9,0.076,11.0,34.0,0.9978,3.51,0.56,9.4,0]}'
```

Kết quả dự kiến:

```json
{"prediction":0,"label":"thap"}
```
