# Submission evidence

| File | Evidence |
|---|---|
| `01-mlflow-runs.png` | MLflow reports 8 matching runs and visibly shows multiple runs with `accuracy` and `f1_score` |
| `02-actions-overview.png` | Workflow run history |
| `03-actions-phase1-green.png` | Phase 1: Test, Train, Eval and Deploy passed |
| `04-actions-phase2-green.png` | Phase 2 data commit triggered all four jobs successfully |
| `05-eval-gate-blocked.png` | Weak model failed Eval and Deploy was skipped |
| `06-s3-model.png` | Model stored at `models/latest/model.pkl` |
| `07-s3-dvc-data.png` | DVC objects stored below `dvc/files/md5/` |
| `08-s3-cli-verification.png` | AWS CLI verifies both S3 prefixes |
| `09-api-predict-result.png` | Live EC2 API returns `{"prediction":0,"label":"thap"}` |

For the final submission, a terminal screenshot showing both successful commands
is stronger than `09-api-predict-result.png` alone. Expected responses:

```text
GET  /health  -> {"status":"ok"}
POST /predict -> {"prediction":0,"label":"thap"}
```

Do not submit a `/predict` screenshot that returns `Field required`; that means
the request omitted its JSON body.
