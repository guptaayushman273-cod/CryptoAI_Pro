from market.market_data import fetch_market_data
from indicators.indicators import calculate_indicators
from strategy.news_ai import analyze_news
from strategy.decision_engine import make_decision
from trader.paper_trader import PaperTrader
from ai.ml_predictor import predict_probability
from risk.risk_manager import calculate_trade


# ============================================================
# CRYPTOAI PRO - MAIN SYSTEM
# ============================================================

print("=" * 60)
print("CRYPTOAI PRO")
print("AI-POWERED CRYPTO TRADING SYSTEM")
print("=" * 60)


# ============================================================
# SETTINGS
# ============================================================

INITIAL_BALANCE = 200.0

bot = PaperTrader(INITIAL_BALANCE)

print(
    f"\nPaper trading balance: "
    f"${INITIAL_BALANCE:.2f}"
)


# ============================================================
# 1. MARKET SCANNER
# ============================================================

print(
    "\n[1/8] Scanning ML-supported CoinDCX markets..."
)

market_data = fetch_market_data(
    min_change_percent=0.0,
    min_volume=10000.0,
    interval="1m",
    limit=200,
    ml_mode=True
)

if market_data is None:

    print(
        "\nNo suitable ML-supported market found."
    )

    print(
        "CryptoAI Pro stopped safely."
    )

    raise SystemExit


best = market_data["market"]
candles = market_data["candles"]

coin = best["market"]
price = float(best["last_price"])
change = float(best["change_24_hour"])
volume = float(best["volume"])


print()
print("Selected ML-Supported Market")
print("-" * 40)

print(f"Coin:       {coin}")
print(f"Price:      {price}")
print(f"24h Change: {change:.2f}%")
print(f"Volume:     {volume:.2f}")
print(f"Candles:    {len(candles)}")

print(
    f"ML Support: "
    f"{market_data.get('ml_supported', False)}"
)


# ============================================================
# 2. TECHNICAL INDICATORS
# ============================================================

print(
    "\n[2/8] Calculating technical indicators..."
)

indicators = calculate_indicators(
    candles
)

if indicators is None or indicators.empty:

    print(
        "Unable to calculate indicators."
    )

    print(
        "CryptoAI Pro stopped safely."
    )

    raise SystemExit


latest = indicators.iloc[-1]


print()
print("Latest Technical Indicators")
print("-" * 40)

print(
    f"RSI:         "
    f"{latest['RSI']:.2f}"
)

print(
    f"EMA20:       "
    f"{latest['EMA20']:.8f}"
)

print(
    f"EMA50:       "
    f"{latest['EMA50']:.8f}"
)

print(
    f"MACD:        "
    f"{latest['MACD']:.8f}"
)

print(
    f"MACD Signal: "
    f"{latest['MACD_SIGNAL']:.8f}"
)

print(
    f"ATR:         "
    f"{latest['ATR']:.8f}"
)


# ============================================================
# 3. MARKET MOMENTUM
# ============================================================

print(
    "\n[3/8] Calculating market momentum score..."
)

market_score = 0


if change >= 15:

    market_score = 40

elif change >= 10:

    market_score = 35

elif change >= 7:

    market_score = 30

elif change >= 5:

    market_score = 25

elif change >= 2:

    market_score = 15

elif change > 0:

    market_score = 10


print(
    f"Market Score: "
    f"{market_score}"
)


# ============================================================
# 4. NEWS SENTIMENT
# ============================================================

print(
    "\n[4/8] Running news sentiment analysis..."
)

try:

    news = analyze_news(
        "crypto adoption growth partnership"
    )

    news_score = news.get(
        "score",
        0
    )

except Exception as error:

    print(
        f"News analysis warning: "
        f"{error}"
    )

    news_score = 0


print(
    f"News Score: "
    f"{news_score}"
)


# ============================================================
# 5. MACHINE LEARNING
# ============================================================

