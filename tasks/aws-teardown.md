# AWS teardown checklist

Chỉ thực hiện sau khi đã chụp đủ bằng chứng pipeline và API. Các lệnh dưới đây
nhắm đúng tài nguyên của lab tại `us-east-1`.

## Tài nguyên của lab

- EC2: `i-068a81d099575023f`
- EBS gốc: `vol-07457b981f08674da` (`DeleteOnTermination=true`)
- Security group: `sg-090ebf0ce2a12dbe4`
- Key pair: `k3-day21-mlops-key`
- S3 bucket: `k3-day21-mlops-432649418926`
- IAM CI user: `k3-day21-mlops-github`
- EC2 role: `k3-day21-mlops-ec2-role`
- Instance profile: `k3-day21-mlops-ec2-profile`
- Provisioning policy attached to `AI20`: `K3Day21ProvisioningS3`

## Thứ tự dọn dẹp

1. Xóa GitHub Actions Secrets của repository.
2. Terminate EC2 và đợi trạng thái `terminated`.
3. Xóa key pair và security group.
4. Xóa mọi version/delete marker trong S3 rồi xóa bucket.
5. Xóa access key, inline policy và IAM user của CI.
6. Gỡ role khỏi instance profile, xóa profile, policy của role và role.
7. Gỡ provisioning policy khỏi `AI20`, sau đó xóa policy.
8. Kiểm tra không còn EC2, EBS, S3 hoặc IAM resource của lab.

## Kiểm tra nhanh trước khi thoát AWS Console

```powershell
aws ec2 describe-instances --region us-east-1 --instance-ids i-068a81d099575023f
aws ec2 describe-volumes --region us-east-1 --volume-ids vol-07457b981f08674da
aws s3api head-bucket --bucket k3-day21-mlops-432649418926
aws iam get-user --user-name k3-day21-mlops-github
aws iam get-role --role-name k3-day21-mlops-ec2-role
```

Sau teardown hoàn chỉnh, các lệnh kiểm tra S3/IAM sẽ trả về `NotFound` và EC2
sẽ ở trạng thái `terminated`; volume gốc sẽ tự bị xóa.
