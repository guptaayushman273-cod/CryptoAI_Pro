# ==========================================
# CRYPTOAI PRO - V2 DASHBOARD
# ==========================================

import os
import sys
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st


# ==========================================
# PROJECT PATH FIX
# ==========================================
# dashboard/app.py is inside the dashboard folder.
# This adds the main CryptoAI_Bot folder to Python's path
# so imports such as database.database work correctly.

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==========================================
# PROJECT IMPORTS
# ==========================================

from database.database import (
    init_db,
    get_position
)


# ==========================================
# DATABASE PATH
# ==========================================

DATABASE_PATH = os.path.join(
    PROJECT_ROOT,
    "cryptoai.db"
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CryptoAI Pro Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 16px;
        color: #777777;
        margin-bottom: 25px;
    }

    .status-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dddddd;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

try:
    init_db()
except Exception as e:
    st.error(
        f"Database initialization failed: {e}"
    )


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_database_connection():
    """
    Create a connection to the CryptoAI Pro SQLite database.
    """

    return sqlite3.connect(
        DATABASE_PATH
    )


def get_trade_history():
    """
    Read all stored trades from the trades table.
    """

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

        dataframe = pd.read_sql_query(
            query,
            connection
        )

        connection.close()

        return dataframe

    except Exception as e:

        st.warning(
            f"Could not read trade history: {e}"
        )

        return pd.DataFrame()


def get_trade_statistics(dataframe):
    """
    Calculate basic trading statistics.
    """

    if dataframe.empty:

        return {
            "total_trades": 0,
            "buy_trades": 0,
            "sell_trades": 0,
            "total_profit": 0.0,
            "winning_trades": 0,
            "losing_trades": 0
        }

    buy_trades = len(
        dataframe[
            dataframe["action"] == "BUY"
        ]
    )

    sell_trades = len(
        dataframe[
            dataframe["action"] == "SELL"
        ]
    )

    sell_dataframe = dataframe[
        dataframe["action"] == "SELL"
    ]

    if sell_dataframe.empty:

        total_profit = 0.0

        winning_trades = 0

        losing_trades = 0

    else:

        total_profit = float(
            sell_dataframe["profit"]
            .fillna(0)
            .sum()
        )

        winning_trades = len(
            sell_dataframe[
                sell_dataframe["profit"] > 0
            ]
        )

        losing_trades = len(
            sell_dataframe[
                sell_dataframe["profit"] < 0
            ]
        )

    return {
        "total_trades": len(dataframe),
        "buy_trades": buy_trades,
        "sell_trades": sell_trades,
        "total_profit": total_profit,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades
    }


def get_current_position():
    """
    Get the currently open paper-trading position.
    """

    try:

        position = get_position()

        return position

    except Exception as e:

        st.warning(
            f"Could not read open position: {e}"
        )

        return None


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">📊 CryptoAI Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'V2 Paper Trading Dashboard'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title(
    "⚙️ Dashboard"
)

st.sidebar.write(
    "CryptoAI Pro V2"
)

st.sidebar.write(
    "Paper Trading Mode"
)

st.sidebar.divider()

if st.sidebar.button(
    "🔄 Refresh Dashboard"
):

    st.rerun()


st.sidebar.divider()

st.sidebar.write(
    "Database:"
)

st.sidebar.code(
    DATABASE_PATH
)


# ==========================================
# LOAD DATA
# ==========================================

position = get_current_position()

trade_history = get_trade_history()

statistics = get_trade_statistics(
    trade_history
)


# ==========================================
# SYSTEM STATUS
# ==========================================

st.subheader(
    "🟢 System Status"
)

status_col1, status_col2, status_col3 = st.columns(3)


with status_col1:

    st.metric(
        "Database",
        "Connected"
    )


with status_col2:

    if position:

        st.metric(
            "Position",
            "OPEN"
        )

    else:

        st.metric(
            "Position",
            "NO POSITION"
        )


with status_col3:

    st.metric(
        "Trading Mode",
        "PAPER"
    )


# ==========================================
# OPEN POSITION
# ==========================================

st.subheader(
    "📌 Current Position"
)

