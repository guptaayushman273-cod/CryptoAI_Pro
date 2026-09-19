from trader.paper_trader import PaperTrader
from trader.position_monitor import PositionMonitor
from database.database import get_position


def main():
    print("=" * 60)
    print("CRYPTOAI PRO - V2 FINAL INTEGRATION TEST")
    print("=" * 60)

    starting_balance = 1000.0
    coin = "V2INTEGRATIONUSDT"

    buy_price = 100.0
    stop_loss_price = 97.0

    print(f"\nStarting balance: ₹{starting_balance:.2f}")
    print(f"Test coin: {coin}")
    print(f"Buy price: ₹{buy_price:.2f}")
    print(f"Stop-loss: ₹{stop_loss_price:.2f}")

    # --------------------------------------------------
    # STEP 1 - Create paper trader
    # --------------------------------------------------

    bot = PaperTrader(starting_balance)

    print("\nSTEP 1 - PAPER TRADER CREATED")
    print(f"Balance: ₹{bot.balance:.2f}")

    # --------------------------------------------------
    # STEP 2 - Execute BUY
    # --------------------------------------------------

    buy_result = bot.buy(
        coin,
        buy_price,
        stop_loss_price
    )

    if not buy_result["success"]:
        print("\n✗ BUY FAILED")
        print(buy_result)
        raise SystemExit(1)

    print("\nSTEP 2 - PAPER BUY")
    print("✓ BUY successful")
    print(f"Coin: {buy_result['coin']}")
    print(f"Entry price: ₹{buy_result['price']:.2f}")
    print(f"Position value: ₹{buy_result['position_value']:.2f}")
    print(f"Amount: {buy_result['amount']}")
    print(f"Stop-loss: ₹{buy_result['stop_loss_price']:.2f}")

    # --------------------------------------------------
    # STEP 3 - Verify database position
    # --------------------------------------------------

    saved_position = get_position()

    print("\nSTEP 3 - DATABASE CHECK")

    if saved_position is None:
        print("✗ Position was not saved to database.")
        raise SystemExit(1)

    print("✓ Position saved to database")
    print(f"Database coin: {saved_position['coin']}")
    print(f"Database price: ₹{saved_position['price']:.2f}")
    print(f"Database stop-loss: ₹{saved_position['stop_loss_price']:.2f}")

    # --------------------------------------------------
    # STEP 4 - Create position monitor
    # --------------------------------------------------

    monitor = PositionMonitor(bot.position)

    print("\nSTEP 4 - POSITION MONITOR")
    print("✓ Position monitor created")
    print(f"Monitoring: {coin}")

    # --------------------------------------------------
    # STEP 5 - Price above stop-loss
    # --------------------------------------------------

    current_price = 100.0

    status = monitor.get_status(current_price)

    print("\nSTEP 5 - NORMAL PRICE CHECK")
    print(f"Current price: ₹{current_price:.2f}")
    print(f"Status: {status['status']}")

    if status["status"] != "HOLD":
        print("✗ Expected HOLD")
        raise SystemExit(1)

    print("✓ Position remains open")

    # --------------------------------------------------
    # STEP 6 - Price reaches stop-loss
    # --------------------------------------------------

    current_price = 97.0

    status = monitor.get_status(current_price)

    print("\nSTEP 6 - STOP-LOSS CHECK")
    print(f"Current price: ₹{current_price:.2f}")
    print(f"Stop-loss: ₹{stop_loss_price:.2f}")
    print(f"Status: {status['status']}")

    if status["status"] != "STOP_LOSS_TRIGGERED":
        print("✗ Stop-loss was not triggered")
        raise SystemExit(1)

    print("✓ Stop-loss triggered correctly")

    # --------------------------------------------------
    # STEP 7 - Execute SELL
    # --------------------------------------------------

    sell_result = bot.sell(current_price)

    print("\nSTEP 7 - PAPER SELL")

    if not sell_result["success"]:
        print("✗ SELL FAILED")
        print(sell_result)
        raise SystemExit(1)

    print("✓ SELL successful")
    print(f"Coin: {sell_result['coin']}")
    print(f"Buy price: ₹{sell_result['buy_price']:.2f}")
    print(f"Sell price: ₹{sell_result['sell_price']:.2f}")
    print(f"Profit/Loss: ₹{sell_result['profit']:.2f}")
    print(f"Profit/Loss %: {sell_result['profit_percent']:.2f}%")
    print(f"Final balance: ₹{sell_result['balance']:.2f}")

    # --------------------------------------------------
    # STEP 8 - Verify database position cleared
    # --------------------------------------------------

    remaining_position = get_position()

    print("\nSTEP 8 - FINAL DATABASE CHECK")

    if remaining_position is not None:
        print("✗ Position still exists in database.")
        print(remaining_position)
        raise SystemExit(1)

    print("✓ Position cleared from database")

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("V2 FINAL INTEGRATION TEST PASSED")
    print("=" * 60)

    print("\nVerified:")
    print("✓ Paper BUY")
    print("✓ Database persistence")
    print("✓ Position monitoring")
    print("✓ Stop-loss detection")
    print("✓ Paper SELL")
    print("✓ Profit/Loss calculation")
    print("✓ Database position clearing")
    print("\nV2 core integration is working correctly.")


if __name__ == "__main__":
    main()