from api.coindcx_api import get_historical_candles
from backtesting.backtester import Backtester


# ==========================================
# SETTINGS
# ==========================================

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "LSKUSDT",
    "STEEMUSDT",
    "ARKUSDT",
    "AVAUSDT",
    "POWRUSDT"
]

CANDLE_LIMIT = 5000
INTERVAL = "1m"

STARTING_BALANCE = 200.0


# ==========================================
# BACKTEST ONE COIN
# ==========================================

def backtest_coin(symbol):

    print()
    print("=" * 60)
    print(f"BACKTESTING {symbol}")
    print("=" * 60)

    try:

        # ----------------------------------
        # Download historical candles
        # ----------------------------------

        candles = get_historical_candles(
            symbol,
            interval=INTERVAL,
            total_limit=CANDLE_LIMIT
        )

        if not candles:

            print(
                f"No candle data available for {symbol}"
            )

            return None

        print(
            f"Downloaded {len(candles)} candles."
        )

        # ----------------------------------
        # Run backtest
        # ----------------------------------

        backtester = Backtester(
            candles
        )

        backtester.run()

        # ----------------------------------
        # Completed trades
        # ----------------------------------

        completed = [
            trade
            for trade in backtester.trades
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

        trade_count = len(
            completed
        )

        if trade_count > 0:

            win_rate = (
                len(winners)
                / trade_count
            ) * 100

        else:

            win_rate = 0.0

        # ----------------------------------
        # Maximum drawdown
        # ----------------------------------

        peak = STARTING_BALANCE
        max_drawdown = 0.0

        for equity in backtester.equity_history:

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

        # ----------------------------------
        # Result
        # ----------------------------------

        result = {
            "symbol": symbol,
            "ending_balance": backtester.balance,
            "profit": total_profit,
            "trades": trade_count,
            "wins": len(winners),
            "losses": len(losers),
            "win_rate": win_rate,
            "max_drawdown": max_drawdown,
            "candles": len(candles)
        }

        print(
            f"{symbol} finished."
        )

        print(
            f"Ending balance: "
            f"{backtester.balance:.2f}"
        )

        print(
            f"Profit: "
            f"{total_profit:.2f}"
        )

        print(
            f"Trades: "
            f"{trade_count}"
        )

        print(
            f"Win rate: "
            f"{win_rate:.2f}%"
        )

        print(
            f"Max drawdown: "
            f"{max_drawdown:.2f}%"
        )

        return result

    except Exception as e:

        print(
            f"Backtest failed for "
            f"{symbol}: {e}"
        )

        return None


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print(
        "Starting fixed-basket "
        "multi-coin backtest..."
    )

    print()
    print("Coins:")

    for symbol in SYMBOLS:

        print(
            f"- {symbol}"
        )

    print()
    print(
        f"Historical candle target: "
        f"{CANDLE_LIMIT}"
    )

    results = []

    # ======================================
    # RUN ALL COINS
    # ======================================

    for symbol in SYMBOLS:

        result = backtest_coin(
            symbol
        )

        if result is not None:

            results.append(
                result
            )

    # ======================================
    # SUMMARY
    # ======================================

    print()
    print("=" * 95)
    print(
        "FIXED-BASKET BACKTEST SUMMARY"
    )
    print("=" * 95)

    if not results:

        print(
            "No successful backtests."
        )

    else:

        print(
            f"{'Symbol':12}"
            f"{'Candles':10}"
            f"{'End Balance':14}"
            f"{'Profit':12}"
            f"{'Trades':10}"
            f"{'Win Rate':12}"
            f"{'Drawdown':12}"
        )

        print(
            "-" * 95
        )

        for result in results:

            print(
                f"{result['symbol']:12}"
                f"{result['candles']:10}"
                f"{result['ending_balance']:14.2f}"
                f"{result['profit']:12.2f}"
                f"{result['trades']:10}"
                f"{result['win_rate']:11.2f}%"
                f"{result['max_drawdown']:11.2f}%"
            )

        # ==================================
        # OVERALL STATISTICS
        # ==================================

        total_profit = sum(
            result["profit"]
            for result in results
        )

        total_trades = sum(
            result["trades"]
            for result in results
        )

        total_wins = sum(
            result["wins"]
            for result in results
        )

        total_losses = sum(
            result["losses"]
            for result in results
        )

        profitable_coins = sum(
            1
            for result in results
            if result["profit"] > 0
        )

        losing_coins = sum(
            1
            for result in results
            if result["profit"] < 0
        )

        if total_trades > 0:

            overall_win_rate = (
                total_wins
                / total_trades
            ) * 100

        else:

            overall_win_rate = 0.0

        print()
        print(
            "-" * 95
        )

        print(
            f"Total tested coins: "
            f"{len(results)}"
        )

        print(
            f"Total simulated profit: "
            f"{total_profit:.2f}"
        )

        print(
            f"Total completed trades: "
            f"{total_trades}"
        )

        print(
            f"Total wins: "
            f"{total_wins}"
        )

        print(
            f"Total losses: "
            f"{total_losses}"
        )

        print(
            f"Overall win rate: "
            f"{overall_win_rate:.2f}%"
        )

        print(
            f"Profitable coins: "
            f"{profitable_coins}"
        )

        print(
            f"Loss-making coins: "
            f"{losing_coins}"
        )

    print(
        "=" * 95
    )