import json
import os

import joblib
import pandas as pd


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


def load_data():
    print("Loading test dataset...")

    with open(
        TEST_DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    return pd.DataFrame(data)


def main():
    print("=" * 60)
    print("CRYPTOAI PRO - V3 STEP 13")
    print("RANDOM FOREST DIAGNOSTIC ANALYSIS")
    print("=" * 60)

    df = load_data()

    print()
    print(f"Test rows: {len(df)}")

    print()
    print("Loading Random Forest model...")

    model = joblib.load(MODEL_PATH)

    print("Model loaded successfully.")

    print()
    print("=" * 60)
    print("FEATURE IMPORTANCE")
    print("=" * 60)

    importance = pd.DataFrame({
        "feature": FEATURES,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    importance = importance.reset_index(
        drop=True
    )

    for index, row in importance.iterrows():
        print(
            f"{index + 1:2}. "
            f"{row['feature']:<30} "
            f"{row['importance']:.6f}"
        )

    print()
    print("=" * 60)
    print("TOP 10 FEATURES")
    print("=" * 60)

    for index, row in importance.head(10).iterrows():
        print(
            f"{index + 1:2}. "
            f"{row['feature']:<30} "
            f"{row['importance']:.6f}"
        )

    print()
    print("=" * 60)
    print("LOW IMPORTANCE FEATURES")
    print("=" * 60)

    low_importance = importance[
        importance["importance"] < 0.02
    ]

    if low_importance.empty:
        print("No features below 0.02 importance.")
    else:
        for _, row in low_importance.iterrows():
            print(
                f"{row['feature']:<30} "
                f"{row['importance']:.6f}"
            )

    print()
    print("=" * 60)
    print("FEATURE IMPORTANCE SUMMARY")
    print("=" * 60)

    print(
        f"Highest importance: "
        f"{importance.iloc[0]['feature']} "
        f"({importance.iloc[0]['importance']:.6f})"
    )

    print(
        f"Lowest importance: "
        f"{importance.iloc[-1]['feature']} "
        f"({importance.iloc[-1]['importance']:.6f})"
    )

    print(
        f"Features below 0.02: "
        f"{len(low_importance)}"
    )

    print()
    print("=" * 60)
    print("COIN DISTRIBUTION")
    print("=" * 60)

    if "coin" in df.columns:
        coin_counts = df["coin"].value_counts()

        for coin, count in coin_counts.items():
            print(
                f"{coin:<15} {count} rows"
            )
    else:
        print(
            "Coin column is not present "
            "in the test dataset."
        )

    print()
    print("=" * 60)
    print("TARGET DISTRIBUTION BY COIN")
    print("=" * 60)

    if "coin" in df.columns:
        target_by_coin = pd.crosstab(
            df["coin"],
            df["target"]
        )

        print(target_by_coin)

    else:
        print(
            "Coin column is not present."
        )

    print()
    print("=" * 60)
    print("STEP 13 DIAGNOSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()