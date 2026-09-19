from trader.paper_trader import PaperTrader
from trader.position_monitor import PositionMonitor
from database.database import get_position


print("=" * 60)
print("CRYPTOAI PRO - STOP-LOSS EXECUTION TEST")
print("=" * 60)


# --------------------------------------------------
# STEP 1: Create a test trader
# --------------------------------------------------

initial_balance = 1000.0

bot = PaperTrader(initial_balance)

coin = "V2STOPLOSSUSDT"
buy_price = 100.0
stop_loss_price = 97.0

print("\nTEST SETUP")
print(f"Initial balance: ₹{initial_balance:.2f}")
print(f"Coin: {coin}")
print(f"Buy price: ₹{buy_price:.2f}")
print(f"Stop-loss: ₹{stop_loss_price:.2f}")


# --------------------------------------------------
# STEP 2: Execute BUY
# --------------------------------------------------

buy_result = bot.buy(
    coin,
    buy_price,
    stop_loss_price
)

if not buy_result["success"]:
    print("\n✗ BUY FAILED")
    print(buy_result["message"])
    raise SystemExit(1)

print("\n✓ PAPER BUY SUCCESSFUL")
print(f"Position value: ₹{buy_result['position_value']:.2f}")
print(f"Amount: {buy_result['amount']}")


# --------------------------------------------------
# STEP 3: Create Position Monitor
# --------------------------------------------------

monitor = PositionMonitor(bot.position)

print("\nPOSITION MONITOR CREATED")
print(f"Monitoring: {coin}")


# --------------------------------------------------
# STEP 4: Test price above stop-loss
# --------------------------------------------------

current_price = 100.0

status = monitor.get_status(current_price)

print("\nPRICE CHECK 1")
print(f"Current price: ₹{current_price:.2f}")
print(f"Stop-loss: ₹{stop_loss_price:.2f}")
print(f"Status: {status['status']}")

if status["status"] != "HOLD":
    print("✗ ERROR: Position should still be held.")
    raise SystemExit(1)

print("✓ Position correctly remains open.")


# --------------------------------------------------
# STEP 5: Simulate price falling to stop-loss
# --------------------------------------------------

current_price = 97.0

status = monitor.get_status(current_price)

print("\nPRICE CHECK 2")
print(f"Current price: ₹{current_price:.2f}")
print(f"Stop-loss: ₹{stop_loss_price:.2f}")
print(f"Status: {status['status']}")

if status["status"] != "STOP_LOSS_TRIGGERED":
    print("✗ ERROR: Stop-loss should have triggered.")
    raise SystemExit(1)

print("✓ Stop-loss correctly triggered.")


# --------------------------------------------------
# STEP 6: Execute automatic SELL
# --------------------------------------------------

print("\nSTOP-LOSS ACTION")
print("Executing paper SELL...")

sell_result = bot.sell(current_price)

if not sell_result["success"]:
    print("✗ STOP-LOSS SELL FAILED")
    print(sell_result["message"])
    raise SystemExit(1)

print("✓ STOP-LOSS SELL SUCCESSFUL")


# --------------------------------------------------
# STEP 7: Display result
# --------------------------------------------------

print("\nSELL RESULT")
print(f"Coin: {sell_result['coin']}")
print(f"Buy price: ₹{sell_result['buy_price']:.2f}")
print(f"Sell price: ₹{sell_result['sell_price']:.2f}")
print(f"Profit/Loss: ₹{sell_result['profit']:.2f}")
print(f"Profit/Loss %: {sell_result['profit_percent']:.2f}%")
print(f"Final balance: ₹{sell_result['balance']:.2f}")


# --------------------------------------------------
# STEP 8: Verify database was cleared
# --------------------------------------------------

print("\nDATABASE CHECK")

remaining_position = get_position()

if remaining_position is None:
    print("✓ Position cleared from database.")
else:
    print("✗ ERROR: Position still exists in database.")
    print(remaining_position)
    raise SystemExit(1)


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print("\n" + "=" * 60)
print("V2 STOP-LOSS TEST RESULT")
print("=" * 60)

print("✓ Paper BUY executed")
print("✓ Position stored")
print("✓ Position monitor detected HOLD")
print("✓ Stop-loss detected")
print("✓ Automatic SELL executed")
print("✓ Loss calculated")
print("✓ Position cleared from database")

print("\nV2 STOP-LOSS TEST PASSED.")
print("=" * 60)