import json
import os

import numpy as np
import pandas as pd

from api.coindcx_api import get_historical_candles
from indicators.indicators import calculate_indicators


# ============================================================
# CRYPTOAI PRO - ML DATASET BUILDER
# ============================================================

COINS = [
    "BTCUSDT",
    "ETHUSDT",
    "LSKUSDT"
]

INTERVAL = "1m"
CANDLE_LIMIT = 5000

# Predict price movement 5 candles into the future.
FUTURE_HORIZON = 5

# New meaningful target threshold.
# Target = 1 only when future return is greater than +0.20%.
TARGET_THRESHOLD_PERCENT = 0.20

OUTPUT_FILE = os.path.join(
    "data",
    "candles",
    "ml_dataset.json"
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def build_features(df):
    """
    Build the 19 engineered ML features used by CryptoAI Pro.
    """

    data = df.copy()

    # --------------------------------------------------------
    # Returns
    # --------------------------------------------------------

    data["return_1"] = (
        data["close"].pct_change(1) * 100
    )

    data["return_5"] = (
        data["close"].pct_change(5) * 100
    )

    data["return_10"] = (
        data["close"].pct_change(10) * 100
    )

    # --------------------------------------------------------
    # Price relative to EMA
    # --------------------------------------------------------

    data["price_vs_ema20"] = (
        (data["close"] - data["EMA20"])
        / data["EMA20"]
    ) * 100

    data["price_vs_ema50"] = (
        (data["close"] - data["EMA50"])
        / data["EMA50"]
    ) * 100

    data["ema20_vs_ema50"] = (
        (data["EMA20"] - data["EMA50"])
        / data["EMA50"]
    ) * 100

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    data["macd_relative"] = (
        data["MACD"] / data["close"]
    ) * 100

    data["macd_signal_diff"] = (
        data["MACD"] - data["MACD_SIGNAL"]
    )

    data["macd_signal_diff_percent"] = (
        (data["MACD"] - data["MACD_SIGNAL"])
        / data["close"]
    ) * 100

    # --------------------------------------------------------
    # Bollinger Bands
    # --------------------------------------------------------

    band_range = (
        data["BB_UPPER"] - data["BB_LOWER"]
    )

    data["bb_position"] = (
        (data["close"] - data["BB_LOWER"])
        / band_range.replace(0, np.nan)
    )

    data["bb_width"] = (
        band_range / data["close"]
    ) * 100

    # --------------------------------------------------------
    # ATR
    # --------------------------------------------------------

    data["atr_percent"] = (
        data["ATR"] / data["close"]
    ) * 100

    # --------------------------------------------------------
    # Volume change
    # --------------------------------------------------------

    data["volume_change"] = (
        data["volume"].pct_change() * 100
    )

    return data


# ============================================================
# BUILD DATASET FOR ONE COIN
# ============================================================

def build_coin_dataset(coin):
    print()
    print("=" * 60)
    print(f"Downloading {CANDLE_LIMIT} candles for {coin}...")
    print("=" * 60)

    candles = get_historical_candles(
        coin,
        interval=INTERVAL,
        total_limit=CANDLE_LIMIT
    )

    if not candles:
        print(f"No candles received for {coin}.")
        return []

    print(f"Downloaded {len(candles)} candles.")

    # --------------------------------------------------------
    # Calculate technical indicators
    # --------------------------------------------------------

    indicators = calculate_indicators(candles)

    if indicators is None or indicators.empty:
        print(f"Indicator calculation failed for {coin}.")
        return []

    df = indicators.copy()

    # Make sure data is chronological.
    df = df.sort_values("time").reset_index(drop=True)

    # --------------------------------------------------------
    # Create future close
    # --------------------------------------------------------

    df["future_close"] = (
        df["close"].shift(-FUTURE_HORIZON)
    )

    # --------------------------------------------------------
    # Future return
    # --------------------------------------------------------

    df["future_return"] = (
        (
            (df["future_close"] - df["close"])
            / df["close"]
        ) * 100
    )

    # --------------------------------------------------------
    # New target
    #
    # 1 = future return > +0.20%
    # 0 = otherwise
    # --------------------------------------------------------

    df["target"] = (
        df["future_return"]
        > TARGET_THRESHOLD_PERCENT
    ).astype(int)

    # --------------------------------------------------------
    # Build engineered features
    # --------------------------------------------------------

    df = build_features(df)

    # --------------------------------------------------------
    # Select the final ML features
    # --------------------------------------------------------

    feature_columns = [
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

    # --------------------------------------------------------
    # Remove rows that cannot be used
    # --------------------------------------------------------

    required_columns = (
        ["time", "future_return", "target"]
        + feature_columns
    )

    df = df.dropna(
        subset=required_columns
    ).copy()

    # Remove infinite values caused by percentage calculations.
    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    df = df.dropna(
        subset=required_columns
    ).copy()

    # --------------------------------------------------------
    # Remove final rows without a real future candle.
    # --------------------------------------------------------

    # This is normally already handled by dropna(future_return),
    # but we explicitly keep only rows with valid future data.
    df = df[
        df["future_close"].notna()
    ].copy()

    # --------------------------------------------------------
    # Convert rows into JSON-friendly dictionaries
    # --------------------------------------------------------

    records = []

    for _, row in df.iterrows():

        record = {
            "coin": coin,
            "time": row["time"],

            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row["volume"]),

            "RSI": float(row["RSI"]),

            "return_1": float(row["return_1"]),
            "return_5": float(row["return_5"]),
            "return_10": float(row["return_10"]),

            "price_vs_ema20": float(
                row["price_vs_ema20"]
            ),

            "price_vs_ema50": float(
                row["price_vs_ema50"]
            ),

            "ema20_vs_ema50": float(
                row["ema20_vs_ema50"]
            ),

            "macd_relative": float(
                row["macd_relative"]
            ),

            "macd_signal_diff": float(
                row["macd_signal_diff"]
            ),

            "macd_signal_diff_percent": float(
                row["macd_signal_diff_percent"]
            ),

            "bb_position": float(
                row["bb_position"]
            ),

            "bb_width": float(
                row["bb_width"]
            ),

            "atr_percent": float(
                row["atr_percent"]
            ),

            "volume_change": float(
                row["volume_change"]
            ),

            "future_return": float(
                row["future_return"]
            ),

            "target": int(row["target"])
        }

        records.append(record)

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    target_counts = (
        df["target"]
        .value_counts()
        .sort_index()
    )

    positive_count = int(
        target_counts.get(1, 0)
    )

    negative_count = int(
        target_counts.get(0, 0)
    )

    total_count = len(df)

    positive_percent = (
        positive_count / total_count * 100
        if total_count > 0
        else 0
    )

    print()
    print(f"{coin} DATASET")
    print("-" * 40)
    print(f"Usable rows: {total_count}")
    print(f"Target 0: {negative_count}")
    print(f"Target 1: {positive_count}")
    print(
        f"Target 1 percentage: "
        f"{positive_percent:.2f}%"
    )

    if total_count > 0:
        print(
            f"Future return mean: "
            f"{df['future_return'].mean():.4f}%"
        )

        print(
            f"Future return median: "
            f"{df['future_return'].median():.4f}%"
        )

    return records


# ============================================================
# MAIN DATASET BUILDER
# ============================================================

def main():

    print()
    print("=" * 60)
    print("CRYPTOAI PRO - STEP 14B")
    print("MEANINGFUL TARGET DATASET")
    print("=" * 60)

    print()
    print(f"Coins: {', '.join(COINS)}")
    print(f"Interval: {INTERVAL}")
    print(f"Candles per coin: {CANDLE_LIMIT}")
    print(f"Future horizon: {FUTURE_HORIZON} candles")
    print(
        f"Target threshold: "
        f"+{TARGET_THRESHOLD_PERCENT:.2f}%"
    )

    all_records = []

    # --------------------------------------------------------
    # Build each coin dataset
    # --------------------------------------------------------

    for coin in COINS:

        records = build_coin_dataset(coin)

        all_records.extend(records)

    # --------------------------------------------------------
    # Sort globally by time
    # --------------------------------------------------------

    all_records.sort(
        key=lambda x: (
            x["time"],
            x["coin"]
        )
    )

    # --------------------------------------------------------
    # Ensure output directory exists
    # --------------------------------------------------------

    output_directory = os.path.dirname(
        OUTPUT_FILE
    )

    os.makedirs(
        output_directory,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_records,
            file,
            indent=2
        )

    # --------------------------------------------------------
    # Final statistics
    # --------------------------------------------------------

    target_0 = sum(
        1
        for row in all_records
        if row["target"] == 0
    )

    target_1 = sum(
        1
        for row in all_records
        if row["target"] == 1
    )

    total = len(all_records)

    print()
    print("=" * 60)
    print("DATASET BUILD COMPLETE")
    print("=" * 60)

    print(f"Total rows: {total}")
    print(f"Target 0: {target_0}")
    print(f"Target 1: {target_1}")

    if total > 0:
        print(
            f"Target 0 percentage: "
            f"{target_0 / total * 100:.2f}%"
        )

        print(
            f"Target 1 percentage: "
            f"{target_1 / total * 100:.2f}%"
        )

    print()
    print(f"Output file: {OUTPUT_FILE}")

    print()
    print("Step 14B dataset generation completed.")


if __name__ == "__main__":
    main()