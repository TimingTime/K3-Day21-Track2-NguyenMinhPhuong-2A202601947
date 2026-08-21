import argparse
import json
from pathlib import Path

import pandas as pd
from scipy.stats import randint, uniform
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold


def tune(
    data_path: str,
    eval_path: str,
    n_iter: int = 60,
    folds: int = 5,
) -> dict:
    """Tune Random Forest on training CV, then evaluate once on held-out data."""
    train_df = pd.read_csv(data_path)
    eval_df = pd.read_csv(eval_path)

    X_train = train_df.drop(columns=["target"])
    y_train = train_df["target"]
    X_eval = eval_df.drop(columns=["target"])
    y_eval = eval_df["target"]

    common_space = {
        "n_estimators": randint(200, 901),
        "max_depth": [None, 10, 14, 18, 22, 28, 36],
        "min_samples_split": randint(2, 13),
        "min_samples_leaf": randint(1, 6),
        "max_features": ["sqrt", "log2", 0.5, 0.75, None],
        "criterion": ["gini", "entropy", "log_loss"],
        "class_weight": [None, "balanced", "balanced_subsample"],
    }
    search_space = [
        {
            **common_space,
            "bootstrap": [True],
            "max_samples": [None, 0.7, 0.85],
        },
        {**common_space, "bootstrap": [False], "max_samples": [None]},
    ]

    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    search = RandomizedSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=1),
        param_distributions=search_space,
        n_iter=n_iter,
        scoring="accuracy",
        n_jobs=-1,
        cv=cv,
        random_state=42,
        verbose=1,
        return_train_score=False,
    )
    search.fit(X_train, y_train)

    predictions = search.best_estimator_.predict(X_eval)
    result = {
        "training_rows": len(train_df),
        "cv_folds": folds,
        "iterations": n_iter,
        "best_cv_accuracy": float(search.best_score_),
        "eval_accuracy": float(accuracy_score(y_eval, predictions)),
        "eval_f1_score": float(
            f1_score(y_eval, predictions, average="weighted")
        ),
        "best_params": search.best_params_,
    }

    Path("outputs").mkdir(exist_ok=True)
    with open("outputs/tuning_results.json", "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(json.dumps(result, indent=2))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", default="data/train_phase1.csv")
    parser.add_argument("--eval-path", default="data/eval.csv")
    parser.add_argument("--n-iter", type=int, default=60)
    parser.add_argument("--folds", type=int, default=5)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    tune(args.data_path, args.eval_path, args.n_iter, args.folds)
