from datetime import datetime

from database.database import save_position, clear_position
from database.trade_history import save_trade


# ============================================================
# CRYPTOAI PRO - PAPER TRADER
# ============================================================


class PaperTrader:

    def __init__(self, balance):

        self.initial_balance = float(balance)
        self.balance = float(balance)
        self.position = None


    # ========================================================
    # BUY
    # ========================================================

    def buy(
        self,
        coin,
        price,
        quantity,
        stop_loss_price,
        take_profit_price=None
    ):
        """
        Open a paper-trading position.

        IMPORTANT:
        Position sizing is NOT calculated here.

        The quantity must already be calculated and approved
        by risk.risk_manager before calling this method.
        """

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if self.position is not None:

            return {
                "success": False,
                "message": "Already holding a position."
            }


        try:

            price = float(price)
            quantity = float(quantity)
            stop_loss_price = float(
                stop_loss_price
            )

            if take_profit_price is not None:

                take_profit_price = float(
                    take_profit_price
                )

        except (TypeError, ValueError):

            return {
                "success": False,
                "message": "Invalid trade values."
            }


        if price <= 0:

            return {
                "success": False,
                "message": "Invalid entry price."
            }


        if quantity <= 0:

            return {
                "success": False,
                "message": "Invalid trade quantity."
            }


        if stop_loss_price <= 0:

            return {
                "success": False,
                "message": "Invalid stop-loss price."
            }


        if stop_loss_price >= price:

            return {
                "success": False,
                "message": (
                    "Stop-loss must be below "
                    "the BUY price."
                )
            }


        if (
            take_profit_price is not None
            and
            take_profit_price <= price
        ):

            return {
                "success": False,
                "message": (
                    "Take-profit must be above "
                    "the BUY price."
                )
            }


        # ----------------------------------------------------
        # POSITION VALUE
        # ----------------------------------------------------

        position_value = (
            quantity * price
        )


        if position_value <= 0:

            return {
                "success": False,
                "message": "Invalid position value."
            }


        if position_value > self.balance:

            return {
                "success": False,
                "message": (
                    "Insufficient paper-trading balance."
                )
            }


        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        buy_time = datetime.now().isoformat(
            sep=" ",
            timespec="seconds"
        )


        # ----------------------------------------------------
        # RESERVE PAPER BALANCE
        # ----------------------------------------------------

        self.balance -= position_value


        # ----------------------------------------------------
        # CREATE POSITION
        # ----------------------------------------------------

        self.position = {

            "coin":
                coin,

            "buy_price":
                price,

            "amount":
                quantity,

            "position_value":
                position_value,

            "stop_loss_price":
                stop_loss_price,

            "take_profit_price":
                take_profit_price,

            "opened_at":
                buy_time
        }


        # ----------------------------------------------------
        # SAVE ACTIVE POSITION
        # ----------------------------------------------------

        try:

            save_position(
                coin,
                price,
                quantity,
                position_value,
                stop_loss_price,
                buy_time
            )

        except Exception as error:

            # Restore balance because opening the position
            # was not successfully persisted.

            self.balance += position_value
            self.position = None

            return {
                "success": False,
                "message": (
                    "Could not save paper position: "
                    f"{error}"
                )
            }


        # ----------------------------------------------------
        # SAVE BUY HISTORY
        # ----------------------------------------------------

        try:

            save_trade({

                "action":
                    "BUY",

                "coin":
                    coin,

                "price":
                    price,

                "amount":
                    quantity,

                "profit":
                    0,

                "profit_percent":
                    0
            })

        except Exception as error:

            print(
                "Trade-history warning: "
                f"{error}"
            )


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return {

            "success":
                True,

            "action":
                "BUY",

            "coin":
                coin,

            "price":
                price,

            "amount":
                quantity,

            "position_value":
                round(
                    position_value,
                    2
                ),

            "remaining_balance":
                round(
                    self.balance,
                    2
                ),

            "stop_loss_price":
                stop_loss_price,

            "take_profit_price":
                take_profit_price,

            "opened_at":
                buy_time
        }


    # ========================================================
    # RESTORE POSITION
    # ========================================================

    def restore_position(
        self,
        coin,
        buy_price,
        amount,
        position_value=None,
        stop_loss_price=None,
        opened_at=None,
        take_profit_price=None
    ):
        """
        Restore an existing paper position from database.
        """

        buy_price = float(
            buy_price
        )

        amount = float(
            amount
        )


        if position_value is None:

            position_value = (
                buy_price * amount
            )

        else:

            position_value = float(
                position_value
            )


        self.position = {

            "coin":
                coin,

            "buy_price":
                buy_price,

            "amount":
                amount,

            "position_value":
                position_value,

            "stop_loss_price":
                stop_loss_price,

            "take_profit_price":
                take_profit_price,

            "opened_at":
                opened_at
        }


        self.balance = max(
            0.0,
            self.initial_balance
            - position_value
        )


    # ========================================================
    # SELL
    # ========================================================

    def sell(
        self,
        price,
        reason="MANUAL"
    ):
        """
        Close the current paper-trading position.
        """

        if self.position is None:

            return {
                "success": False,
                "message": "No open position."
            }


        try:

            price = float(
                price
            )

        except (TypeError, ValueError):

            return {
                "success": False,
                "message": "Invalid sell price."
            }


        if price <= 0:

            return {
                "success": False,
                "message": "Invalid sell price."
            }


        # ----------------------------------------------------
        # POSITION INFORMATION
        # ----------------------------------------------------

        coin = self.position[
            "coin"
        ]

        buy_price = float(
            self.position[
                "buy_price"
            ]
        )

        amount = float(
            self.position[
                "amount"
            ]
        )

        position_value = float(
            self.position.get(
                "position_value"
            )
            or
            (
                buy_price
                * amount
            )
        )


        # ----------------------------------------------------
        # SELL VALUE
        # ----------------------------------------------------

        sell_value = (
            amount * price
        )


        # ----------------------------------------------------
        # PROFIT / LOSS
        # ----------------------------------------------------

        profit = (
            sell_value
            - position_value
        )


        profit_percent = (

            (
                profit
                / position_value
            )
            * 100

            if position_value > 0

            else 0
        )


        # ----------------------------------------------------
        # RETURN MONEY TO PAPER BALANCE
        # ----------------------------------------------------

        self.balance += (
            sell_value
        )


        # ----------------------------------------------------
        # SAVE SELL HISTORY
        # ----------------------------------------------------

        try:

            save_trade({

                "action":
                    "SELL",

                "coin":
                    coin,

                "price":
                    price,

                "amount":
                    amount,

                "profit":
                    round(
                        profit,
                        2
                    ),

                "profit_percent":
                    round(
                        profit_percent,
                        2
                    )
            })

        except Exception as error:

            print(
                "Trade-history warning: "
                f"{error}"
            )


        # ----------------------------------------------------
        # CLEAR DATABASE POSITION
        # ----------------------------------------------------

        try:

            clear_position()

        except Exception as error:

            print(
                "Database clear warning: "
                f"{error}"
            )


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        result = {

            "success":
                True,

            "action":
                "SELL",

            "reason":
                reason,

            "coin":
                coin,

            "buy_price":
                buy_price,

            "sell_price":
                price,

            "amount":
                amount,

            "position_value":
                round(
                    position_value,
                    2
                ),

            "sell_value":
                round(
                    sell_value,
                    2
                ),

            "profit":
                round(
                    profit,
                    2
                ),

            "profit_percent":
                round(
                    profit_percent,
                    2
                ),

            "balance":
                round(
                    self.balance,
                    2
                )
        }


        self.position = None


        return result


    # ========================================================
    # CHECK STOP LOSS / TAKE PROFIT
    # ========================================================

    def check_exit(
        self,
        current_price
    ):
        """
        Check whether the current position has reached
        stop-loss or take-profit.

        Returns:
            sell result if an exit occurs,
            otherwise None.
        """

        if self.position is None:

            return None


        try:

            current_price = float(
                current_price
            )

        except (TypeError, ValueError):

            return None


        stop_loss = (
            self.position.get(
                "stop_loss_price"
            )
        )

        take_profit = (
            self.position.get(
                "take_profit_price"
            )
        )


        # ----------------------------------------------------
        # STOP LOSS
        # ----------------------------------------------------

        if (
            stop_loss is not None
            and
            current_price
            <= float(stop_loss)
        ):

            return self.sell(
                current_price,
                reason="STOP_LOSS"
            )


        # ----------------------------------------------------
        # TAKE PROFIT
        # ----------------------------------------------------

        if (
            take_profit is not None
            and
            current_price
            >= float(take_profit)
        ):

            return self.sell(
                current_price,
                reason="TAKE_PROFIT"
            )


        return None


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CRYPTOAI PRO - PAPER TRADER TEST")
    print("=" * 60)

    trader = PaperTrader(
        200
    )

    test_price = 2636.50

    test_quantity = (
        50 / test_price
    )

    test_stop_loss = (
        test_price * 0.97
    )

    test_take_profit = (
        test_price * 1.06
    )


    print()
    print("Opening test paper trade...")

    result = trader.buy(

        coin="ETHUSDT",

        price=test_price,

        quantity=test_quantity,

        stop_loss_price=test_stop_loss,

        take_profit_price=test_take_profit
    )

    print(
        result
    )


    if result.get(
        "success"
    ):

        print()
        print(
            "Paper position opened successfully."
        )

        print(
            f"Position value: "
            f"${result['position_value']:.2f}"
        )

        print(
            f"Remaining balance: "
            f"${result['remaining_balance']:.2f}"
        )


        print()
        print(
            "Simulating take-profit..."
        )

        exit_result = trader.check_exit(
            test_take_profit
        )

        print(
            exit_result
        )


    print()
    print("=" * 60)
    print("PAPER TRADER TEST COMPLETE")
    print("=" * 60)