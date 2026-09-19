from trader.paper_trader import PaperTrader
from database.database import get_position


print("=" * 60)
print("CRYPTOAI PRO - SELL EXECUTION TEST")
print("=" * 60)


# --------------------------------------------------
# STEP 1: Check existing database position
# --------------------------------------------------

saved_position = get_position()

if saved_position is None:
    print("ERROR: No open position found in database.")
    print("Run the V2 BUY test first.")
    raise SystemExit(1)


print("\nDATABASE POSITION FOUND")
print(f"Coin: {saved_position['coin']}")
print(f"Buy price: {saved_position['price']}")
print(f"Amount: {saved_position['amount']}")
print(f"Position value: {saved_position['position_value']}")
print(f"Stop-loss: {saved_position['stop_loss_price']}")


# --------------------------------------------------
# STEP 2: Restore position into PaperTrader
# --------------------------------------------------

initial_balance = 1000.0

bot = PaperTrader(initial_balance)

bot.restore_position(
    coin=saved_position["coin"],
    buy_price=saved_position["price"],
    amount=saved_position["amount"],
    position_value=saved_position["position_value"],
    stop_loss_price=saved_position["stop_loss_price"],
    opened_at=saved_position["opened_at"]
)

print("\nPOSITION RESTORED")
print(f"PaperTrader position: {bot.position}")
print(f"Available balance: ₹{bot.balance:.2f}")


# --------------------------------------------------
# STEP 3: Simulate SELL
# --------------------------------------------------

sell_price = saved_position["price"] * 1.05

print("\nSELL TEST")
print(f"Buy price: ₹{saved_position['price']}")
print(f"Simulated sell price: ₹{sell_price:.2f}")


result = bot.sell(sell_price)


# --------------------------------------------------
# STEP 4: Display SELL result
# --------------------------------------------------

print("\nSELL RESULT")

if result["success"]:
    print("PAPER SELL SUCCESSFUL.")
    print(f"Coin: {result['coin']}")
    print(f"Buy price: ₹{result['buy_price']}")
    print(f"Sell price: ₹{result['sell_price']}")
    print(f"Amount: {result['amount']}")
    print(f"Position value: ₹{result['position_value']:.2f}")
    print(f"Sell value: ₹{result['sell_value']:.2f}")
    print(f"Profit: ₹{result['profit']:.2f}")
    print(f"Profit %: {result['profit_percent']:.2f}%")
    print(f"Final balance: ₹{result['balance']:.2f}")
else:
    print("PAPER SELL FAILED.")
    print(result["message"])
    raise SystemExit(1)


# --------------------------------------------------
# STEP 5: Check database position
# --------------------------------------------------

print("\nDATABASE CHECK")

remaining_position = get_position()

if remaining_position is None:
    print("✓ Open position removed from database.")
else:
    print("✗ Position still exists in database.")
    print(remaining_position)
    raise SystemExit(1)


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print("\n" + "=" * 60)
print("V2 SELL EXECUTION TEST RESULT")
print("=" * 60)

print("✓ Position restored")
print("✓ PaperTrader SELL executed")
print("✓ Profit calculated")
print("✓ SELL trade processed")
print("✓ Open position cleared from database")

print("\nV2 SELL execution test PASSED.")
print("=" * 60)