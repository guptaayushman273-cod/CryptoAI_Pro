import json
import os

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TEST_DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "candles",
    "test_dataset.json"
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "models",
    "random_forest_model.pkl"
)

SCALER_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "models",
    "random_forest_scaler.pkl"
)


FEATURES = [
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


def load_test_data():
    print("Loading unseen test dataset...")

    with open(TEST_DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    df = pd.DataFrame(data)

    print(f"Test rows: {len(df)}")

    return df


def validate_data(df):
    print()
    print("Validating test data...")

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

    if "target" not in df.columns:
        raise ValueError(
            "Target column is missing."
        )

    if df[FEATURES].isnull().any().any():
        raise ValueError(
            "Test dataset contains missing feature values."
        )

    if df["target"].isnull().any():
        raise ValueError(
            "Test dataset contains missing target values."
        )

    print(f"Features available: {len(FEATURES)}")
    print("Validation successful.")


def main():
    print("=" * 60)
    print("CRYPTOAI PRO - V3 STEP 12 RANDOM FOREST TEST")
    print("=" * 60)

    df = load_test_data()

    validate_data(df)

    print()
    print("Loading Random Forest model...")

    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

    print()
    print("Loading feature scaler...")

    scaler = joblib.load(SCALER_PATH)

    print("Scaler loaded successfully.")

    X_test = df[FEATURES]
    y_test = df["target"]

    print()
    print("Preparing test features...")

    X_test_scaled = scaler.transform(X_test)

    print("Test features prepared.")

    print()
    print("Making predictions...")

    predictions = model.predict(X_test_scaled)

    print("Predictions complete.")

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print()
    print("=" * 60)
    print("RANDOM FOREST TEST RESULTS")
    print("=" * 60)

    print()
    print(f"Test accuracy: {accuracy * 100:.2f}%")

    print()
    print("Classification report:")

    print(
        classification_report(
            y_test,
            predictions,
            digits=4
        )
    )

    print("Confusion matrix:")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    print()
    print("Prediction distribution:")

    prediction_distribution = pd.Series(
        predictions
    ).value_counts().sort_index()

    for target_value, count in prediction_distribution.items():
        print(
            f"Predicted {target_value}: {count}"
        )

    print()
    print("Actual target distribution:")

    actual_distribution = y_test.value_counts().sort_index()

    for target_value, count in actual_distribution.items():
        print(
            f"Actual {target_value}: {count}"
        )

    print()
    print("Features used:")

    for index, feature in enumerate(FEATURES, start=1):
        print(f"{index}. {feature}")

    print()
    print("=" * 60)
    print("RANDOM FOREST TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()