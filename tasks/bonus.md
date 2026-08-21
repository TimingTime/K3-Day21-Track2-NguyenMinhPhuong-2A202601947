# Bonus implementation

## Bonus 1 — Remote MLflow with DagsHub

The workflow already forwards these optional GitHub Secrets to `src/train.py`:

- `MLFLOW_TRACKING_URI`
- `MLFLOW_TRACKING_USERNAME`
- `MLFLOW_TRACKING_PASSWORD`

When they are empty, training safely falls back to local `sqlite:///mlflow.db`.
To activate remote tracking, connect this repository to DagsHub and add the
three values shown on the DagsHub **Remote → Experiments** setup page.

## Bonus 2 — Multiple algorithms

`params.yaml` supports:

- `random_forest`
- `gradient_boosting`
- `logistic_regression`

Select an algorithm using `model_type` and keep only parameters accepted by
that estimator. Every run logs `model_type`, parameters, Accuracy and F1 to
MLflow.

Local comparison on the same Phase 1/eval split:

| Algorithm | Accuracy | Weighted F1 |
|---|---:|---:|
| Random Forest | **0.6820** | **0.6811** |
| Gradient Boosting | 0.5960 | 0.5925 |
| Logistic Regression | 0.5680 | 0.5632 |

Random Forest remains the deployed choice because it performs best.

## Bonus 3 — Automatic performance report

Training creates `outputs/report.txt` with a 3x3 confusion matrix and
precision, recall, F1 and support for classes 0, 1 and 2. GitHub Actions uploads
the report in the `metrics` artifact and promotes it to
`models/latest/report.txt` after approval.

## Bonus 4 — Protect the deployed model

The Eval job downloads `models/latest/metrics.json` from S3. Deployment is
blocked when the new Accuracy is lower than the currently deployed Accuracy.
On the first run, no previous metrics exist, so deployment is allowed. Approved
metrics are versioned beside the model in S3.

## Bonus 5 — Label-distribution warning

Training writes class ratios to `label_distribution` in `metrics.json`. A clear
warning is printed and recorded in `data_drift_warnings` whenever any class
represents less than 10% of training samples.
