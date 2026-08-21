import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.train import EVAL_THRESHOLD, train


FEATURE_NAMES = [
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
    "wine_type",
]


def _make_temp_data(tmp_path: Path) -> tuple[str, str]:
    """Create a small deterministic dataset with the production schema."""
    rng = np.random.default_rng(0)
    sample_count = 200
    features = rng.random((sample_count, len(FEATURE_NAMES)))
    targets = rng.integers(0, 3, size=sample_count)

    dataframe = pd.DataFrame(features, columns=FEATURE_NAMES)
    dataframe["target"] = targets

    train_path = tmp_path / "train.csv"
    eval_path = tmp_path / "eval.csv"
    dataframe.iloc[:160].to_csv(train_path, index=False)
    dataframe.iloc[160:].to_csv(eval_path, index=False)
    return str(train_path), str(eval_path)


def test_train_returns_float(tmp_path, monkeypatch):
    """The training function returns an accuracy in the expected range."""
    monkeypatch.chdir(tmp_path)
    train_path, eval_path = _make_temp_data(tmp_path)

    accuracy = train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )

    assert isinstance(accuracy, float)
    assert 0.0 <= accuracy <= 1.0


def test_metrics_file_created(tmp_path, monkeypatch):
    """Training persists both required evaluation metrics."""
    monkeypatch.chdir(tmp_path)
    train_path, eval_path = _make_temp_data(tmp_path)

    train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )

    metrics_path = Path("outputs/metrics.json")
    assert metrics_path.exists()
    with metrics_path.open(encoding="utf-8") as file:
        metrics = json.load(file)
    assert "accuracy" in metrics
    assert "f1_score" in metrics
    assert metrics["eval_threshold"] == EVAL_THRESHOLD == 0.68


def test_model_file_created(tmp_path, monkeypatch):
    """Training persists a deployable model file."""
    monkeypatch.chdir(tmp_path)
    train_path, eval_path = _make_temp_data(tmp_path)

    train(
        {"n_estimators": 10, "max_depth": 3},
        data_path=train_path,
        eval_path=eval_path,
    )

    assert Path("models/model.pkl").exists()
