import json
import os

from collections import Counter


INPUT_FILE = "data/candles/ml_dataset.json"

TRAIN_FILE = "data/candles/ml_train.json"
TEST_FILE = "data/candles/ml_test.json"

TRAIN_RATIO = 0.80

COINS = [
    "BTCUSDT",
    "ETHUSDT",
    "LSKUSDT"
]


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


def load_dataset():
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def validate_dataset(data):

    print()
    print("VALIDATING DATASET")
    print("-" * 50)

    if not data:
        raise ValueError(
            "Dataset is empty."
        )

    required_columns = (
        ["coin", "time", "target"]
        + FEATURE_COLUMNS
    )

    for index, row in enumerate(data):

        for column in required_columns:

            if column not in row:

                raise ValueError(
                    f"Missing column '{column}' "
                    f"at row {index}"
                )

    print(
        f"Rows validated: {len(data)}"
    )

    print(
        f"Features: {len(FEATURE_COLUMNS)}"
    )

    print("Dataset validation passed.")


def split_coin_data(coin_data):

    # Make sure the data is chronological.
    coin_data = sorted(
        coin_data,
        key=lambda row: row["time"]
    )

    total = len(coin_data)

    train_size = int(
        total * TRAIN_RATIO
    )

    train_data = coin_data[:train_size]

    test_data = coin_data[train_size:]

    return train_data, test_data


def print_target_distribution(
    name,
    data
):

    targets = [
        row["target"]
        for row in data
    ]

    counts = Counter(targets)

    target_0 = counts.get(0, 0)
    target_1 = counts.get(1, 0)

    total = len(data)

    print()
    print(name)
    print("-" * 50)

    print(
        f"Rows: {total}"
    )

    print(
        f"Target 0: {target_0}"
    )

    print(
        f"Target 1: {target_1}"
    )

    if total > 0:

        print(
            f"Target 0 %: "
            f"{target_0 / total * 100:.2f}%"
        )

        print(
            f"Target 1 %: "
            f"{target_1 / total * 100:.2f}%"
        )


def save_json(
    filename,
    data
):

    directory = os.path.dirname(
        filename
    )

    os.makedirs(
        directory,
        exist_ok=True
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


def main():

    print()
    print("=" * 60)
    print("CRYPTOAI PRO - STEP 14C")
    print("CHRONOLOGICAL ML TRAIN / TEST SPLIT")
    print("=" * 60)

    print()
    print(
        f"Training ratio: "
        f"{TRAIN_RATIO * 100:.0f}%"
    )

    print(
        f"Testing ratio: "
        f"{(1 - TRAIN_RATIO) * 100:.0f}%"
    )

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    data = load_dataset()

    print()
    print(
        f"Loaded rows: {len(data)}"
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_dataset(data)

    # --------------------------------------------------------
    # Group by coin
    # --------------------------------------------------------

    train_data = []
    test_data = []

    print()
    print("COIN SPLITS")
    print("-" * 50)

    for coin in COINS:

        coin_data = [
            row
            for row in data
            if row["coin"] == coin
        ]

        if not coin_data:

            print(
                f"{coin}: NO DATA"
            )

            continue

        coin_train, coin_test = (
            split_coin_data(coin_data)
        )

        train_data.extend(
            coin_train
        )

        test_data.extend(
            coin_test
        )

        print(
            f"{coin}: "
            f"{len(coin_data)} total → "
            f"{len(coin_train)} train / "
            f"{len(coin_test)} test"
        )

    # --------------------------------------------------------
    # Keep chronological order
    # --------------------------------------------------------

    train_data.sort(
        key=lambda row: (
            row["time"],
            row["coin"]
        )
    )

    test_data.sort(
        key=lambda row: (
            row["time"],
            row["coin"]
        )
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_json(
        TRAIN_FILE,
        train_data
    )

    save_json(
        TEST_FILE,
        test_data
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("TRAINING DATA")
    print("=" * 60)

    print_target_distribution(
        "TRAINING SET",
        train_data
    )

    print()
    print("=" * 60)
    print("TEST DATA")
    print("=" * 60)

    print_target_distribution(
        "TEST SET",
        test_data
    )

    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("STEP 14C COMPLETE")
    print("=" * 60)

    print(
        f"Training rows: "
        f"{len(train_data)}"
    )

    print(
        f"Testing rows: "
        f"{len(test_data)}"
    )

    print()
    print(
        f"Training file: "
        f"{TRAIN_FILE}"
    )

    print(
        f"Testing file: "
        f"{TEST_FILE}"
    )

    print()
    print(
        "Chronological train/test split "
        "completed successfully."
    )


if __name__ == "__main__":
    main()