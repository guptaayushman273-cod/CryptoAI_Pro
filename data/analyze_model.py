import os

import joblib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "models",
    "logistic_regression_model.pkl"
)


# ============================================================
# FEATURES
# Must exactly match train_model.py
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
    print("CRYPTOAI PRO - V3 STEP 10 MODEL DIAGNOSIS")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    print("\nLoading trained Logistic Regression model...")

    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

    # --------------------------------------------------------
    # GET COEFFICIENTS
    # --------------------------------------------------------

    coefficients = model.coef_[0]

    if len(coefficients) != len(FEATURE_COLUMNS):
        raise ValueError(
            "Number of model coefficients does not match "
            "number of features."
        )

    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    results = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "coefficient": coefficients
    })

    results["absolute_coefficient"] = (
        results["coefficient"].abs()
    )

    # --------------------------------------------------------
    # SORT BY IMPORTANCE
    # --------------------------------------------------------

    results = results.sort_values(
        "absolute_coefficient",
        ascending=False
    )

    results.reset_index(drop=True, inplace=True)

    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    print("\nFeature importance:")
    print("-" * 60)

    for index, row in results.iterrows():

        direction = (
            "POSITIVE"
            if row["coefficient"] > 0
            else "NEGATIVE"
        )

        print(
            f"{index + 1:2}. "
            f"{row['feature']:<28} "
            f"{row['coefficient']:>10.6f} "
            f"{direction}"
        )

    # --------------------------------------------------------
    # TOP POSITIVE FEATURES
    # --------------------------------------------------------

    positive = results[
        results["coefficient"] > 0
    ].sort_values(
        "coefficient",
        ascending=False
    )

    print("\n" + "=" * 60)
    print("TOP POSITIVE FEATURES")
    print("=" * 60)

    for index, row in positive.head(5).iterrows():

        print(
            f"{row['feature']:<28} "
            f"{row['coefficient']:>10.6f}"
        )

    # --------------------------------------------------------
    # TOP NEGATIVE FEATURES
    # --------------------------------------------------------

    negative = results[
        results["coefficient"] < 0
    ].sort_values(
        "coefficient",
        ascending=True
    )

    print("\n" + "=" * 60)
    print("TOP NEGATIVE FEATURES")
    print("=" * 60)

    for index, row in negative.head(5).iterrows():

        print(
            f"{row['feature']:<28} "
            f"{row['coefficient']:>10.6f}"
        )

    # --------------------------------------------------------
    # LOW-INFLUENCE FEATURES
    # --------------------------------------------------------

    low_influence = results[
        results["absolute_coefficient"] < 0.05
    ]

    print("\n" + "=" * 60)
    print("LOW-INFLUENCE FEATURES")
    print("=" * 60)

    if low_influence.empty:

        print("No features below coefficient threshold.")

    else:

        for index, row in low_influence.iterrows():

            print(
                f"{row['feature']:<28} "
                f"{row['coefficient']:>10.6f}"
            )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("MODEL DIAGNOSIS SUMMARY")
    print("=" * 60)

    print(
        f"\nTotal features: {len(FEATURE_COLUMNS)}"
    )

    print(
        f"Positive features: {len(positive)}"
    )

    print(
        f"Negative features: {len(negative)}"
    )

    print(
        f"Low-influence features: {len(low_influence)}"
    )

    print("\nDiagnosis completed.")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()