import json
import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
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
    "train_dataset.json"
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

    print("=" * 60)
    print("CRYPTOAI PRO - V3 STEP 11 RANDOM FOREST TRAINING")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD TRAINING DATA
    # --------------------------------------------------------

    print("\nLoading training dataset...")

    with open(TRAIN_DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)

    print(f"Training rows: {len(df)}")

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

    print(f"Features available: {len(FEATURE_COLUMNS)}")

    # --------------------------------------------------------
    # VALIDATE TARGET
    # --------------------------------------------------------

    if "target" not in df.columns:
        raise ValueError(
            "Target column not found in training dataset."
        )

    print("\nTarget distribution:")

    print(
        df["target"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    X = df[FEATURE_COLUMNS].copy()
    y = df["target"].astype(int)

    if X.isnull().any().any():
        raise ValueError(
            "Training features contain missing values."
        )

    # --------------------------------------------------------
    # SCALE FEATURES
    # --------------------------------------------------------

    print("\nScaling training features...")

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    print("Scaling complete.")

    # --------------------------------------------------------
    # CREATE RANDOM FOREST
    # --------------------------------------------------------

    print("\nCreating Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    print("Training Random Forest...")

    model.fit(X_scaled, y)

    print("Training complete.")

    # --------------------------------------------------------
    # TRAINING ACCURACY
    # --------------------------------------------------------

    training_predictions = model.predict(X_scaled)

    training_accuracy = (
        training_predictions == y
    ).mean()

    print(
        f"\nTraining accuracy: "
        f"{training_accuracy * 100:.2f}%"
    )

    # --------------------------------------------------------
    # SAVE
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
    # RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("RANDOM FOREST TRAINING COMPLETE")
    print("=" * 60)

    print("\nModel saved:")
    print(MODEL_PATH)

    print("\nScaler saved:")
    print(SCALER_PATH)

    print("\nModel configuration:")
    print("Algorithm: Random Forest Classifier")
    print("Trees: 300")
    print("Maximum depth: 12")
    print("Minimum samples per leaf: 10")
    print("Class weight: balanced")
    print("Random state: 42")

    print("\nFeatures used:")

    for number, feature in enumerate(
        FEATURE_COLUMNS,
        start=1
    ):
        print(f"{number}. {feature}")

    print("\nNext step:")
    print("Test the Random Forest on the unseen test dataset.")

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()