print(
    "\n[5/8] Running Random Forest AI prediction..."
)

ml_probability = None
ml_confidence = None
ai_signal = "UNAVAILABLE"


try:

    ml_result = predict_probability(
        indicators
    )

    ml_probability = float(
        ml_result["probability"]
    )

    ml_confidence = float(
        ml_result["confidence_percent"]
    )


    if ml_probability >= 0.65:

        ai_signal = "STRONG BULLISH"

    elif ml_probability >= 0.55:

        ai_signal = "MODERATE BULLISH"

    elif ml_probability >= 0.40:

        ai_signal = "NEUTRAL"

    else:

        ai_signal = "BEARISH"


    print()
    print("AI Prediction")
    print("-" * 40)

    print(
        f"Probability: "
        f"{ml_confidence:.2f}%"
    )

    print(
        "Target: Future 5-candle "
        "return > +0.20%"
    )

    print(
        f"AI Signal: "
        f"{ai_signal}"
    )


except Exception as error:

    print()
    print(
        "AI prediction unavailable."
    )

    print(
        f"Reason: {error}"
    )

    print(
        "Technical engine will continue without ML."
    )


# ============================================================
# 6. HYBRID DECISION ENGINE
# ============================================================

print(
    "\n[6/8] Running hybrid decision engine..."
)

# Paper trading mode.
fee_ok = True


decision = make_decision(
    market_score,
    news_score,
    fee_ok,
    indicators,
    ml_probability=ml_probability
)


print()
print("Trading Decision")
print("=" * 60)

print(
    f"Decision: "
    f"{decision['decision']}"
)

print(
    f"Score: "
    f"{decision['score']}"
)

print(
    f"Confirmations: "
    f"{decision['technical_confirmations']}"
)

print(
    f"ATR %: "
    f"{decision.get('atr_percent', 'N/A')}"
)


decision_ml_confidence = (
    decision.get(
        "ml_confidence_percent"
    )
)


if decision_ml_confidence is not None:

    print(
        f"AI Confidence: "
        f"{decision_ml_confidence:.2f}%"
    )

    print(
        f"AI Confirmation: "
        f"{decision.get('ml_confirmation')}"
    )

else:

    print(
        "AI Confidence: N/A"
    )


print()
print("Reasons:")


reasons = decision.get(
    "reason",
    []
)


if isinstance(reasons, list):

    for reason in reasons:

        print(
            f"  - {reason}"
        )

else:

    print(
        f"  - {reasons}"
    )


# ============================================================
# 7. RISK MANAGEMENT
# ============================================================

print(
    "\n[7/8] Running risk management..."
)


risk_result = calculate_trade(
    balance=bot.balance,
    price=price
)


print()
print("Risk Management")
print("=" * 60)

print(
    f"Approved: "
    f"{risk_result.get('approved', False)}"
)

print(
    f"Available Balance: "
    f"${bot.balance:.2f}"
)

print(
    f"Position Value: "
    f"${risk_result.get('position_value', 0):.2f}"
)

print(
    f"Quantity: "
    f"{risk_result.get('quantity', 0)}"
)

print(
    f"Risk Limit: "
    f"{risk_result.get('risk_percent_limit', 0):.2f}%"
)

print(
    f"Actual Account Risk: "
    f"{risk_result.get('actual_risk_percent', 0):.2f}%"
)

print(
    f"Actual Risk Amount: "
    f"${risk_result.get('actual_risk_amount', 0):.2f}"
)

print(
    f"Stop Loss: "
    f"{risk_result.get('stop_loss', 0)}"
)

print(
    f"Take Profit: "
    f"{risk_result.get('take_profit', 0)}"
)

print(
    f"Risk/Reward: "
    f"{risk_result.get('risk_reward_ratio', 0)}:1"
)

print(
    f"Risk Status: "
    f"{risk_result.get('reason')}"
)


