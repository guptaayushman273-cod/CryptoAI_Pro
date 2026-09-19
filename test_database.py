from database.database import init_db
from database.trade_history import save_trade


# ==========================================
# INITIALIZE DATABASE
# ==========================================

init_db()

print("Database initialized.")


# ==========================================
# TEST TRADE
# ==========================================

test_trade = {
    "action": "BUY",
    "coin": "TESTUSDT",
    "price": 100.0,
    "amount": 2.0
}


save_trade(test_trade)

print("Test trade saved successfully.")