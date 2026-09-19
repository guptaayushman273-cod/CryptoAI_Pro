import os

import joblib
import numpy as np
import pandas as pd


# ============================================================
# CRYPTOAI PRO - ML PREDICTOR
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
    "random_forest_model.pkl"
)

SCALER_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "models",
    "random_forest_scaler.pkl"
)


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


_model = None
_scaler = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_ml_model():

    global _model
    global _scaler

    if (
        _model is not None
        and
        _scaler is not None
    ):

        return _model, _scaler

    if not os.path.exists(
        MODEL_PATH
    ):

        raise FileNotFoundError(
            f"ML model not found: "
            f"{MODEL_PATH}"
        )

    if not os.path.exists(
        SCALER_PATH
    ):

        raise FileNotFoundError(
            f"ML scaler not found: "
            f"{SCALER_PATH}"
        )

    _model = joblib.load(
        MODEL_PATH
    )

    _scaler = joblib.load(
        SCALER_PATH
    )

    return _model, _scaler


# ============================================================
# BUILD LIVE ML FEATURES
# ============================================================

def build_live_features(
    indicators
):

    if (
        indicators is None
        or
        len(indicators) < 51
    ):

        raise ValueError(
            "Not enough indicator data "
            "for ML prediction."
        )

    df = indicators.copy()

    # --------------------------------------------------------
    # RETURNS
    # --------------------------------------------------------

    df["return_1"] = (
        df["close"]
        .pct_change(1)
        * 100
    )

    df["return_5"] = (
        df["close"]
        .pct_change(5)
        * 100
    )

    df["return_10"] = (
        df["close"]
        .pct_change(10)
        * 100
    )

    # --------------------------------------------------------
    # EMA RELATIONSHIPS
    # --------------------------------------------------------

    df["price_vs_ema20"] = (
        (
            df["close"]
            - df["EMA20"]
        )
        /
        df["EMA20"]
    ) * 100

    df["price_vs_ema50"] = (
        (
            df["close"]
            - df["EMA50"]
        )
        /
        df["EMA50"]
    ) * 100

    df["ema20_vs_ema50"] = (
        (
            df["EMA20"]
            - df["EMA50"]
        )
        /
        df["EMA50"]
    ) * 100

    # --------------------------------------------------------
    # MACD FEATURES
    # --------------------------------------------------------

    df["macd_relative"] = (
        df["MACD"]
        /
        df["close"]
    ) * 100

    df["macd_signal_diff"] = (
        df["MACD"]
        -
        df["MACD_SIGNAL"]
    )

    df[
        "macd_signal_diff_percent"
    ] = (
        (
            df["MACD"]
            -
            df["MACD_SIGNAL"]
        )
        /
        df["close"]
    ) * 100

    # --------------------------------------------------------
    # BOLLINGER FEATURES
    # --------------------------------------------------------

    band_range = (
        df["BB_UPPER"]
        -
        df["BB_LOWER"]
    )

    safe_band_range = (
        band_range.replace(
            0,
            np.nan
        )
    )

    df["bb_position"] = (
        (
            df["close"]
            -
            df["BB_LOWER"]
        )
        /
        safe_band_range
    )

    df["bb_width"] = (
        band_range
        /
        df["close"]
    ) * 100

    # --------------------------------------------------------
    # ATR
    # --------------------------------------------------------

    df["atr_percent"] = (
        df["ATR"]
        /
        df["close"]
    ) * 100

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    df["volume_change"] = (
        df["volume"]
        .pct_change()
        * 100
    )

    # --------------------------------------------------------
    # CLEAN
    # --------------------------------------------------------

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    latest = df.iloc[-1]

    missing = [
        feature
        for feature in FEATURE_COLUMNS
        if (
            feature not in latest.index
            or
            pd.isna(
                latest[feature]
            )
        )
    ]

    if missing:

        raise ValueError(
            "Invalid live ML features: "
            f"{missing}"
        )

    feature_values = {

        feature:
            float(
                latest[feature]
            )

        for feature
        in FEATURE_COLUMNS
    }

    return feature_values


# ============================================================
# PREDICT
# ============================================================

def predict_probability(
    indicators
):

    model, scaler = (
        load_ml_model()
    )

    features = (
        build_live_features(
            indicators
        )
    )

    feature_frame = pd.DataFrame(
        [
            features
        ],
        columns=FEATURE_COLUMNS
    )

    scaled_features = (
        scaler.transform(
            feature_frame
        )
    )

    probabilities = (
        model.predict_proba(
            scaled_features
        )[0]
    )

    positive_probability = float(
        probabilities[1]
    )

    prediction = int(
        positive_probability
        >= 0.50
    )

    return {

        "prediction":
            prediction,

        "probability":
            round(
                positive_probability,
                6
            ),

        "confidence_percent":
            round(
                positive_probability
                * 100,
                2
            ),

        "target_description":
            (
                "Future 5-candle return "
                "> +0.20%"
            )
    }