import json
import os
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

EVAL_THRESHOLD = 0.68
EXPERIMENT_NAME = "wine-quality-classification"


def _get_experiment_id() -> str:
    """Configure local MLflow defaults and return the experiment ID."""
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    artifact_root = Path(
        os.getenv("MLFLOW_ARTIFACT_ROOT", "mlartifacts")
    ).resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    mlflow.set_tracking_uri(tracking_uri)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is not None:
        return experiment.experiment_id

    return mlflow.create_experiment(
        EXPERIMENT_NAME,
        artifact_location=artifact_root.as_uri(),
    )


def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    """Train, evaluate, track, and persist a Random Forest model."""
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

    model_params = dict(params)
    model_params.setdefault("random_state", 42)
    experiment_id = _get_experiment_id()

    with mlflow.start_run(experiment_id=experiment_id):
        mlflow.log_params(model_params)

        model = RandomForestClassifier(**model_params)
        model.fit(X_train, y_train)

        predictions = model.predict(X_eval)
        accuracy = float(accuracy_score(y_eval, predictions))
        f1 = float(f1_score(y_eval, predictions, average="weighted"))

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)
        mlflow.sklearn.log_model(model, "model")

        print(f"Accuracy: {accuracy:.4f} | F1: {f1:.4f}")

        Path("outputs").mkdir(parents=True, exist_ok=True)
        with open("outputs/metrics.json", "w", encoding="utf-8") as file:
            json.dump(
                {
                    "accuracy": accuracy,
                    "f1_score": f1,
                    "eval_threshold": EVAL_THRESHOLD,
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