# ============================================================
# 8. PAPER TRADING EXECUTION
# ============================================================

print(
    "\n[8/8] Paper trading execution..."
)


decision_is_buy = (
    "BUY"
    in decision["decision"]
)

risk_approved = (
    risk_result.get(
        "approved",
        False
    )
)


# ------------------------------------------------------------
# BUY + RISK APPROVED
# ------------------------------------------------------------

if (
    decision_is_buy
    and
    risk_approved
):

    print()
    print(
        "BUY signal passed risk management."
    )

    print(
        "Opening PAPER position..."
    )


    buy_result = bot.buy(

        coin=coin,

        price=price,

        quantity=
            risk_result["quantity"],

        stop_loss_price=
            risk_result["stop_loss"],

        take_profit_price=
            risk_result["take_profit"]
    )


    print()
    print("Paper Trade Result")
    print("-" * 40)

    print(
        buy_result
    )


    if buy_result.get(
        "success"
    ):

        print()
        print(
            "PAPER POSITION OPENED"
        )

        print(
            f"Coin: "
            f"{coin}"
        )

        print(
            f"Entry: "
            f"{price}"
        )

        print(
            f"Quantity: "
            f"{risk_result['quantity']}"
        )

        print(
            f"Position Value: "
            f"${risk_result['position_value']:.2f}"
        )

        print(
            f"Stop Loss: "
            f"{risk_result['stop_loss']}"
        )

        print(
            f"Take Profit: "
            f"{risk_result['take_profit']}"
        )

        print(
            f"Remaining Balance: "
            f"${bot.balance:.2f}"
        )

        print()
        print(
            "Position will remain open until "
            "stop-loss or take-profit conditions "
            "are reached."
        )


# ------------------------------------------------------------
# BUY + RISK REJECTED
# ------------------------------------------------------------

elif (
    decision_is_buy
    and
    not risk_approved
):

    print()
    print(
        "BUY signal detected."
    )

    print(
        "Risk manager rejected the trade."
    )

    print(
        "No paper position opened."
    )


# ------------------------------------------------------------
# WATCH
# ------------------------------------------------------------

elif (
    "WATCH"
    in decision["decision"]
):

    print()
    print(
        "Market remains on WATCH."
    )

    print(
        "Risk parameters calculated, "
        "but no position opened."
    )


# ------------------------------------------------------------
# AVOID
# ------------------------------------------------------------

else:

    print()
    print(
        "No BUY signal."
    )

    print(
        "Risk parameters calculated, "
        "but no position opened."
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 60)
print("CRYPTOAI PRO ANALYSIS COMPLETE")
print("=" * 60)

print(
    f"Market: "
    f"{coin}"
)

print(
    f"Price: "
    f"{price}"
)

print(
    f"Decision: "
    f"{decision['decision']}"
)


if ml_probability is not None:

    print(
        f"AI Probability: "
        f"{ml_probability * 100:.2f}%"
    )

else:

    print(
        "AI Probability: N/A"
    )


print(
    f"AI Signal: "
    f"{ai_signal}"
)

print(
    f"Decision Score: "
    f"{decision['score']}"
)

print(
    f"Risk Approved: "
    f"{risk_approved}"
)

print(
    f"Recommended Position: "
    f"${risk_result.get('position_value', 0):.2f}"
)

print(
    f"Stop Loss: "
    f"{risk_result.get('stop_loss', 0)}"
)

print(
    f"Take Profit: "
    f"{risk_result.get('take_profit', 0)}"
)

print(
    f"Paper Balance: "
    f"${bot.balance:.2f}"
)


if bot.position is not None:

    print(
        "Position Status: OPEN"
    )

else:

    print(
        "Position Status: NO OPEN POSITION"
    )


print()
print(
    "Mode: ML-SUPPORTED "
    "RISK-MANAGED PAPER TRADING"
)

print("=" * 60)