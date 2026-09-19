import pandas as pd

from ta.momentum import RSIIndicator

from ta.trend import EMAIndicator
from ta.trend import MACD

from ta.volatility import BollingerBands
from ta.volatility import AverageTrueRange


def calculate_indicators(candles):

    """
    Converts candle data into a DataFrame
    and calculates technical indicators.
    """

    if len(candles) == 0:

        return None

    rows = []

    for candle in candles:

        rows.append({

            "time": candle["time"],

            "open": float(candle["open"]),

            "high": float(candle["high"]),

            "low": float(candle["low"]),

            "close": float(candle["close"]),

            "volume": float(candle["volume"])

        })

    df = pd.DataFrame(rows)

    df = df.sort_values("time")

    df.reset_index(drop=True, inplace=True)

    # ============================
    # RSI
    # ============================

    df["RSI"] = RSIIndicator(
        close=df["close"],
        window=14
    ).rsi()

    # ============================
    # EMA
    # ============================

    df["EMA20"] = EMAIndicator(
        close=df["close"],
        window=20
    ).ema_indicator()

    df["EMA50"] = EMAIndicator(
        close=df["close"],
        window=50
    ).ema_indicator()

    # ============================
    # MACD
    # ============================

    macd = MACD(df["close"])

    df["MACD"] = macd.macd()

    df["MACD_SIGNAL"] = macd.macd_signal()

    # ============================
    # Bollinger Bands
    # ============================

    bb = BollingerBands(df["close"])

    df["BB_UPPER"] = bb.bollinger_hband()

    df["BB_LOWER"] = bb.bollinger_lband()

    # ============================
    # ATR
    # ============================

    atr = AverageTrueRange(

        high=df["high"],

        low=df["low"],

        close=df["close"]

    )

    df["ATR"] = atr.average_true_range()

    return df
