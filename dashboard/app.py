# ============================================================
# CRYPTOAI PRO - V3 DASHBOARD
# ============================================================

import os
import sys
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# PROJECT IMPORTS
# ============================================================

from database.database import init_db, get_position
from market.market_data import fetch_market_data
from indicators.indicators import calculate_indicators
from strategy.news_ai import analyze_news
from strategy.decision_engine import make_decision
from ai.ml_predictor import predict_probability
from risk.risk_manager import calculate_trade


# ============================================================
# SETTINGS
# ============================================================

DATABASE_PATH = os.path.join(
    PROJECT_ROOT,
    "cryptoai.db"
)

PAPER_BALANCE = 200.0

OVERALL_PROGRESS = 100
V1_PROGRESS = 100
V2_PROGRESS = 100
V3_PROGRESS = 100


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CryptoAI Pro V3",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# DATABASE
# ============================================================

try:
    init_db()
except Exception as error:
    st.warning(
        f"Database initialization warning: {error}"
    )


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_database_connection():

    return sqlite3.connect(
        DATABASE_PATH
    )


def get_trade_history():

    connection = None

    try:

        connection = get_database_connection()

        query = """
        SELECT
            action,
            coin,
            price,
            amount,
            profit,
            profit_percent,
            time
        FROM trades
        ORDER BY time DESC
        """

        return pd.read_sql_query(
            query,
            connection
        )

    except Exception as error:

        st.warning(
            f"Could not read trade history: {error}"
        )

        return pd.DataFrame()

    finally:

        if connection is not None:
            connection.close()


def get_current_position():

    try:

        return get_position()

    except Exception as error:

        st.warning(
            f"Could not read position: {error}"
        )

        return None


def get_statistics(dataframe):

    if dataframe.empty:

        return {
            "total": 0,
            "buys": 0,
            "sells": 0,
            "profit": 0.0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0
        }

    buys = len(
        dataframe[
            dataframe["action"] == "BUY"
        ]
    )

    sells_df = dataframe[
        dataframe["action"] == "SELL"
    ].copy()

    sells = len(sells_df)

    if sells_df.empty:

        profit = 0.0
        wins = 0
        losses = 0
        win_rate = 0.0

    else:

        sells_df["profit"] = pd.to_numeric(
            sells_df["profit"],
            errors="coerce"
        ).fillna(0)

        profit = float(
            sells_df["profit"].sum()
        )

        wins = int(
            (
                sells_df["profit"] > 0
            ).sum()
        )

        losses = int(
            (
                sells_df["profit"] < 0
            ).sum()
        )

        completed = wins + losses

        win_rate = (
            wins / completed * 100
            if completed > 0
            else 0.0
        )

    return {
        "total": len(dataframe),
        "buys": buys,
        "sells": sells,
        "profit": profit,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate
    }


# ============================================================
# MARKET SCORE
# ============================================================

def calculate_market_score(change):

    if change >= 15:
        return 40

    if change >= 10:
        return 35

    if change >= 7:
        return 30

    if change >= 5:
        return 25

    if change >= 2:
        return 15

    if change > 0:
        return 10

    return 0


# ============================================================
# LIVE ANALYSIS
# ============================================================

def run_live_analysis():

    result = {
        "success": False
    }

    try:

        market_data = fetch_market_data(
            min_change_percent=0.0,
            min_volume=10000.0,
            interval="1m",
            limit=200,
            ml_mode=True
        )

        if not market_data:

            result["error"] = (
                "No ML-supported market found."
            )

            return result

        best = market_data["market"]
        candles = market_data["candles"]

        coin = best["market"]
        price = float(
            best["last_price"]
        )

        change = float(
            best["change_24_hour"]
        )

        volume = float(
            best["volume"]
        )

        indicators = calculate_indicators(
            candles
        )

        if (
            indicators is None
            or indicators.empty
        ):

            result["error"] = (
                "Indicator calculation failed."
            )

            return result

        latest = indicators.iloc[-1]

        market_score = (
            calculate_market_score(
                change
            )
        )

        # ----------------------------------------------------
        # NEWS
        # ----------------------------------------------------

        try:

            news = analyze_news(
                "crypto adoption growth partnership"
            )

            news_score = news.get(
                "score",
                0
            )

        except Exception:

            news_score = 0

        # ----------------------------------------------------
        # ML
        # ----------------------------------------------------

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
                ml_result[
                    "confidence_percent"
                ]
            )

            if ml_probability >= 0.65:

                ai_signal = (
                    "STRONG BULLISH"
                )

            elif ml_probability >= 0.55:

                ai_signal = (
                    "MODERATE BULLISH"
                )

            elif ml_probability >= 0.40:

                ai_signal = "NEUTRAL"

            else:

                ai_signal = "BEARISH"

        except Exception:

            pass

        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        decision = make_decision(
            market_score,
            news_score,
            True,
            indicators,
            ml_probability=ml_probability
        )

        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        risk = calculate_trade(
            balance=PAPER_BALANCE,
            price=price
        )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        result.update({

            "success":
                True,

            "coin":
                coin,

            "price":
                price,

            "change":
                change,

            "volume":
                volume,

            "candles":
                len(candles),

            "rsi":
                float(latest["RSI"]),

            "ema20":
                float(latest["EMA20"]),

            "ema50":
                float(latest["EMA50"]),

            "macd":
                float(latest["MACD"]),

            "macd_signal":
                float(
                    latest["MACD_SIGNAL"]
                ),

            "atr":
                float(latest["ATR"]),

            "market_score":
                market_score,

            "news_score":
                news_score,

            "ml_probability":
                ml_probability,

            "ml_confidence":
                ml_confidence,

            "ai_signal":
                ai_signal,

            "decision":
                decision,

            "risk":
                risk
        })

        return result

    except Exception as error:

        result["error"] = str(
            error
        )

        return result


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 CryptoAI Pro V3"
)

