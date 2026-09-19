from datetime import datetime

from risk.risk_control import calculate_position_size
from database.database import save_position, clear_position
from database.trade_history import save_trade


class PaperTrader:
    def __init__(self, balance):
        self.initial_balance = balance
        self.balance = balance
        self.position = None

    def buy(self, coin, price, stop_loss_price):
        if self.position is not None:
            return {
                "success": False,
                "message": "Already holding a coin"
            }

        if price <= 0:
            return {
                "success": False,
                "message": "Invalid entry price"
            }

        if stop_loss_price <= 0:
            return {
                "success": False,
                "message": "Invalid stop-loss price"
            }

        position_value = calculate_position_size(
            self.balance,
            price,
            stop_loss_price
        )

        if position_value <= 0:
            return {
                "success": False,
                "message": "Calculated position size is zero"
            }

        if position_value > self.balance:
            return {
                "success": False,
                "message": "Insufficient available balance"
            }

        amount = position_value / price

        buy_time = datetime.now().isoformat(
            sep=" ",
            timespec="seconds"
        )

        # Reserve money for the open position.
        self.balance -= position_value

        self.position = {
            "coin": coin,
            "buy_price": price,
            "amount": amount,
            "position_value": position_value,
            "stop_loss_price": stop_loss_price,
            "opened_at": buy_time
        }

        # Save the currently open position.
        save_position(
            coin,
            price,
            amount,
            position_value,
            stop_loss_price,
            buy_time
        )

        # Save BUY event in trade history.
        save_trade({
            "action": "BUY",
            "coin": coin,
            "price": price,
            "amount": amount,
            "profit": 0,
            "profit_percent": 0
        })

        return {
            "success": True,
            "action": "BUY",
            "coin": coin,
            "price": price,
            "amount": amount,
            "position_value": position_value,
            "remaining_balance": self.balance,
            "stop_loss_price": stop_loss_price
        }

    def restore_position(
        self,
        coin,
        buy_price,
        amount,
        position_value=None,
        stop_loss_price=None,
        opened_at=None
    ):
        # Legacy database records may not contain position_value.
        # Reconstruct it from entry price and amount.
        if position_value is None:
            position_value = buy_price * amount

        self.position = {
            "coin": coin,
            "buy_price": buy_price,
            "amount": amount,
            "position_value": position_value,
            "stop_loss_price": stop_loss_price,
            "opened_at": opened_at
        }

        # Reconstruct available balance after the position was opened.
        self.balance = self.initial_balance - position_value

    def sell(self, price):
        if self.position is None:
            return {
                "success": False,
                "message": "No position"
            }

        if price <= 0:
            return {
                "success": False,
                "message": "Invalid sell price"
            }

        coin = self.position["coin"]
        buy_price = self.position["buy_price"]
        amount = self.position["amount"]

        position_value = (
            self.position.get("position_value")
            or buy_price * amount
        )

        sell_value = amount * price

        profit = sell_value - position_value

        profit_percent = (
            (profit / position_value) * 100
            if position_value > 0
            else 0
        )

        # Return the position's sale value to available balance.
        self.balance += sell_value

        # Save SELL event in trade history.
        save_trade({
            "action": "SELL",
            "coin": coin,
            "price": price,
            "amount": amount,
            "profit": round(profit, 2),
            "profit_percent": round(profit_percent, 2)
        })

        # Remove the active position from the database.
        clear_position()

        result = {
            "success": True,
            "action": "SELL",
            "coin": coin,
            "buy_price": buy_price,
            "sell_price": price,
            "amount": amount,
            "position_value": position_value,
            "sell_value": sell_value,
            "profit": round(profit, 2),
            "profit_percent": round(profit_percent, 2),
            "balance": round(self.balance, 2)
        }

        self.position = None

        return result