import json
import os

import numpy as np
import pandas as pd


DATASET_PATH = os.path.join(
    "data",
    "candles",
    "ml_dataset.json"
)

FUTURE_HORIZON = 5


def load_dataset():
    if not os.path.exists(DATASET_PATH):
        print("ERROR: Dataset not found.")
        print(f"Expected file: {DATASET_PATH}")
        return None

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return pd.DataFrame(data)


def analyze_returns(df):
    print("=" * 60)
    print("CRYPTOAI PRO - TARGET RETURN ANALYSIS")
    print("=" * 60)

    print(f"Dataset rows: {len(df)}")
    print(f"Future horizon: {FUTURE_HORIZON} candles")
    print()

    required_columns = ["coin", "close"]

    for column in required_columns:
        if column not in df.columns:
            print(f"ERROR: Missing column: {column}")
            return

    df = df.sort_values(["coin", "time"]).reset_index(drop=True)

    df["future_close"] = (
        df.groupby("coin")["close"]
        .shift(-FUTURE_HORIZON)
    )

    df["future_return_5"] = (
        (df["future_close"] - df["close"])
        / df["close"]
        * 100
    )

    returns = df["future_return_5"].dropna()

    if returns.empty:
        print("ERROR: No future returns could be calculated.")
        return

    print("OVERALL FUTURE RETURN")
    print("-" * 60)

    print(f"Mean:   {returns.mean():.4f}%")
    print(f"Median: {returns.median():.4f}%")
    print(f"Std:    {returns.std():.4f}%")
    print(f"Min:    {returns.min():.4f}%")
    print(f"Max:    {returns.max():.4f}%")
    print()

    positive_thresholds = [
        0.05,
        0.10,
        0.20,
        0.30,
        0.50,
        1.00
    ]

    print("PERCENTAGE ABOVE POSITIVE THRESHOLDS")
    print("-" * 60)

    for threshold in positive_thresholds:
        percentage = (
            (returns > threshold).mean()
            * 100
        )

        print(
            f">{threshold:>4.2f}% : "
            f"{percentage:>6.2f}%"
        )

    print()

    negative_thresholds = [
        -0.05,
        -0.10,
        -0.20,
        -0.30,
        -0.50,
        -1.00
    ]

    print("PERCENTAGE BELOW NEGATIVE THRESHOLDS")
    print("-" * 60)

    for threshold in negative_thresholds:
        percentage = (
            (returns < threshold).mean()
            * 100
        )

        print(
            f"<{threshold:>5.2f}% : "
            f"{percentage:>6.2f}%"
        )

    print()

    print("RETURN DISTRIBUTION")
    print("-" * 60)

    bins = [
        -np.inf,
        -1.0,
        -0.5,
        -0.3,
        -0.2,
        -0.1,
        -0.05,
        0,
        0.05,
        0.1,
        0.2,
        0.3,
        0.5,
        1.0,
        np.inf
    ]

    labels = [
        "< -1.00%",
        "-1.00 to -0.50%",
        "-0.50 to -0.30%",
        "-0.30 to -0.20%",
        "-0.20 to -0.10%",
        "-0.10 to -0.05%",
        "-0.05 to 0%",
        "0 to 0.05%",
        "0.05 to 0.10%",
        "0.10 to 0.20%",
        "0.20 to 0.30%",
        "0.30 to 0.50%",
        "0.50 to 1.00%",
        "> 1.00%"
    ]

    distribution = pd.cut(
        returns,
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    distribution_counts = (
        distribution
        .value_counts(sort=False)
    )

    total = len(returns)

    for label, count in distribution_counts.items():
        percentage = count / total * 100

        print(
            f"{str(label):<20} "
            f"{count:>6} rows "
            f"({percentage:>6.2f}%)"
        )

    print()

    print("RETURN STATISTICS BY COIN")
    print("-" * 60)

    for coin, group in df.groupby("coin"):
        coin_returns = (
            group["future_return_5"]
            .dropna()
        )

        if coin_returns.empty:
            continue

        print(f"\n{coin}")
        print(f"Rows:   {len(coin_returns)}")
        print(f"Mean:   {coin_returns.mean():.4f}%")
        print(f"Median: {coin_returns.median():.4f}%")
        print(f"Std:    {coin_returns.std():.4f}%")
        print(f"Min:    {coin_returns.min():.4f}%")
        print(f"Max:    {coin_returns.max():.4f}%")

        above_05 = (
            (coin_returns > 0.50).mean()
            * 100
        )

        below_05 = (
            (coin_returns < -0.50).mean()
            * 100
        )

        print(f"> +0.50%: {above_05:.2f}%")
        print(f"< -0.50%: {below_05:.2f}%")

    print()
    print("=" * 60)
    print("TARGET RETURN ANALYSIS COMPLETE")
    print("=" * 60)


def main():
    df = load_dataset()

    if df is None:
        return

    analyze_returns(df)


if __name__ == "__main__":
    main()