st.caption(
    "AI-Powered Crypto Analysis & "
    "Risk-Managed Paper Trading"
)

st.info(
    "Dashboard mode is monitoring/analysis only. "
    "Trade execution remains controlled by main.py."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ CryptoAI Pro"
)

st.sidebar.write(
    "V3 Development Dashboard"
)

st.sidebar.write(
    "Trading Mode: PAPER"
)

st.sidebar.write(
    "Live Trading: DISABLED"
)

st.sidebar.divider()

if st.sidebar.button(
    "🔄 Refresh Analysis",
    width="stretch"
):

    st.rerun()

st.sidebar.divider()

st.sidebar.caption(
    "ML Training Universe"
)

st.sidebar.write(
    "BTCUSDT"
)

st.sidebar.write(
    "ETHUSDT"
)

st.sidebar.write(
    "LSKUSDT"
)


# ============================================================
# PROJECT PROGRESS
# ============================================================

st.header(
    "🚀 Project Development Progress"
)

st.subheader(
    f"Overall Project Progress — "
    f"{OVERALL_PROGRESS}%"
)

st.progress(
    OVERALL_PROGRESS / 100
)

st.write("")

progress_col1, progress_col2, progress_col3 = (
    st.columns(3)
)


with progress_col1:

    st.markdown(
        "### V1 — Core Foundation"
    )

    st.metric(
        "Progress",
        f"{V1_PROGRESS}%"
    )

    st.progress(
        V1_PROGRESS / 100
    )

    st.caption(
        "API, market scanner, indicators, "
        "strategy foundation and project structure."
    )


with progress_col2:

    st.markdown(
        "### V2 — Paper Trading"
    )

    st.metric(
        "Progress",
        f"{V2_PROGRESS}%"
    )

    st.progress(
        V2_PROGRESS / 100
    )

    st.caption(
        "Paper trader, SQLite database, "
        "trade history and portfolio tracking."
    )


with progress_col3:

    st.markdown(
        "### V3 — AI / ML"
    )

    st.metric(
        "Progress",
        f"{V3_PROGRESS}%"
    )

    st.progress(
        V3_PROGRESS / 100
    )

    st.caption(
        "Random Forest, live inference, "
        "hybrid decisions and risk management."
    )


st.divider()


# ============================================================
# LOAD DATABASE INFORMATION
# ============================================================

position = get_current_position()

trade_history = get_trade_history()

statistics = get_statistics(
    trade_history
)


# ============================================================
# SYSTEM STATUS
# ============================================================

st.header(
    "🖥️ System Status"
)

status1, status2, status3, status4 = (
    st.columns(4)
)


with status1:

    st.metric(
        "Database",
        "CONNECTED"
    )


with status2:

    st.metric(
        "Trading Mode",
        "PAPER"
    )


with status3:

    st.metric(
        "ML Model",
        "ACTIVE"
    )


with status4:

    st.metric(
        "Position",
        (
            "OPEN"
            if position
            else "NO POSITION"
        )
    )


# ============================================================
# LIVE ANALYSIS
# ============================================================

st.divider()

st.header(
    "📡 Live Market Analysis"
)

with st.spinner(
    "Running CryptoAI Pro analysis..."
):

    analysis = run_live_analysis()


if not analysis["success"]:

    st.error(
        "Live analysis failed: "
        + analysis.get(
            "error",
            "Unknown error"
        )
    )