if position:

    position_col1, position_col2, position_col3, position_col4 = st.columns(
        4
    )

    with position_col1:

        st.metric(
            "Coin",
            position.get(
                "coin",
                "Unknown"
            )
        )

    with position_col2:

        st.metric(
            "Buy Price",
            f"₹{float(position.get('price', 0)):,.6f}"
        )

    with position_col3:

        st.metric(
            "Position Value",
            f"₹{float(position.get('position_value', 0)):,.2f}"
        )

    with position_col4:

        st.metric(
            "Stop Loss",
            f"₹{float(position.get('stop_loss_price', 0)):,.6f}"
        )

    st.write(
        "**Amount:**",
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
        "No open paper-trading position."
    )


# ==========================================
# TRADING STATISTICS
# ==========================================

st.subheader(
    "📈 Trading Statistics"
)

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(
    4
)


with stat_col1:

    st.metric(
        "Total Trades",
        statistics["total_trades"]
    )


with stat_col2:

    st.metric(
        "BUY Trades",
        statistics["buy_trades"]
    )


with stat_col3:

    st.metric(
        "SELL Trades",
        statistics["sell_trades"]
    )


with stat_col4:

    total_profit = statistics[
        "total_profit"
    ]

    st.metric(
        "Total P/L",
        f"₹{total_profit:,.2f}"
    )


# ==========================================
# WIN / LOSS STATISTICS
# ==========================================

win_col1, win_col2, win_col3 = st.columns(
    3
)


with win_col1:

    st.metric(
        "Winning Trades",
        statistics["winning_trades"]
    )


with win_col2:

    st.metric(
        "Losing Trades",
        statistics["losing_trades"]
    )


with win_col3:

    completed_trades = (
        statistics["winning_trades"]
        + statistics["losing_trades"]
    )

    if completed_trades > 0:

        win_rate = (
            statistics["winning_trades"]
            / completed_trades
        ) * 100

    else:

        win_rate = 0.0

    st.metric(
        "Win Rate",
        f"{win_rate:.2f}%"
    )


# ==========================================
# PROFIT / LOSS CHART
# ==========================================

st.subheader(
    "📊 Profit / Loss"
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

        sell_history["time"] = pd.to_datetime(
            sell_history["time"],
            errors="coerce"
        )

        sell_history = sell_history.sort_values(
            "time"
        )

        sell_history["cumulative_profit"] = (
            sell_history["profit"].cumsum()
        )

        chart_data = sell_history[
            [
                "time",
                "cumulative_profit"
            ]
        ].set_index(
            "time"
        )

        st.line_chart(
            chart_data
        )

    else:

        st.info(
            "No completed SELL trades available for the chart."
        )

else:

    st.info(
        "No trade history available yet."
    )


# ==========================================
# TRADE HISTORY
# ==========================================

st.subheader(
    "📜 Trade History"
)

if not trade_history.empty:

    display_history = trade_history.copy()

    if "price" in display_history.columns:

        display_history["price"] = (
            pd.to_numeric(
                display_history["price"],
                errors="coerce"
            )
        )

    if "amount" in display_history.columns:

        display_history["amount"] = (
            pd.to_numeric(
                display_history["amount"],
                errors="coerce"
            )
        )

    if "profit" in display_history.columns:

        display_history["profit"] = (
            pd.to_numeric(
                display_history["profit"],
                errors="coerce"
            )
        )

    if "profit_percent" in display_history.columns:

        display_history["profit_percent"] = (
            pd.to_numeric(
                display_history["profit_percent"],
                errors="coerce"
            )
        )

    st.dataframe(
        display_history,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No trades have been recorded yet."
    )


# ==========================================
# LATEST TRADE
# ==========================================

st.subheader(
    "🕒 Latest Trade"
)

if not trade_history.empty:

    latest_trade = trade_history.iloc[0]

    latest_col1, latest_col2, latest_col3 = st.columns(
        3
    )

    with latest_col1:

        st.write(
            "**Action:**",
            latest_trade.get(
                "action",
                "Unknown"
            )
        )

        st.write(
            "**Coin:**",
            latest_trade.get(
                "coin",
                "Unknown"
            )
        )

    with latest_col2:

        st.write(
            "**Price:**",
            latest_trade.get(
                "price",
                0
            )
        )

        st.write(
            "**Amount:**",
            latest_trade.get(
                "amount",
                0
            )
        )

    with latest_col3:

        st.write(
            "**Profit:**",
            latest_trade.get(
                "profit",
                0
            )
        )

        st.write(
            "**Time:**",
            latest_trade.get(
                "time",
                "Unknown"
            )
        )

else:

    st.info(
        "No latest trade available."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "CryptoAI Pro V2 • Paper Trading • SQLite Database"
)

st.caption(
    "Last dashboard refresh: "
    + datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)