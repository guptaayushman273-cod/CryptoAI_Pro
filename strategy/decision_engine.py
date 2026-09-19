import pandas as pd


# ============================================================
# CRYPTOAI PRO - DECISION ENGINE
# ============================================================

BUY_SCORE_THRESHOLD = 110
WATCH_SCORE_THRESHOLD = 55

# Volatility filter
MAX_BUY_ATR_PERCENT = 2.0

# ML confidence settings
ML_STRONG_THRESHOLD = 0.65
ML_MODERATE_THRESHOLD = 0.55


# ============================================================
# MAIN DECISION FUNCTION
# ============================================================

def make_decision(
    market_score,
    news_score,
    fee_ok,
    indicators,
    ml_probability=None
):
    """
    CryptoAI Pro hybrid trading decision engine.

    Combines:
    - Market momentum
    - News sentiment
    - EMA trend
    - Price position
    - RSI
    - MACD
    - Bollinger Bands
    - ATR volatility
    - Machine-learning probability

    ML is used only as an additional confirmation.
    It cannot independently create a BUY signal.
    """

    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if not fee_ok:

        return {
            "decision": "SKIP 🔴",
            "score": 0,
            "technical_confirmations": 0,
            "ml_probability": ml_probability,
            "reason": [
                "Fees are too high."
            ]
        }

    if indicators is None or len(indicators) < 2:

        return {
            "decision": "SKIP 🔴",
            "score": 0,
            "technical_confirmations": 0,
            "ml_probability": ml_probability,
            "reason": [
                "Not enough indicator data."
            ]
        }

    required_columns = [
        "close",
        "RSI",
        "EMA20",
        "EMA50",
        "MACD",
        "MACD_SIGNAL",
        "BB_UPPER",
        "BB_LOWER",
        "ATR"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in indicators.columns
    ]

    if missing_columns:

        return {
            "decision": "SKIP 🔴",
            "score": 0,
            "technical_confirmations": 0,
            "ml_probability": ml_probability,
            "reason": [
                f"Missing indicators: {missing_columns}"
            ]
        }

    latest = indicators.iloc[-1]
    previous = indicators.iloc[-2]

    values_to_check = [
        latest["close"],
        latest["RSI"],
        latest["EMA20"],
        latest["EMA50"],
        latest["MACD"],
        latest["MACD_SIGNAL"],
        latest["BB_UPPER"],
        latest["BB_LOWER"],
        latest["ATR"]
    ]

    if any(
        pd.isna(value)
        for value in values_to_check
    ):

        return {
            "decision": "SKIP 🔴",
            "score": 0,
            "technical_confirmations": 0,
            "ml_probability": ml_probability,
            "reason": [
                "Indicator values contain NaN."
            ]
        }

    # ========================================================
    # EXTRACT VALUES
    # ========================================================

    price = float(
        latest["close"]
    )

    rsi = float(
        latest["RSI"]
    )

    ema20 = float(
        latest["EMA20"]
    )

    ema50 = float(
        latest["EMA50"]
    )

    previous_ema20 = float(
        previous["EMA20"]
    )

    previous_ema50 = float(
        previous["EMA50"]
    )

    macd = float(
        latest["MACD"]
    )

    macd_signal = float(
        latest["MACD_SIGNAL"]
    )

    previous_macd = float(
        previous["MACD"]
    )

    previous_macd_signal = float(
        previous["MACD_SIGNAL"]
    )

    bb_upper = float(
        latest["BB_UPPER"]
    )

    bb_lower = float(
        latest["BB_LOWER"]
    )

    atr = float(
        latest["ATR"]
    )

    # ========================================================
    # PRICE VALIDATION
    # ========================================================

    if price <= 0:

        return {
            "decision": "SKIP 🔴",
            "score": 0,
            "technical_confirmations": 0,
            "ml_probability": ml_probability,
            "reason": [
                "Invalid price."
            ]
        }

    # ========================================================
    # ATR VOLATILITY
    # ========================================================

    atr_percent = (
        atr / price
    ) * 100

    # ========================================================
    # SCORE
    # ========================================================

    score = 0

    confirmations = 0

    reasons = []

    # ========================================================
    # 1. MARKET MOMENTUM
    # ========================================================

    market_score = float(
        market_score
    )

    market_component = min(
        max(
            market_score,
            0
        ),
        40
    )

    score += market_component

    if market_score >= 20:

        reasons.append(
            "Strong market momentum"
        )

    elif market_score >= 10:

        reasons.append(
            "Moderate market momentum"
        )

    else:

        reasons.append(
            "Weak market momentum"
        )

    # ========================================================
    # 2. NEWS SENTIMENT
    # ========================================================

    news_score = float(
        news_score
    )

    news_component = (
        news_score * 3
    )

    news_component = min(
        max(
            news_component,
            -15
        ),
        15
    )

    score += news_component

    if news_score > 0:

        reasons.append(
            "Bullish news"
        )

    elif news_score < 0:

        reasons.append(
            "Bearish news"
        )

    else:

        reasons.append(
            "Neutral news"
        )

    # ========================================================
    # 3. EMA TREND
    # ========================================================

    bullish_ema = (
        ema20 > ema50
    )

    bullish_ema_crossover = (
        previous_ema20 <= previous_ema50
        and
        ema20 > ema50
    )

    if bullish_ema:

        score += 20

        confirmations += 1

        reasons.append(
            "EMA20 above EMA50"
        )

    else:

        score -= 20

        reasons.append(
            "EMA20 below EMA50"
        )

    if bullish_ema_crossover:

        score += 10

        reasons.append(
            "Fresh bullish EMA crossover"
        )

    # ========================================================
    # 4. PRICE VS EMA20
    # ========================================================

    price_above_ema20 = (
        price > ema20
    )

    if price_above_ema20:

        score += 15

        confirmations += 1

        reasons.append(
            "Price above EMA20"
        )

    else:

        score -= 15

        reasons.append(
            "Price below EMA20"
        )

    # ========================================================
    # 5. RSI
    # ========================================================

    rsi_good = False

    if 45 <= rsi <= 65:

        score += 15

        confirmations += 1

        rsi_good = True

        reasons.append(
            "RSI in healthy bullish range"
        )

    elif 35 <= rsi < 45:

        score += 5

        reasons.append(
            "RSI recovering"
        )

    elif 65 < rsi <= 70:

        score += 5

        reasons.append(
            "RSI strong but elevated"
        )

    elif rsi > 70:

        score -= 20

        reasons.append(
            "RSI overbought"
        )

    else:

        score -= 10

        reasons.append(
            "RSI weak"
        )

    # ========================================================
    # 6. MACD
    # ========================================================

    bullish_macd = (
        macd > macd_signal
    )

    bullish_macd_crossover = (
        previous_macd
        <= previous_macd_signal
        and
        macd > macd_signal
    )

    if bullish_macd:

        score += 20

        confirmations += 1

        reasons.append(
            "MACD bullish"
        )

    else:

        score -= 20

        reasons.append(
            "MACD bearish"
        )

    if bullish_macd_crossover:

        score += 10

        reasons.append(
            "Fresh bullish MACD crossover"
        )

    # ========================================================
    # 7. BOLLINGER BANDS
    # ========================================================

    band_range = (
        bb_upper - bb_lower
    )

    if band_range > 0:

        band_position = (
            price - bb_lower
        ) / band_range

    else:

        band_position = 0.5

    if (
        0.20
        <= band_position
        <= 0.75
    ):

        score += 5

        reasons.append(
            "Price in usable Bollinger zone"
        )

    elif band_position > 0.85:

        score -= 10

        reasons.append(
            "Price near upper Bollinger Band"
        )

    else:

        reasons.append(
            "Price near lower Bollinger Band"
        )

    # ========================================================
    # 8. ATR VOLATILITY
    # ========================================================

    volatility_ok = True

    if atr_percent < 0.10:

        score -= 10

        volatility_ok = False

        reasons.append(
            f"Volatility too low "
            f"({atr_percent:.2f}%)"
        )

    elif (
        atr_percent
        > MAX_BUY_ATR_PERCENT
    ):

        score -= 15

        volatility_ok = False

        reasons.append(
            f"Volatility too high "
            f"({atr_percent:.2f}%)"
        )

    else:

        score += 5

        confirmations += 1

        reasons.append(
            f"Usable volatility "
            f"({atr_percent:.2f}%)"
        )

    # ========================================================
    # 9. MACHINE LEARNING
    # ========================================================

    ml_confirmation = False

    ml_available = (
        ml_probability is not None
    )

    if ml_available:

        try:

            ml_probability = float(
                ml_probability
            )

            ml_probability = min(
                max(
                    ml_probability,
                    0.0
                ),
                1.0
            )

            if (
                ml_probability
                >= ML_STRONG_THRESHOLD
            ):

                score += 15

                confirmations += 1

                ml_confirmation = True

                reasons.append(
                    "Strong AI bullish confirmation "
                    f"({ml_probability * 100:.1f}%)"
                )

            elif (
                ml_probability
                >= ML_MODERATE_THRESHOLD
            ):

                score += 5

                reasons.append(
                    "Moderate AI bullish probability "
                    f"({ml_probability * 100:.1f}%)"
                )

            elif ml_probability < 0.40:

                score -= 10

                reasons.append(
                    "AI probability is bearish "
                    f"({ml_probability * 100:.1f}%)"
                )

            else:

                reasons.append(
                    "AI probability is neutral "
                    f"({ml_probability * 100:.1f}%)"
                )

        except (
            TypeError,
            ValueError
        ):

            ml_probability = None

            reasons.append(
                "AI prediction unavailable"
            )

    else:

        reasons.append(
            "AI prediction unavailable"
        )

    # ========================================================
    # FINAL CONDITIONS
    # ========================================================

    strong_trend = (
        bullish_ema
        and
        price_above_ema20
    )

    strong_momentum = (
        bullish_macd
        and
        rsi_good
    )

    # AI is an additional confirmation.
    #
    # If AI is available, a strong BUY requires
    # ML probability >= 65%.
    #
    # If ML is unavailable, the original technical
    # engine can still operate safely.

    ai_buy_ok = (
        ml_confirmation
        if ml_available
        else True
    )

    # ========================================================
    # FINAL DECISION
    # ========================================================

    if (
        confirmations >= 4
        and strong_trend
        and strong_momentum
        and volatility_ok
        and ai_buy_ok
        and score >= BUY_SCORE_THRESHOLD
    ):

        decision = (
            "BUY CANDIDATE 🟢"
        )

    elif (
        confirmations >= 3
        and
        score >= WATCH_SCORE_THRESHOLD
    ):

        decision = (
            "WATCH 🟡"
        )

    else:

        decision = (
            "AVOID 🔴"
        )

    # ========================================================
    # RESULT
    # ========================================================

    if ml_probability is not None:

        ml_probability_output = round(
            ml_probability,
            4
        )

        ml_confidence_percent = round(
            ml_probability * 100,
            2
        )

    else:

        ml_probability_output = None
        ml_confidence_percent = None

    return {

        "decision":
            decision,

        "score":
            round(
                score,
                2
            ),

        "technical_confirmations":
            confirmations,

        "atr_percent":
            round(
                atr_percent,
                2
            ),

        "ml_probability":
            ml_probability_output,

        "ml_confidence_percent":
            ml_confidence_percent,

        "ml_confirmation":
            ml_confirmation,

        "reason":
            reasons
    }