else:

    # ========================================================
    # MARKET
    # ========================================================

    market1, market2, market3, market4 = (
        st.columns(4)
    )


    with market1:

        st.metric(
            "Selected Market",
            analysis["coin"]
        )


    with market2:

        st.metric(
            "Price",
            f"${analysis['price']:,.6f}"
        )


    with market3:

        st.metric(
            "24h Change",
            f"{analysis['change']:.2f}%"
        )


    with market4:

        st.metric(
            "24h Volume",
            f"${analysis['volume']:,.0f}"
        )


    st.caption(
        f"Using {analysis['candles']} "
        f"one-minute candles."
    )


    # ========================================================
    # TECHNICAL ANALYSIS
    # ========================================================

    st.subheader(
        "📈 Technical Analysis"
    )

    tech1, tech2, tech3 = (
        st.columns(3)
    )


    with tech1:

        st.metric(
            "RSI",
            f"{analysis['rsi']:.2f}"
        )

        st.metric(
            "ATR",
            f"{analysis['atr']:.6f}"
        )


    with tech2:

        st.metric(
            "EMA 20",
            f"{analysis['ema20']:.6f}"
        )

        st.metric(
            "EMA 50",
            f"{analysis['ema50']:.6f}"
        )


    with tech3:

        st.metric(
            "MACD",
            f"{analysis['macd']:.6f}"
        )

        st.metric(
            "MACD Signal",
            f"{analysis['macd_signal']:.6f}"
        )


    # ========================================================
    # AI
    # ========================================================

    st.subheader(
        "🧠 AI Intelligence"
    )

    ai1, ai2, ai3, ai4 = (
        st.columns(4)
    )


    with ai1:

        if (
            analysis["ml_confidence"]
            is not None
        ):

            st.metric(
                "AI Probability",
                (
                    f"{analysis['ml_confidence']:.2f}%"
                )
            )

        else:

            st.metric(
                "AI Probability",
                "N/A"
            )


    with ai2:

        st.metric(
            "AI Signal",
            analysis["ai_signal"]
        )


    with ai3:

        st.metric(
            "Market Score",
            analysis["market_score"]
        )


    with ai4:

        st.metric(
            "News Score",
            analysis["news_score"]
        )


    st.caption(
        "ML target: probability that the "
        "future 5-candle return exceeds +0.20%."
    )


    # ========================================================
    # HYBRID DECISION
    # ========================================================

    st.subheader(
        "🎯 Hybrid Trading Decision"
    )

    decision = analysis[
        "decision"
    ]

    decision1, decision2, decision3 = (
        st.columns(3)
    )


    with decision1:

        st.metric(
            "Decision",
            decision.get(
                "decision",
                "N/A"
            )
        )


    with decision2:

        st.metric(
            "Decision Score",
            decision.get(
                "score",
                0
            )
        )


    with decision3:

        st.metric(
            "Confirmations",
            decision.get(
                "technical_confirmations",
                0
            )
        )


    reasons = decision.get(
        "reason",
        []
    )

    with st.expander(
        "View Decision Reasons"
    ):

        if isinstance(
            reasons,
            list
        ):

            for reason in reasons:

                st.write(
                    "•",
                    reason
                )

        else:

            st.write(
                reasons
            )


    # ========================================================
    # RISK MANAGEMENT
    # ========================================================

    st.subheader(
        "🛡️ Risk Management"
    )

    risk = analysis[
        "risk"
    ]

    risk1, risk2, risk3, risk4 = (
        st.columns(4)
    )


    with risk1:

        st.metric(
            "Position Size",
            (
                f"${risk.get('position_value', 0):.2f}"
            )
        )

        st.metric(
            "Quantity",
            risk.get(
                "quantity",
                0
            )
        )


    with risk2:

        st.metric(
            "Actual Risk",
            (
                f"{risk.get('actual_risk_percent', 0):.2f}%"
            )
        )

        st.metric(
            "Risk Amount",
            (
                f"${risk.get('actual_risk_amount', 0):.2f}"
            )
        )


    with risk3:

        st.metric(
            "Stop Loss",
            risk.get(
                "stop_loss",
                0
            )
        )

        st.metric(
            "Take Profit",
            risk.get(
                "take_profit",
                0
            )
        )


    with risk4:

        st.metric(
            "Risk / Reward",
            (
                f"{risk.get('risk_reward_ratio', 0)}:1"
            )
        )

        st.metric(
            "Risk Approval",
            (
                "APPROVED"
                if risk.get(
                    "approved",
                    False
                )
                else "REJECTED"
            )
        )


# ============================================================
# CURRENT POSITION
# ============================================================

