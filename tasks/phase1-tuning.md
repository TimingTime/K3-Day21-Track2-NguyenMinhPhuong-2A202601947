# Phase 1 Random Forest tuning

## Mục tiêu

Tuning Random Forest trên đúng 2.998 mẫu của Phase 1 mà không hạ quality
threshold `0.70` và không dùng tập eval để lựa chọn tham số.

## Phương pháp

- Dữ liệu Phase 1 được lấy lại từ DVC hash
  `c43afab731fd6431a94f888fdc687876`.
- `RandomizedSearchCV` thử 60 cấu hình.
- Mỗi cấu hình được đánh giá bằng `StratifiedKFold` 5 folds.
- Search space gồm `n_estimators`, `max_depth`, `min_samples_split`,
  `min_samples_leaf`, `max_features`, `criterion`, `class_weight`,
  `bootstrap` và `max_samples`.
- Tập `eval.csv` chỉ được dùng một lần sau khi CV đã chọn xong cấu hình.

## Kết quả

| Cấu hình | CV accuracy | Eval accuracy | Eval F1 |
|---|---:|---:|---:|
| Baseline Phase 1 | 0.6594 | 0.6820 | 0.6811 |
| Best CV tuning | 0.6644 | 0.6560 | 0.6546 |

Cấu hình có CV accuracy cao nhất:

```yaml
n_estimators: 800
max_depth: 22
min_samples_split: 5
min_samples_leaf: 2
max_features: sqrt
criterion: log_loss
class_weight: balanced_subsample
bootstrap: true
max_samples: 0.85
```

## Quyết định

Tuning tăng CV accuracy khoảng `0.005`, nhưng làm accuracy trên tập eval giảm từ
`0.682` xuống `0.656`. Vì vậy cấu hình tuned bị từ chối và baseline được giữ
nguyên. Cả hai vẫn thấp hơn threshold `0.70`, nên Phase 1 không đủ điều kiện
deploy. Đây là kết quả hợp lệ của quality gate, không phải lỗi CI/CD.

Quality chỉ vượt gate sau khi bổ sung dữ liệu Phase 2: 5.996 mẫu giúp accuracy
tăng lên `0.7460` và F1 tăng lên `0.7449`.

## Chạy lại

```powershell
.\.venv\Scripts\python.exe src\tune.py `
  --data-path <phase-1-csv> `
  --eval-path data\eval.csv `
  --n-iter 60 `
  --folds 5
```
