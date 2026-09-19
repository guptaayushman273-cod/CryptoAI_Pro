class PositionMonitor:
    """
    Monitors an open paper-trading position.

    The monitor checks whether the current market price
    has reached or crossed the position's stop-loss price.
    """

    def __init__(self, position):
        self.position = position

    def is_position_open(self):
        """
        Check whether a valid position exists.
        """

        return self.position is not None

    def get_stop_loss_price(self):
        """
        Return the stop-loss price of the current position.
        """

        if not self.is_position_open():
            return None

        return self.position.get("stop_loss_price")

    def check_stop_loss(self, current_price):
        """
        Check whether the stop-loss has been triggered.

        Returns True when:
            current_price <= stop_loss_price

        Returns False otherwise.
        """

        if not self.is_position_open():
            return False

        stop_loss_price = self.get_stop_loss_price()

        if stop_loss_price is None:
            return False

        if current_price <= 0:
            return False

        return current_price <= stop_loss_price

    def get_status(self, current_price):
        """
        Return a simple status describing the position.
        """

        if not self.is_position_open():
            return {
                "status": "NO_POSITION",
                "current_price": current_price,
                "stop_loss_price": None
            }

        stop_loss_price = self.get_stop_loss_price()

        if stop_loss_price is None:
            return {
                "status": "NO_STOP_LOSS",
                "current_price": current_price,
                "stop_loss_price": None
            }

        if current_price <= stop_loss_price:
            return {
                "status": "STOP_LOSS_TRIGGERED",
                "current_price": current_price,
                "stop_loss_price": stop_loss_price
            }

        return {
            "status": "HOLD",
            "current_price": current_price,
            "stop_loss_price": stop_loss_price
        }


if __name__ == "__main__":
    print("=" * 60)
    print("CRYPTOAI PRO - POSITION MONITOR TEST")
    print("=" * 60)

    test_position = {
        "coin": "V2TESTUSDT",
        "buy_price": 100.0,
        "amount": 4.0,
        "position_value": 400.0,
        "stop_loss_price": 97.0,
        "opened_at": "2026-09-14 12:00:00"
    }

    monitor = PositionMonitor(test_position)

    print("\nTEST POSITION")
    print(f"Coin: {test_position['coin']}")
    print(f"Buy price: ₹{test_position['buy_price']}")
    print(f"Stop-loss: ₹{test_position['stop_loss_price']}")

    # Test 1: Price above stop-loss
    current_price = 100.0

    status = monitor.get_status(current_price)

    print("\nTEST 1")
    print(f"Current price: ₹{current_price}")
    print(f"Status: {status['status']}")

    if status["status"] == "HOLD":
        print("✓ Correct: position should remain open.")
    else:
        print("✗ ERROR: Expected HOLD.")
        raise SystemExit(1)

    # Test 2: Price exactly at stop-loss
    current_price = 97.0

    status = monitor.get_status(current_price)

    print("\nTEST 2")
    print(f"Current price: ₹{current_price}")
    print(f"Status: {status['status']}")

    if status["status"] == "STOP_LOSS_TRIGGERED":
        print("✓ Correct: stop-loss triggered.")
    else:
        print("✗ ERROR: Expected STOP_LOSS_TRIGGERED.")
        raise SystemExit(1)

    # Test 3: Price below stop-loss
    current_price = 95.0

    status = monitor.get_status(current_price)

    print("\nTEST 3")
    print(f"Current price: ₹{current_price}")
    print(f"Status: {status['status']}")

    if status["status"] == "STOP_LOSS_TRIGGERED":
        print("✓ Correct: stop-loss triggered.")
    else:
        print("✗ ERROR: Expected STOP_LOSS_TRIGGERED.")
        raise SystemExit(1)

    print("\n" + "=" * 60)
    print("POSITION MONITOR TEST PASSED.")
    print("=" * 60)