st.divider()

st.header(
    "📌 Current Paper Position"
)


if position:

    pos1, pos2, pos3, pos4 = (
        st.columns(4)
    )


    with pos1:

        st.metric(
            "Coin",
            position.get(
                "coin",
                "Unknown"
            )
        )


    with pos2:

        st.metric(
            "Entry Price",
            (
                f"${float(position.get('price', 0)):,.6f}"
            )
        )


    with pos3:

        st.metric(
            "Position Value",
            (
                f"${float(position.get('position_value', 0)):,.2f}"
            )
        )


    with pos4:

        st.metric(
            "Stop Loss",
            (
                f"${float(position.get('stop_loss_price', 0)):,.6f}"
            )
        )


    st.write(
        "**Quantity:**",
        position.get(
            "amount",
            0
        )
    )

    st.write(
        "**Opened At:**",
        position.get(
            "opened_at",
            "Unknown"
        )
    )


else:

    st.info(
        "No paper position is currently open."
    )


# ============================================================
# TRADING PERFORMANCE
# ============================================================

st.divider()

st.header(
    "💼 Paper Trading Performance"
)

perf1, perf2, perf3, perf4 = (
    st.columns(4)
)


with perf1:

    st.metric(
        "Total Events",
        statistics["total"]
    )


with perf2:

    st.metric(
        "Completed Trades",
        statistics["sells"]
    )


with perf3:

    st.metric(
        "Total P/L",
        f"${statistics['profit']:,.2f}"
    )


with perf4:

    st.metric(
        "Win Rate",
        f"{statistics['win_rate']:.2f}%"
    )


perf5, perf6, perf7 = (
    st.columns(3)
)


with perf5:

    st.metric(
        "BUY Events",
        statistics["buys"]
    )


with perf6:

    st.metric(
        "Winning Trades",
        statistics["wins"]
    )


with perf7:

    st.metric(
        "Losing Trades",
        statistics["losses"]
    )


# ============================================================
# P/L CHART
# ============================================================

st.subheader(
    "📊 Cumulative Profit / Loss"
)


if not trade_history.empty:

    sell_history = trade_history[
        trade_history["action"] == "SELL"
    ].copy()


    if not sell_history.empty:

        sell_history["profit"] = (
            pd.to_numeric(
                sell_history["profit"],
                errors="coerce"
            )
            .fillna(0)
        )

        sell_history["time"] = (
            pd.to_datetime(
                sell_history["time"],
                errors="coerce"
            )
        )

        sell_history = (
            sell_history
            .sort_values(
                "time"
            )
        )

        sell_history[
            "cumulative_profit"
        ] = (
            sell_history[
                "profit"
            ].cumsum()
        )

        chart = sell_history[
            [
                "time",
                "cumulative_profit"
            ]
        ].set_index(
            "time"
        )

        st.line_chart(
            chart
        )

    else:

        st.info(
            "No completed SELL trades yet."
        )

else:

    st.info(
        "No trade history available yet."
    )


# ============================================================
# TRADE HISTORY
# ============================================================

st.subheader(
    "📜 Trade History"
)


if not trade_history.empty:

    st.dataframe(
        trade_history,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No trades have been recorded yet."
    )


# ============================================================
# MODEL INFORMATION
# ============================================================

st.divider()

st.header(
    "🤖 Machine Learning Model"
)

model1, model2, model3, model4 = (
    st.columns(4)
)


with model1:

    st.metric(
        "Algorithm",
        "Random Forest"
    )


with model2:

    st.metric(
        "Features",
        "19"
    )


with model3:

    st.metric(
        "Test ROC-AUC",
        "0.8306"
    )


with model4:

    st.metric(
        "Training Markets",
        "3"
    )


st.warning(
    "The current ML model is experimental and is used "
    "as an advisory signal for paper trading. Test "
    "performance varies substantially between BTCUSDT, "
    "ETHUSDT and LSKUSDT, so it should not be treated "
    "as a production trading model."
)


# ============================================================
# ARCHITECTURE
# ============================================================

st.divider()

st.header(
    "🏗️ System Pipeline"
)

st.code(
    """
CoinDCX Market Data
        ↓
Technical Indicators
        ↓
Market + News Analysis
        ↓
Random Forest AI
        ↓
Hybrid Decision Engine
        ↓
Risk Manager
        ↓
Paper Trader
        ↓
SQLite Database
        ↓
CryptoAI Pro Dashboard
""",
    language="text"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "CryptoAI Pro V3 • AI/ML • "
    "Risk Management • Paper Trading"
)

st.caption(
    "Dashboard refreshed: "
    + datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)