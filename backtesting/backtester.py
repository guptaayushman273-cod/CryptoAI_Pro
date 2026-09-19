from dataclasses import dataclass

from api.coindcx_api import get_candles
from indicators.indicators import calculate_indicators
from strategy.decision_engine import make_decision


# ==========================================
# SETTINGS
# ==========================================

SYMBOL = "LSKUSDT"
INTERVAL = "1m"
CANDLE_LIMIT = 1000

STARTING_BALANCE = 200.0

TAKE_PROFIT_PERCENT = 5.0
STOP_LOSS_PERCENT = -3.0

FEE_RATE = 0.002


# ==========================================
# TRADE RECORD
# ==========================================

@dataclass
class Trade:

    action: str
    price: float
    amount: float
    profit: float = 0.0
    profit_percent: float = 0.0
    reason: str = ""


# ==========================================
# MARKET SCORE
# ==========================================

def calculate_market_score(change, volume):

    score = 0

    if change > 50:
        score += 50

    elif change > 20:
        score += 40

    elif change > 10:
        score += 30

    elif change > 5:
        score += 20

    if volume > 10000:
        score += 30

    return score


# ==========================================
# BACKTESTER
# ==========================================

class Backtester:

    def __init__(self, candles):

        self.candles = sorted(
            candles,
            key=lambda candle: candle["time"]
        )

        self.balance = STARTING_BALANCE
        self.position = None

        self.trades = []
        self.equity_history = []

    # ======================================
    # BUY
    # ======================================

    def buy(self, price):

        if self.position is not None:
            return

        if self.balance <= 0:
            return

        total_cost_per_unit = (
            price * (1 + FEE_RATE)
        )

        amount = (
            self.balance
            / total_cost_per_unit
        )

        buy_value = price * amount
        buy_fee = buy_value * FEE_RATE

        total_cost = (
            buy_value + buy_fee
        )

        if total_cost > self.balance:
            return

        self.balance -= total_cost

        self.position = {
            "price": price,
            "amount": amount,
            "buy_value": buy_value,
            "buy_fee": buy_fee
        }

        self.trades.append(
            Trade(
                action="BUY",
                price=price,
                amount=amount
            )
        )

    # ======================================
    # SELL
    # ======================================

    def sell(self, price, reason):

        if self.position is None:
            return

        buy_price = self.position["price"]
        amount = self.position["amount"]
        buy_value = self.position["buy_value"]
        buy_fee = self.position["buy_fee"]

        sell_value = price * amount
        sell_fee = sell_value * FEE_RATE

        net_sell_value = (
            sell_value - sell_fee
        )

        profit = (
            net_sell_value
            - buy_value
            - buy_fee
        )

        profit_percent = (
            profit
            / (buy_value + buy_fee)
        ) * 100

        self.balance += net_sell_value

        self.trades.append(
            Trade(
                action="SELL",
                price=price,
                amount=amount,
                profit=profit,
                profit_percent=profit_percent,
                reason=reason
            )
        )

        self.position = None

    # ======================================
    # EQUITY
    # ======================================

    def current_equity(self, price):

        if self.position is None:
            return self.balance

        position_value = (
            self.position["amount"]
            * price
        )

        estimated_exit_fee = (
            position_value
            * FEE_RATE
        )

        return (
            self.balance
            + position_value
            - estimated_exit_fee
        )

    # ======================================
    # RUN
    # ======================================

    def run(self):

        print(
            f"Starting backtest with "
            f"{len(self.candles)} candles..."
        )

        for index in range(
            50,
            len(self.candles)
        ):

            candle = self.candles[index]

            open_price = float(
                candle["open"]
            )

            high_price = float(
                candle["high"]
            )

            low_price = float(
                candle["low"]
            )

            close_price = float(
                candle["close"]
            )

            # ==================================
            # OPEN POSITION
            # ==================================

            if self.position is not None:

                entry_price = (
                    self.position["price"]
                )

                stop_price = (
                    entry_price
                    * (1 + STOP_LOSS_PERCENT / 100)
                )

                target_price = (
                    entry_price
                    * (1 + TAKE_PROFIT_PERCENT / 100)
                )

                stop_hit = (
                    low_price <= stop_price
                )

                target_hit = (
                    high_price >= target_price
                )

                # ----------------------------------
                # BOTH HIT IN THE SAME CANDLE
                # ----------------------------------

                if stop_hit and target_hit:

                    # We do not know which happened
                    # first from OHLC data alone.
                    #
                    # Use the conservative assumption:
                    # stop-loss happened first.

                    self.sell(
                        stop_price,
                        "STOP_LOSS_SAME_CANDLE"
                    )

                elif stop_hit:

                    self.sell(
                        stop_price,
                        "STOP_LOSS"
                    )

                elif target_hit:

                    self.sell(
                        target_price,
                        "TAKE_PROFIT"
                    )

            # ==================================
            # NEW ENTRY
            # ==================================

            if self.position is None:

                historical_candles = (
                    self.candles[:index + 1]
                )

                indicators = calculate_indicators(
                    historical_candles
                )

                if (
                    indicators is None
                    or indicators.empty
                ):
                    continue

                previous_candle = (
                    self.candles[index - 1]
                )

                previous_close = float(
                    previous_candle["close"]
                )

                if previous_close <= 0:
                    continue

                change_percent = (
                    (
                        close_price
                        - previous_close
                    )
                    / previous_close
                ) * 100

                volume = float(
                    candle["volume"]
                )

                market_score = (
                    calculate_market_score(
                        change_percent,
                        volume
                    )
                )

                decision = make_decision(
                    market_score=market_score,
                    news_score=0,
                    fee_ok=True,
                    indicators=indicators
                )

                if (
                    decision["decision"]
                    == "BUY CANDIDATE 🟢"
                ):

                    self.buy(close_price)

            # ==================================
            # EQUITY
            # ==================================

            equity = self.current_equity(
                close_price
            )

            self.equity_history.append(
                equity
            )

        # ======================================
        # CLOSE FINAL POSITION
        # ======================================

        if self.position is not None:

            final_price = float(
                self.candles[-1]["close"]
            )

            self.sell(
                final_price,
                "END_OF_BACKTEST"
            )

            self.equity_history.append(
                self.balance
            )

        print("Backtest completed.")

    # ======================================
    # RESULTS
    # ======================================

    def results(self):

        completed = [
            trade
            for trade in self.trades
            if trade.action == "SELL"
        ]

        winners = [
            trade
            for trade in completed
            if trade.profit > 0
        ]

        losers = [
            trade
            for trade in completed
            if trade.profit <= 0
        ]

        total_profit = sum(
            trade.profit
            for trade in completed
        )

        trade_count = len(completed)

        win_rate = (
            len(winners) / trade_count * 100
            if trade_count > 0
            else 0
        )

        # ==================================
        # MAX DRAWDOWN
        # ==================================

        peak = STARTING_BALANCE
        max_drawdown = 0.0

        for equity in self.equity_history:

            if equity > peak:
                peak = equity

            if peak > 0:

                drawdown = (
                    (peak - equity)
                    / peak
                ) * 100

                max_drawdown = max(
                    max_drawdown,
                    drawdown
                )

        # ==================================
        # TRADE DETAILS
        # ==================================

        print()
        print("=" * 60)
        print("COMPLETED TRADES")
        print("=" * 60)

        for number, trade in enumerate(
            completed,
            start=1
        ):

            result_type = (
                "WIN"
                if trade.profit > 0
                else "LOSS"
            )

            print(
                f"Trade {number}: "
                f"{result_type} | "
                f"Sell: {trade.price:.6f} | "
                f"Profit: {trade.profit:.2f} | "
                f"{trade.profit_percent:.2f}% | "
                f"{trade.reason}"
            )

        # ==================================
        # SUMMARY
        # ==================================

        print()
        print("=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)

        print(
            f"Starting balance: "
            f"{STARTING_BALANCE:.2f}"
        )

        print(
            f"Ending balance: "
            f"{self.balance:.2f}"
        )

        print(
            f"Total profit: "
            f"{total_profit:.2f}"
        )

        print(
            f"Completed trades: "
            f"{trade_count}"
        )

        print(
            f"Winning trades: "
            f"{len(winners)}"
        )

        print(
            f"Losing trades: "
            f"{len(losers)}"
        )

        print(
            f"Win rate: "
            f"{win_rate:.2f}%"
        )

        print(
            f"Maximum drawdown: "
            f"{max_drawdown:.2f}%"
        )

        print("=" * 60)


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print(
        f"Downloading historical candles "
        f"for {SYMBOL}..."
    )

    candles = get_candles(
        SYMBOL,
        interval=INTERVAL,
        limit=CANDLE_LIMIT
    )

    if not candles:

        print("No candle data received.")

    else:

        print(
            f"Downloaded {len(candles)} candles."
        )

        print(
            "Oldest candle time:",
            min(
                candle["time"]
                for candle in candles
            )
        )

        print(
            "Newest candle time:",
            max(
                candle["time"]
                for candle in candles
            )
        )

        backtester = Backtester(
            candles
        )

        backtester.run()

        backtester.results()