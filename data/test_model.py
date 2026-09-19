import json
import os

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TEST_DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "candles",
    "ml_test.json"
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
    print("CRYPTOAI PRO - V3 STEP 14E")
    print("RANDOM FOREST TEST EVALUATION")
    print("=" * 60)

    # --------------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------------

    if not os.path.exists(TEST_DATA_PATH):

        raise FileNotFoundError(
            f"Test dataset not found: "
            f"{TEST_DATA_PATH}"
        )

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            f"Model not found: "
            f"{MODEL_PATH}"
        )

    if not os.path.exists(SCALER_PATH):

        raise FileNotFoundError(
            f"Scaler not found: "
            f"{SCALER_PATH}"
        )

    # --------------------------------------------------------
    # LOAD TEST DATA
    # --------------------------------------------------------

    print("\nLoading unseen test dataset...")

    print(TEST_DATA_PATH)

    with open(
        TEST_DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not data:

        raise ValueError(
            "Test dataset is empty."
        )

    df = pd.DataFrame(data)

    print(
        f"\nTest rows: {len(df)}"
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print("\nValidating test dataset...")

    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            f"Missing features: "
            f"{missing_features}"
        )

    if "target" not in df.columns:

        raise ValueError(
            "Target column not found."
        )

    if df[FEATURE_COLUMNS].isnull().any().any():

        raise ValueError(
            "Test features contain missing values."
        )

    print(
        f"Features available: "
        f"{len(FEATURE_COLUMNS)}"
    )

    # --------------------------------------------------------
    # TARGET DISTRIBUTION
    # --------------------------------------------------------

    print("\nTest target distribution:")
    print("-" * 40)

    target_counts = (
        df["target"]
        .value_counts()
        .sort_index()
    )

    print(
        target_counts.to_string()
    )

    total = len(df)

    for target_value in [0, 1]:

        count = int(
            target_counts.get(
                target_value,
                0
            )
        )

        percentage = (
            count / total * 100
        )

        print(
            f"Target {target_value}: "
            f"{count} "
            f"({percentage:.2f}%)"
        )

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    print("\nLoading trained model...")

    model = joblib.load(
        MODEL_PATH
    )

    scaler = joblib.load(
        SCALER_PATH
    )

    print(
        "Model and scaler loaded."
    )

    # --------------------------------------------------------
    # PREPARE TEST FEATURES
    # --------------------------------------------------------

    X_test = df[
        FEATURE_COLUMNS
    ].copy()

    y_test = df[
        "target"
    ].astype(int)

    X_scaled = scaler.transform(
        X_test
    )

    # --------------------------------------------------------
    # PREDICTIONS
    # --------------------------------------------------------

    print(
        "\nRunning predictions..."
    )

    predictions = model.predict(
        X_scaled
    )

    probabilities = (
        model.predict_proba(
            X_scaled
        )[:, 1]
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    auc = roc_auc_score(
        y_test,
        probabilities
    )

    matrix = confusion_matrix(
        y_test,
        predictions
    )

    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------

    majority_class_accuracy = (
        y_test.value_counts().max()
        / len(y_test)
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("UNSEEN TEST PERFORMANCE")
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
        f"\nMajority-class baseline accuracy: "
        f"{majority_class_accuracy * 100:.2f}%"
    )

    print(
        "\nConfusion Matrix:"
    )

    print(matrix)

    tn, fp, fn, tp = matrix.ravel()

    print()
    print(
        f"True Negatives : {tn}"
    )

    print(
        f"False Positives: {fp}"
    )

    print(
        f"False Negatives: {fn}"
    )

    print(
        f"True Positives  : {tp}"
    )

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
            zero_division=0
        )
    )

    # --------------------------------------------------------
    # PROBABILITY ANALYSIS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("AI CONFIDENCE ANALYSIS")
    print("=" * 60)

    thresholds = [
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75
    ]

    print()
    print(
        "Threshold | Signals | Precision | Recall | F1"
    )

    print(
        "-" * 55
    )

    for threshold in thresholds:

        threshold_predictions = (
            probabilities >= threshold
        ).astype(int)

        signal_count = int(
            threshold_predictions.sum()
        )

        threshold_precision = (
            precision_score(
                y_test,
                threshold_predictions,
                zero_division=0
            )
        )

        threshold_recall = (
            recall_score(
                y_test,
                threshold_predictions,
                zero_division=0
            )
        )

        threshold_f1 = (
            f1_score(
                y_test,
                threshold_predictions,
                zero_division=0
            )
        )

        print(
            f"{threshold:9.2f} | "
            f"{signal_count:7d} | "
            f"{threshold_precision * 100:8.2f}% | "
            f"{threshold_recall * 100:6.2f}% | "
            f"{threshold_f1 * 100:6.2f}%"
        )

    # --------------------------------------------------------
    # COIN-BY-COIN ANALYSIS
    # --------------------------------------------------------

    if "coin" in df.columns:

        print()
        print("=" * 60)
        print("COIN-BY-COIN PERFORMANCE")
        print("=" * 60)

        result_df = df[
            ["coin"]
        ].copy()

        result_df[
            "target"
        ] = y_test.values

        result_df[
            "prediction"
        ] = predictions

        result_df[
            "probability"
        ] = probabilities

        for coin in sorted(
            result_df["coin"].unique()
        ):

            coin_df = result_df[
                result_df["coin"] == coin
            ]

            coin_accuracy = accuracy_score(
                coin_df["target"],
                coin_df["prediction"]
            )

            coin_precision = precision_score(
                coin_df["target"],
                coin_df["prediction"],
                zero_division=0
            )

            coin_recall = recall_score(
                coin_df["target"],
                coin_df["prediction"],
                zero_division=0
            )

            coin_f1 = f1_score(
                coin_df["target"],
                coin_df["prediction"],
                zero_division=0
            )

            try:

                coin_auc = roc_auc_score(
                    coin_df["target"],
                    coin_df["probability"]
                )

            except ValueError:

                coin_auc = 0.0

            print()
            print(coin)

            print(
                f"  Rows      : "
                f"{len(coin_df)}"
            )

            print(
                f"  Accuracy  : "
                f"{coin_accuracy * 100:.2f}%"
            )

            print(
                f"  Precision : "
                f"{coin_precision * 100:.2f}%"
            )

            print(
                f"  Recall    : "
                f"{coin_recall * 100:.2f}%"
            )

            print(
                f"  F1        : "
                f"{coin_f1 * 100:.2f}%"
            )

            print(
                f"  ROC-AUC   : "
                f"{coin_auc:.4f}"
            )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 14E COMPLETE")
    print("=" * 60)

    print(
        "Random Forest evaluated on "
        "unseen chronological data."
    )

    print()
    print(
        "Target = 1 means:"
    )

    print(
        "Future 5-candle return > +0.20%"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()