import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "cryptoai.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_FILE)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            coin TEXT NOT NULL,
            price REAL NOT NULL,
            amount REAL,
            profit REAL,
            profit_percent REAL,
            time TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            coin TEXT,
            buy_price REAL,
            amount REAL,
            position_value REAL,
            stop_loss_price REAL,
            opened_at TEXT
        )
    """)

    # --------------------------------------------------------
    # Upgrade older database versions
    # --------------------------------------------------------

    cursor.execute("PRAGMA table_info(positions)")
    columns = {row[1] for row in cursor.fetchall()}

    if "position_value" not in columns:
        cursor.execute(
            "ALTER TABLE positions ADD COLUMN position_value REAL"
        )

    if "stop_loss_price" not in columns:
        cursor.execute(
            "ALTER TABLE positions ADD COLUMN stop_loss_price REAL"
        )

    connection.commit()
    connection.close()


# ============================================================
# SAVE POSITION
# ============================================================

def save_position(
    coin,
    buy_price,
    amount,
    position_value,
    stop_loss_price,
    opened_at
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO positions (
            id,
            coin,
            buy_price,
            amount,
            position_value,
            stop_loss_price,
            opened_at
        )
        VALUES (1, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(id)
        DO UPDATE SET
            coin = excluded.coin,
            buy_price = excluded.buy_price,
            amount = excluded.amount,
            position_value = excluded.position_value,
            stop_loss_price = excluded.stop_loss_price,
            opened_at = excluded.opened_at
    """, (
        coin,
        buy_price,
        amount,
        position_value,
        stop_loss_price,
        opened_at
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET CURRENT POSITION
# ============================================================

def get_position():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            coin,
            buy_price,
            amount,
            position_value,
            stop_loss_price,
            opened_at
        FROM positions
        WHERE id = 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "coin": row[0],
        "price": row[1],
        "amount": row[2],
        "position_value": row[3],
        "stop_loss_price": row[4],
        "opened_at": row[5]
    }


# ============================================================
# CLEAR CURRENT POSITION
# ============================================================

def clear_position():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM positions WHERE id = 1"
    )

    connection.commit()
    connection.close()


# ============================================================
# SAVE TRADE
# ============================================================

def save_trade(
    action,
    coin,
    price,
    amount=None,
    profit=None,
    profit_percent=None,
    time=None
):
    """
    Save a completed trade into the trades table.
    """

    connection = get_connection()
    cursor = connection.cursor()

    if time is None:
        from datetime import datetime
        time = datetime.now().isoformat(timespec="seconds")

    cursor.execute("""
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
    """, (
        action,
        coin,
        price,
        amount,
        profit,
        profit_percent,
        time
    ))

    connection.commit()

    trade_id = cursor.lastrowid

    connection.close()

    return trade_id


# ============================================================
# GET ALL TRADES
# ============================================================

def get_all_trades():
    """
    Return all stored trades.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
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
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# GET RECENT TRADES
# ============================================================

def get_recent_trades(limit=10):
    """
    Return the most recent trades.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
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
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# GET TRADE COUNT
# ============================================================

def get_trade_count():
    """
    Return the total number of stored trades.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM trades
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# GET TOTAL PROFIT
# ============================================================

def get_total_profit():
    """
    Return the total profit/loss of stored trades.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(profit), 0)
        FROM trades
        WHERE profit IS NOT NULL
    """)

    total_profit = cursor.fetchone()[0]

    connection.close()

    return total_profit


# ============================================================
# DATABASE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CRYPTOAI PRO DATABASE TEST")
    print("=" * 60)

    init_db()

    print()
    print("Database initialized successfully.")

    print()
    print("Database file:")
    print(DATABASE_FILE)

    print()
    print("Stored trades:")
    print(get_trade_count())

    print()
    print("Total profit:")
    print(f"₹{get_total_profit():.2f}")

    print()
    print("Database test completed successfully.")