from datetime import datetime

from database.database import get_connection


# ==========================================
# SAVE TRADE
# ==========================================

def save_trade(data):
    """
    Save a trade event into the SQLite database.
    """

    connection = get_connection()

    cursor = connection.cursor()

    trade_time = datetime.now().isoformat(
        sep=" ",
        timespec="seconds"
    )

    cursor.execute(
        """
        INSERT INTO trades (
            action,
            coin,
            price,
            amount,
            profit,
            profit_percent,
            time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("action"),
            data.get("coin"),
            data.get("price"),
            data.get("amount"),
            data.get("profit"),
            data.get("profit_percent"),
            trade_time
        )
    )

    connection.commit()
    connection.close()


# ==========================================
# SHOW TRADES
# ==========================================

def show_trades():
    """
    Display all stored trades.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            action,
            coin,
            price,
            amount,
            profit,
            profit_percent,
            time
        FROM trades
        ORDER BY id
        """
    )

    trades = cursor.fetchall()

    connection.close()

    if not trades:
        print("No trades yet.")
        return

    for trade in trades:
        print(trade)