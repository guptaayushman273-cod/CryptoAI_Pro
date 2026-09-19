import json
import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TRAIN_DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "candles",
    "ml_train.json"
)

MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_model.pkl"
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_scaler.pkl"
)


# ============================================================
# FEATURES
# ============================================================

FEATURE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "RSI",
    "return_1",
    "return_5",
    "return_10",
    "price_vs_ema20",
    "price_vs_ema50",
    "ema20_vs_ema50",
    "macd_relative",
    "macd_signal_diff",
    "macd_signal_diff_percent",
    "bb_position",
    "bb_width",
    "atr_percent",
    "volume_change"
]


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("CRYPTOAI PRO - V3 STEP 14D")
    print("RANDOM FOREST TRAINING")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    print("\nLoading improved training dataset...")
    print(TRAIN_DATA_PATH)

    if not os.path.exists(TRAIN_DATA_PATH):
        raise FileNotFoundError(
            f"Training dataset not found: {TRAIN_DATA_PATH}"
        )

    with open(
        TRAIN_DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not data:
        raise ValueError(
            "Training dataset is empty."
        )

    df = pd.DataFrame(data)

    print(
        f"\nTraining rows: {len(df)}"
    )

    # --------------------------------------------------------
    # VALIDATE FEATURES
    # --------------------------------------------------------

    print("\nValidating features...")

    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            f"Missing features: {missing_features}"
        )

    if "target" not in df.columns:

        raise ValueError(
            "Target column not found."
        )

    print(
        f"Features available: "
        f"{len(FEATURE_COLUMNS)}"
    )

    # --------------------------------------------------------
    # TARGET DISTRIBUTION
    # --------------------------------------------------------

    print("\nTarget distribution:")
    print("-" * 40)

    target_counts = (
        df["target"]
        .value_counts()
        .sort_index()
    )

    print(
        target_counts.to_string()
    )

    total_rows = len(df)

    for target_value in [0, 1]:

        count = int(
            target_counts.get(
                target_value,
                0
            )
        )

        percentage = (
            count / total_rows * 100
        )

        print(
            f"Target {target_value}: "
            f"{count} "
            f"({percentage:.2f}%)"
        )

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    X = df[
        FEATURE_COLUMNS
    ].copy()

    y = df[
        "target"
    ].astype(int)

    if X.isnull().any().any():

        raise ValueError(
            "Training features contain missing values."
        )

    # --------------------------------------------------------
    # SCALE
    # --------------------------------------------------------

    print(
        "\nScaling training features..."
    )

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(
        X
    )

    print(
        "Scaling complete."
    )

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    print(
        "\nCreating Random Forest..."
    )

    model = RandomForestClassifier(

        n_estimators=400,

        max_depth=12,

        min_samples_leaf=8,

        min_samples_split=10,

        class_weight="balanced",

        random_state=42,

        n_jobs=-1
    )

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    print(
        "Training model..."
    )

    model.fit(
        X_scaled,
        y
    )

    print(
        "Training complete."
    )

    # --------------------------------------------------------
    # TRAINING METRICS
    # --------------------------------------------------------

    predictions = model.predict(
        X_scaled
    )

    probabilities = (
        model.predict_proba(
            X_scaled
        )[:, 1]
    )

    accuracy = accuracy_score(
        y,
        predictions
    )

    precision = precision_score(
        y,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y,
        predictions,
        zero_division=0
    )

    auc = roc_auc_score(
        y,
        probabilities
    )

    matrix = confusion_matrix(
        y,
        predictions
    )

    print()
    print("=" * 60)
    print("TRAINING PERFORMANCE")
    print("=" * 60)

    print(
        f"Accuracy : "
        f"{accuracy * 100:.2f}%"
    )

    print(
        f"Precision: "
        f"{precision * 100:.2f}%"
    )

    print(
        f"Recall   : "
        f"{recall * 100:.2f}%"
    )

    print(
        f"F1 Score : "
        f"{f1 * 100:.2f}%"
    )

    print(
        f"ROC-AUC  : "
        f"{auc:.4f}"
    )

    print(
        "\nConfusion Matrix:"
    )

    print(matrix)

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y,
            predictions,
            digits=4,
            zero_division=0
        )
    )

    # --------------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------------

    importance_df = pd.DataFrame({

        "feature":
            FEATURE_COLUMNS,

        "importance":
            model.feature_importances_
    })

    importance_df = (
        importance_df
        .sort_values(
            "importance",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    print()
    print("=" * 60)
    print("TOP FEATURE IMPORTANCE")
    print("=" * 60)

    for index, row in (
        importance_df.head(10)
        .iterrows()
    ):

        print(
            f"{index + 1:2}. "
            f"{row['feature']:<28} "
            f"{row['importance']:.6f}"
        )

    # --------------------------------------------------------
    # SAVE MODEL
    # --------------------------------------------------------

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    joblib.dump(
        scaler,
        SCALER_PATH
    )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 14D TRAINING COMPLETE")
    print("=" * 60)

    print(
        f"\nModel saved:\n"
        f"{MODEL_PATH}"
    )

    print(
        f"\nScaler saved:\n"
        f"{SCALER_PATH}"
    )

    print()
    print(
        "Algorithm: Random Forest"
    )

    print(
        "Target: future 5-candle "
        "return > +0.20%"
    )

    print(
        "Class balancing: ENABLED"
    )

    print(
        f"Features: "
        f"{len(FEATURE_COLUMNS)}"
    )

    print()
    print(
        "Next: evaluate on unseen "
        "chronological test data."
    )

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()