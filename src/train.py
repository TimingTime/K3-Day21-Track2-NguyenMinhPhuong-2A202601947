import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

EVAL_THRESHOLD = 0.68
EXPERIMENT_NAME = "wine-quality-classification"
SUPPORTED_MODEL_TYPES = {
    "random_forest",
    "gradient_boosting",
    "logistic_regression",
}


def _get_experiment_id() -> str:
    """Configure local or remote MLflow and return the experiment ID."""
    configured_uri = os.getenv("MLFLOW_TRACKING_URI", "").strip()
    tracking_uri = configured_uri or "sqlite:///mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)

    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is not None:
        return experiment.experiment_id

    if configured_uri.startswith(("http://", "https://")):
        return mlflow.create_experiment(EXPERIMENT_NAME)

    artifact_root = Path(
        os.getenv("MLFLOW_ARTIFACT_ROOT", "mlartifacts")
    ).resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)
    return mlflow.create_experiment(
        EXPERIMENT_NAME,
        artifact_location=artifact_root.as_uri(),
    )


def _build_model(params: dict):
    """Create the algorithm selected by ``model_type``."""
    model_params = dict(params)
    model_type = model_params.pop("model_type", "random_forest")
    if model_type not in SUPPORTED_MODEL_TYPES:
        supported = ", ".join(sorted(SUPPORTED_MODEL_TYPES))
        raise ValueError(
            f"Unsupported model_type '{model_type}'. Choose one of: {supported}."
        )

    model_params.setdefault("random_state", 42)
    if model_type == "random_forest":
        model = RandomForestClassifier(**model_params)
    elif model_type == "gradient_boosting":
        model = GradientBoostingClassifier(**model_params)
    else:
        model_params.setdefault("max_iter", 1000)
        model = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("classifier", LogisticRegression(**model_params)),
            ]
        )

    logged_params = {"model_type": model_type, **model_params}
    return model_type, model, logged_params


def _label_distribution(y_train: pd.Series) -> tuple[dict[str, float], list[str]]:
    """Return class ratios and warnings for classes below ten percent."""
    ratios = y_train.value_counts(normalize=True)
    distribution = {
        str(label): float(ratios.get(label, 0.0)) for label in (0, 1, 2)
    }
    warnings = [
        f"Class {label} represents only {ratio:.2%} of training samples."
        for label, ratio in distribution.items()
        if ratio < 0.10
    ]
    for warning in warnings:
        print(f"WARNING: {warning}")
    return distribution, warnings


def _performance_report(
    y_true: pd.Series,
    predictions,
) -> tuple[str, dict[str, dict[str, float]]]:
    """Build a text report and structured per-class metrics."""
    labels = [0, 1, 2]
    matrix = confusion_matrix(y_true, predictions, labels=labels)
    precision, recall, class_f1, support = precision_recall_fscore_support(
        y_true,
        predictions,
        labels=labels,
        zero_division=0,
    )

    per_class = {}
    lines = ["Confusion matrix (rows=true, columns=predicted):"]
    lines.extend(" ".join(str(value) for value in row) for row in matrix)
    lines.extend(["", "Per-class metrics:", "class precision recall f1 support"])
    for index, label in enumerate(labels):
        per_class[str(label)] = {
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "f1_score": float(class_f1[index]),
            "support": int(support[index]),
        }
        lines.append(
            f"{label} {precision[index]:.4f} {recall[index]:.4f} "
            f"{class_f1[index]:.4f} {int(support[index])}"
        )
    return "\n".join(lines) + "\n", per_class


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    """Train, evaluate, track, report, and persist a classifier."""
    df_train = pd.read_csv(data_path)
    df_eval = pd.read_csv(eval_path)

    required_column = "target"
    if required_column not in df_train or required_column not in df_eval:
        raise ValueError("Both datasets must contain a 'target' column.")

    X_train = df_train.drop(columns=[required_column])
    y_train = df_train[required_column]
    X_eval = df_eval.drop(columns=[required_column])
    y_eval = df_eval[required_column]

    if list(X_train.columns) != list(X_eval.columns):
        raise ValueError("Training and evaluation feature columns must match.")

    model_type, model, logged_params = _build_model(params)
    distribution, drift_warnings = _label_distribution(y_train)
    experiment_id = _get_experiment_id()

    with mlflow.start_run(experiment_id=experiment_id):
        mlflow.log_params(logged_params)

        model.fit(X_train, y_train)

        predictions = model.predict(X_eval)
        accuracy = float(accuracy_score(y_eval, predictions))
        f1 = float(f1_score(y_eval, predictions, average="weighted"))
        report, per_class = _performance_report(y_eval, predictions)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(model, "model")

        print(
            f"Model: {model_type} | Accuracy: {accuracy:.4f} | "
            f"F1: {f1:.4f}"
        )

        Path("outputs").mkdir(parents=True, exist_ok=True)
        report_path = Path("outputs/report.txt")
        report_path.write_text(report, encoding="utf-8")
        mlflow.log_artifact(str(report_path), artifact_path="reports")

        with open("outputs/metrics.json", "w", encoding="utf-8") as file:
            json.dump(
                {
                    "model_type": model_type,
                    "accuracy": accuracy,
                    "f1_score": f1,
                    "eval_threshold": EVAL_THRESHOLD,
                    "per_class": per_class,
                    "label_distribution": distribution,
                    "data_drift_warnings": drift_warnings,
                },
                file,
                indent=2,
            )

        Path("models").mkdir(parents=True, exist_ok=True)
        joblib.dump(model, "models/model.pkl")

    return accuracy


if __name__ == "__main__":
    with open("params.yaml", encoding="utf-8") as file:
        parameters = yaml.safe_load(file)
    train(parameters)
