import sqlite3


connection = sqlite3.connect("cryptoai.db")

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
    """
)

rows = cursor.fetchall()

print("\nTrades in SQLite:\n")

for row in rows:
    print(row)

connection.close()