import json
import math
import os

import pandas as pd


# --------------------------------------------------
# PATH
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "candles",
    "ml_dataset.json"
)


# --------------------------------------------------
# EXPECTED FEATURES
# --------------------------------------------------

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


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def validate_dataset():

    print("=" * 60)
    print("CRYPTOAI PRO - V3 DATASET VALIDATION")
    print("=" * 60)

    # ----------------------------------------------
    # Load dataset
    # ----------------------------------------------

    print("\nLoading dataset...")

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    print(f"Total rows: {len(data)}")

    if not data:
        print("\nERROR: Dataset is empty.")
        return

    df = pd.DataFrame(data)

    # ----------------------------------------------
    # Check columns
    # ----------------------------------------------

    print("\nChecking columns...")

    required_columns = [
        "coin",
        "time",
        "future_close",
        "target"
    ] + FEATURE_COLUMNS

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print("MISSING COLUMNS:")
        for column in missing_columns:
            print(f"- {column}")

        return

    print("All required columns present.")

    # ----------------------------------------------
    # Check missing values
    # ----------------------------------------------

    print("\nChecking missing values...")

    missing_values = df[
        required_columns
    ].isnull().sum().sum()

    print(
        f"Missing values: {missing_values}"
    )

    # ----------------------------------------------
    # Check invalid numbers
    # ----------------------------------------------

    print("\nChecking invalid numbers...")

    numeric_columns = [
        "time",
        "future_close"
    ] + FEATURE_COLUMNS

    invalid_numbers = 0

    for column in numeric_columns:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid_numbers += (
            ~values.map(
                lambda value:
                math.isfinite(value)
                if pd.notna(value)
                else False
            )
        ).sum()

    print(
        f"Invalid numbers: {invalid_numbers}"
    )

    # ----------------------------------------------
    # Check targets
    # ----------------------------------------------

    print("\nChecking targets...")

    valid_targets = {0, 1}

    invalid_targets = df[
        ~df["target"].isin(valid_targets)
    ]

    print(
        f"Invalid targets: "
        f"{len(invalid_targets)}"
    )

    target_counts = (
        df["target"]
        .value_counts()
        .sort_index()
    )

    print("\nTarget distribution:")

    for target, count in target_counts.items():

        print(
            f"Target {target}: {count}"
        )

    # ----------------------------------------------
    # Check duplicate coin/time
    # ----------------------------------------------

    print(
        "\nChecking duplicate coin/time records..."
    )

    duplicates = df.duplicated(
        subset=[
            "coin",
            "time"
        ]
    ).sum()

    print(
        f"Duplicate records: {duplicates}"
    )

    # ----------------------------------------------
    # Rows per coin
    # ----------------------------------------------

    print("\nRows per coin:")

    rows_per_coin = (
        df["coin"]
        .value_counts()
        .sort_index()
    )

    for coin, count in rows_per_coin.items():

        print(
            f"{coin}: {count}"
        )

    # ----------------------------------------------
    # Feature statistics
    # ----------------------------------------------

    print("\nFeature range check:")

    for column in FEATURE_COLUMNS:

        minimum = df[column].min()
        maximum = df[column].max()

        print(
            f"{column:<28} "
            f"min={minimum:.6f} "
            f"max={maximum:.6f}"
        )

    # ----------------------------------------------
    # Final result
    # ----------------------------------------------

    print("\n" + "=" * 60)

    if (
        missing_values == 0
        and invalid_numbers == 0
        and len(invalid_targets) == 0
        and duplicates == 0
    ):

        print("DATASET VALIDATION PASSED")
        print("=" * 60)

        print("\nThe dataset is ready for train/test preparation.")

    else:

        print("DATASET VALIDATION FAILED")
        print("=" * 60)

        print("\nFix the problems above before training.")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    validate_dataset()