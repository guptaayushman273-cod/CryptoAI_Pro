from api.coindcx_api import get_historical_candles
from indicators.indicators import calculate_indicators
from strategy.news_ai import analyze_news
from strategy.decision_engine import make_decision
from risk.risk_control import calculate_adaptive_position_size


# ==========================================
# SETTINGS
# ==========================================

STARTING_BALANCE = 200.0

MAX_POSITION_SIZE = 0.50

TAKE_PROFIT_PERCENT = 5.0
STOP_LOSS_PERCENT = 3.0

FEE_RATE = 0.002

INTERVAL = "1m"
CANDLE_LIMIT = 5000

# After a STOP LOSS, prevent the same coin
# from being selected for this many candles.
COOLDOWN_CANDLES = 3


# ==========================================
# COINS USED IN THIS EXPERIMENT
# ==========================================
#
# POWRUSDT has been temporarily removed
# because the previous diagnostic showed:
#
# 1 win / 6 trades
# Win rate: 16.67%
#
# We are testing whether removing it improves
# the overall strategy.
#

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "LSKUSDT",
    "STEEMUSDT",
    "ARKUSDT",
    "AVAUSDT",
]


# ==========================================
# POSITION SIZE
# ==========================================

def calculate_position_size(
    balance,
    entry_price,
    stop_loss_price,
    peak_balance=None,
    losing_streak=0,
    setup_score=None,
):
    return calculate_adaptive_position_size(
        balance=balance,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        peak_balance=peak_balance,
        losing_streak=losing_streak,
        setup_score=setup_score,
    )


# ==========================================
# OPEN POSITION
# ==========================================

def open_position(
    balance,
    price,
    peak_balance=None,
    losing_streak=0,
    setup_score=None,
):
    if price <= 0:
        return None

    stop_loss_price = price * (
        1 - STOP_LOSS_PERCENT / 100
    )

    position_value = calculate_position_size(
        balance=balance,
        entry_price=price,
        stop_loss_price=stop_loss_price,
        peak_balance=peak_balance,
        losing_streak=losing_streak,
        setup_score=setup_score,
    )

    if position_value <= 0:
        return None

    buy_fee = position_value * FEE_RATE

    total_cost = position_value + buy_fee

    if total_cost > balance:
        return None

    amount = position_value / price

    return {
        "entry_price": price,
        "stop_loss_price": stop_loss_price,
        "position_value": position_value,
        "amount": amount,
        "buy_fee": buy_fee,
        "total_cost": total_cost,
    }


# ==========================================
# CLOSE POSITION
# ==========================================

def close_position(position, exit_price):
    amount = position["amount"]

    gross_sell_value = amount * exit_price

    sell_fee = gross_sell_value * FEE_RATE

    net_sell_value = gross_sell_value - sell_fee

    profit = (
        net_sell_value
        - position["total_cost"]
    )

    profit_percent = (
        profit
        / position["total_cost"]
    ) * 100

    return {
        "sell_price": exit_price,
        "gross_sell_value": gross_sell_value,
        "sell_fee": sell_fee,
        "net_sell_value": net_sell_value,
        "profit": profit,
        "profit_percent": profit_percent,
    }


# ==========================================
# CANDIDATE SELECTION
# ==========================================

def select_candidate(results):
    if not results:
        return None

    best = None

    for item in results:

        if item["decision"]["decision"] != "BUY CANDIDATE 🟢":
            continue

        if best is None:
            best = item
            continue

        if (
            item["decision"]["score"]
            > best["decision"]["score"]
        ):
            best = item

    return best


# ==========================================
# SCORE BUCKET
# ==========================================

def get_score_bucket(score):

    if score < 80:
        return "<80"

    if score < 90:
        return "80-89"

    if score < 100:
        return "90-99"

    if score < 110:
        return "100-109"

    return "110+"


# ==========================================
# DECISION DIAGNOSTICS
# ==========================================

def print_decision_diagnostics(completed_trades):

    if not completed_trades:

        print()
        print("DECISION DIAGNOSTICS")
        print("-" * 60)
        print("No completed trades available.")

        return

    diagnostic_trades = [
        trade
        for trade in completed_trades
        if "setup_score" in trade
    ]

    if not diagnostic_trades:

        print()
        print("DECISION DIAGNOSTICS")
        print("-" * 60)
        print("No diagnostic data available.")

        return

    print()
    print("=" * 60)
    print("DECISION DIAGNOSTICS")
    print("=" * 60)

    # ======================================
    # OVERALL
    # ======================================

    print()
    print("EXECUTED TRADE SETUPS")
    print("-" * 60)

    print(
        f"Diagnostic trades: "
        f"{len(diagnostic_trades)}"
    )

    avg_score = (
        sum(
            trade["setup_score"]
            for trade in diagnostic_trades
        )
        / len(diagnostic_trades)
    )

    avg_market_score = (
        sum(
            trade["market_score"]
            for trade in diagnostic_trades
        )
        / len(diagnostic_trades)
    )

    avg_rsi = (
        sum(
            trade["rsi"]
            for trade in diagnostic_trades
        )
        / len(diagnostic_trades)
    )

    avg_atr = (
        sum(
            trade["atr_percent"]
            for trade in diagnostic_trades
        )
        / len(diagnostic_trades)
    )

    avg_profit = (
        sum(
            trade["profit"]
            for trade in diagnostic_trades
        )
        / len(diagnostic_trades)
    )

    print(
        f"Average decision score : "
        f"{avg_score:.2f}"
    )

    print(
        f"Average market score   : "
        f"{avg_market_score:.2f}"
    )

    print(
        f"Average RSI            : "
        f"{avg_rsi:.2f}"
    )

    print(
        f"Average ATR %          : "
        f"{avg_atr:.2f}%"
    )

    print(
        f"Average trade P/L      : "
        f"₹{avg_profit:.2f}"
    )

    # ======================================
    # RESULT BY SCORE
    # ======================================

    print()
    print("RESULT BY DECISION SCORE")
    print("-" * 60)

    buckets = [
        "<80",
        "80-89",
        "90-99",
        "100-109",
        "110+",
    ]

    for bucket in buckets:

        bucket_trades = [
            trade
            for trade in diagnostic_trades
            if get_score_bucket(
                trade["setup_score"]
            ) == bucket
        ]

        if not bucket_trades:
            continue

        wins = sum(
            1
            for trade in bucket_trades
            if trade["profit"] > 0
        )

        losses = (
            len(bucket_trades)
            - wins
        )

        win_rate = (
            wins
            / len(bucket_trades)
            * 100
        )

        average_profit = (
            sum(
                trade["profit"]
                for trade in bucket_trades
            )
            / len(bucket_trades)
        )

        print(
            f"{bucket:>7} | "
            f"Trades: {len(bucket_trades):2d} | "
            f"Wins: {wins:2d} | "
            f"Losses: {losses:2d} | "
            f"Win rate: {win_rate:6.2f}% | "
            f"Avg P/L: ₹{average_profit:6.2f}"
        )

    # ======================================
    # RESULT BY COIN
    # ======================================

    print()
    print("RESULT BY COIN")
    print("-" * 60)

    symbols = sorted(
        set(
            trade["symbol"]
            for trade in diagnostic_trades
        )
    )

    for symbol in symbols:

        symbol_trades = [
            trade
            for trade in diagnostic_trades
            if trade["symbol"] == symbol
        ]

        wins = sum(
            1
            for trade in symbol_trades
            if trade["profit"] > 0
        )

        losses = (
            len(symbol_trades)
            - wins
        )

        win_rate = (
            wins
            / len(symbol_trades)
            * 100
        )

        average_score = (
            sum(
                trade["setup_score"]
                for trade in symbol_trades
            )
            / len(symbol_trades)
        )

        total_profit = sum(
            trade["profit"]
            for trade in symbol_trades
        )

        print(
            f"{symbol:10} | "
            f"Trades: {len(symbol_trades):2d} | "
            f"Wins: {wins:2d} | "
            f"Losses: {losses:2d} | "
            f"Win rate: {win_rate:6.2f}% | "
            f"Avg score: {average_score:6.2f} | "
            f"P/L: ₹{total_profit:7.2f}"
        )

    # ======================================
    # WINNING VS LOSING SETUPS
    # ======================================

    print()
    print("WINNING VS LOSING SETUPS")
    print("-" * 60)

    winning_setups = [
        trade
        for trade in diagnostic_trades
        if trade["profit"] > 0
    ]

    losing_setups = [
        trade
        for trade in diagnostic_trades
        if trade["profit"] <= 0
    ]

    def print_setup_average(
        label,
        setups,
    ):

        if not setups:

            print(
                f"{label}: no trades"
            )

            return

        average_score = (
            sum(
                trade["setup_score"]
                for trade in setups
            )
            / len(setups)
        )

        average_market_score = (
            sum(
                trade["market_score"]
                for trade in setups
            )
            / len(setups)
        )

        average_rsi = (
            sum(
                trade["rsi"]
                for trade in setups
            )
            / len(setups)
        )

        average_atr = (
            sum(
                trade["atr_percent"]
                for trade in setups
            )
            / len(setups)
        )

        average_confirmations = (
            sum(
                trade[
                    "technical_confirmations"
                ]
                for trade in setups
            )
            / len(setups)
        )

        print(
            f"{label:8} | "
            f"Trades: {len(setups):2d} | "
            f"Score: {average_score:6.2f} | "
            f"Market: {average_market_score:5.2f} | "
            f"RSI: {average_rsi:5.2f} | "
            f"ATR: {average_atr:5.2f}% | "
            f"Confirmations: "
            f"{average_confirmations:4.2f}"
        )

    print(
        "Type     | "
        "Trades | "
        "Score  | "
        "Market | "
        "RSI   | "
        "ATR   | "
        "Confirmations"
    )

    print_setup_average(
        "WIN",
        winning_setups,
    )

    print_setup_average(
        "LOSS",
        losing_setups,
    )


# ==========================================
# MAIN
# ==========================================

def main():

    print("=" * 60)
    print("CRYPTOAI PRO PORTFOLIO BACKTEST")
    print("=" * 60)

    print(
        f"Starting balance: "
        f"₹{STARTING_BALANCE:.2f}"
    )

    print(
        "Risk management: ADAPTIVE"
    )

    print(
        f"Maximum position: "
        f"{MAX_POSITION_SIZE * 100:.1f}%"
    )

    print(
        f"Take profit: "
        f"{TAKE_PROFIT_PERCENT:.1f}%"
    )

    print(
        f"Stop loss: "
        f"{STOP_LOSS_PERCENT:.1f}%"
    )

    print(
        f"Loss cooldown: "
        f"{COOLDOWN_CANDLES} candles"
    )

    print(
        "Coin quality test: "
        "POWRUSDT REMOVED"
    )

    print()

    # ======================================
    # DOWNLOAD DATA
    # ======================================

    market_data = {}

    for symbol in SYMBOLS:

        print(
            f"Downloading {CANDLE_LIMIT} candles "
            f"for {symbol}..."
        )

        try:

            candles = get_historical_candles(
                symbol,
                interval=INTERVAL,
                total_limit=CANDLE_LIMIT,
            )

        except Exception as e:

            print(
                f"Failed to download {symbol}: "
                f"{e}"
            )

            continue

        if not candles:

            print(
                f"No candles received for "
                f"{symbol}"
            )

            continue

        candles = sorted(
            candles,
            key=lambda x: x["time"],
        )

        market_data[symbol] = candles

        print(
            f"Downloaded "
            f"{len(candles)} candles."
        )

    if not market_data:

        print(
            "No market data available."
        )

        return

    # ======================================
    # COMMON TIMELINE
    # ======================================

    timestamps = set()

    for candles in market_data.values():

        for candle in candles:

            timestamps.add(
                candle["time"]
            )

    timestamps = sorted(
        timestamps
    )

    print()

    print(
        f"Common timestamps: "
        f"{len(timestamps)}"
    )

    # ======================================
    # PORTFOLIO STATE
    # ======================================

    balance = STARTING_BALANCE

    position = None

    completed_trades = []

    equity_curve = []

    max_equity = STARTING_BALANCE

    max_drawdown = 0.0

    # ======================================
    # ADAPTIVE RISK STATE
    # ======================================

    losing_streak = 0

    # ======================================
    # COOLDOWN STATE
    # ======================================

    cooldowns = {}

    # ======================================
    # TIMESTAMP LOOP
    # ======================================

    for timestamp in timestamps:

        # ----------------------------------
        # REDUCE COOLDOWNS
        # ----------------------------------

        expired_symbols = []

        for symbol in cooldowns:

            cooldowns[symbol] -= 1

            if cooldowns[symbol] <= 0:

                expired_symbols.append(
                    symbol
                )

        for symbol in expired_symbols:

            del cooldowns[symbol]

        # ----------------------------------
        # CURRENT CANDLES
        # ----------------------------------

        current_markets = []

        for symbol, candles in (
            market_data.items()
        ):

            matching_candle = None

            for candle in candles:

                if candle["time"] == timestamp:

                    matching_candle = candle

                    break

            if matching_candle is None:
                continue

            current_markets.append(
                {
                    "symbol": symbol,
                    "candle": matching_candle,
                }
            )

        if not current_markets:
            continue

        # ==================================
        # MANAGE OPEN POSITION
        # ==================================

        if position is not None:

            current_symbol = (
                position["symbol"]
            )

            current_candle = None

            for item in current_markets:

                if (
                    item["symbol"]
                    == current_symbol
                ):

                    current_candle = (
                        item["candle"]
                    )

                    break

            if current_candle is not None:

                high = float(
                    current_candle["high"]
                )

                low = float(
                    current_candle["low"]
                )

                take_profit_price = (
                    position["entry_price"]
                    * (
                        1
                        + TAKE_PROFIT_PERCENT
                        / 100
                    )
                )

                stop_loss_price = (
                    position[
                        "stop_loss_price"
                    ]
                )

                exit_price = None
                exit_reason = None

                # Stop loss gets priority if
                # both levels occur in one candle.

                if low <= stop_loss_price:

                    exit_price = (
                        stop_loss_price
                    )

                    exit_reason = (
                        "STOP LOSS"
                    )

                elif high >= take_profit_price:

                    exit_price = (
                        take_profit_price
                    )

                    exit_reason = (
                        "TAKE PROFIT"
                    )

                if exit_price is not None:

                    result = close_position(
                        position,
                        exit_price,
                    )

                    balance += result[
                        "net_sell_value"
                    ]

                    profit = result[
                        "profit"
                    ]

                    completed_trades.append(
                        {
                            "symbol":
                                current_symbol,

                            "entry_price":
                                position[
                                    "entry_price"
                                ],

                            "exit_price":
                                exit_price,

                            "profit":
                                profit,

                            "profit_percent":
                                result[
                                    "profit_percent"
                                ],

                            "reason":
                                exit_reason,

                            "setup_score":
                                position[
                                    "setup_score"
                                ],

                            "market_score":
                                position[
                                    "market_score"
                                ],

                            "news_score":
                                position[
                                    "news_score"
                                ],

                            "rsi":
                                position["rsi"],

                            "ema20":
                                position["ema20"],

                            "ema50":
                                position["ema50"],

                            "macd":
                                position["macd"],

                            "macd_signal":
                                position[
                                    "macd_signal"
                                ],

                            "atr_percent":
                                position[
                                    "atr_percent"
                                ],

                            "technical_confirmations":
                                position[
                                    "technical_confirmations"
                                ],
                        }
                    )

                    # ------------------------------
                    # UPDATE LOSING STREAK
                    # ------------------------------

                    if profit < 0:

                        losing_streak += 1

                    elif profit > 0:

                        losing_streak = 0

                    # ------------------------------
                    # APPLY COOLDOWN
                    # ------------------------------

                    if (
                        exit_reason
                        == "STOP LOSS"
                    ):

                        cooldowns[
                            current_symbol
                        ] = COOLDOWN_CANDLES

                    position = None

        # ==================================
        # SEARCH FOR NEW POSITION
        # ==================================

        if position is None:

            candidates = []

            for item in current_markets:

                symbol = item["symbol"]

                # ----------------------------------
                # COOLDOWN
                # ----------------------------------

                if symbol in cooldowns:
                    continue

                candles = market_data[
                    symbol
                ]

                # ----------------------------------
                # CANDLES UNTIL CURRENT TIME
                # ----------------------------------

                candles_until_now = [
                    candle
                    for candle in candles
                    if candle["time"]
                    <= timestamp
                ]

                if len(candles_until_now) < 60:
                    continue

                recent_candles = (
                    candles_until_now[-200:]
                )

                # ----------------------------------
                # INDICATORS
                # ----------------------------------

                try:

                    indicators = (
                        calculate_indicators(
                            recent_candles
                        )
                    )

                except Exception:

                    continue

                if (
                    indicators is None
                    or indicators.empty
                ):

                    continue

                # ----------------------------------
                # PRICE
                # ----------------------------------

                latest_candle = (
                    recent_candles[-1]
                )

                price = float(
                    latest_candle["close"]
                )

                # ----------------------------------
                # MARKET MOMENTUM
                # ----------------------------------

                previous_close = float(
                    recent_candles[-2][
                        "close"
                    ]
                )

                market_change = 0.0

                if previous_close > 0:

                    market_change = (
                        (
                            price
                            - previous_close
                        )
                        / previous_close
                    ) * 100

                if market_change > 1:

                    market_score = 80

                elif market_change > 0:

                    market_score = 60

                elif market_change > -1:

                    market_score = 40

                else:

                    market_score = 20

                # ----------------------------------
                # NEWS
                # ----------------------------------

                news = analyze_news(
                    "crypto adoption growth partnership"
                )

                # ----------------------------------
                # DECISION ENGINE
                # ----------------------------------

                decision = make_decision(
                    market_score,
                    news["score"],
                    True,
                    indicators,
                )

                latest_indicator = (
                    indicators.iloc[-1]
                )

                atr_value = float(
                    latest_indicator["ATR"]
                )

                atr_percent = (
                    atr_value
                    / price
                    * 100
                    if price > 0
                    else 0.0
                )

                # ----------------------------------
                # STORE CANDIDATE
                # ----------------------------------

                candidates.append(
                    {
                        "symbol": symbol,

                        "price": price,

                        "decision": decision,

                        "market_score":
                            market_score,

                        "news_score":
                            news["score"],

                        "rsi":
                            float(
                                latest_indicator[
                                    "RSI"
                                ]
                            ),

                        "ema20":
                            float(
                                latest_indicator[
                                    "EMA20"
                                ]
                            ),

                        "ema50":
                            float(
                                latest_indicator[
                                    "EMA50"
                                ]
                            ),

                        "macd":
                            float(
                                latest_indicator[
                                    "MACD"
                                ]
                            ),

                        "macd_signal":
                            float(
                                latest_indicator[
                                    "MACD_SIGNAL"
                                ]
                            ),

                        "atr_percent":
                            atr_percent,

                        "technical_confirmations":
                            int(
                                decision[
                                    "technical_confirmations"
                                ]
                            ),
                    }
                )

            # ==================================
            # SELECT BEST CANDIDATE
            # ==================================

            best = select_candidate(
                candidates
            )

            if best is not None:

                position_data = open_position(
                    balance=balance,

                    price=best["price"],

                    peak_balance=max_equity,

                    losing_streak=losing_streak,

                    setup_score=best[
                        "decision"
                    ]["score"],
                )

                if position_data is not None:

                    balance -= position_data[
                        "total_cost"
                    ]

                    position = {
                        "symbol":
                            best["symbol"],

                        **position_data,

                        "setup_score":
                            float(
                                best[
                                    "decision"
                                ]["score"]
                            ),

                        "market_score":
                            float(
                                best[
                                    "market_score"
                                ]
                            ),

                        "news_score":
                            float(
                                best[
                                    "news_score"
                                ]
                            ),

                        "rsi":
                            float(
                                best["rsi"]
                            ),

                        "ema20":
                            float(
                                best["ema20"]
                            ),

                        "ema50":
                            float(
                                best["ema50"]
                            ),

                        "macd":
                            float(
                                best["macd"]
                            ),

                        "macd_signal":
                            float(
                                best[
                                    "macd_signal"
                                ]
                            ),

                        "atr_percent":
                            float(
                                best[
                                    "atr_percent"
                                ]
                            ),

                        "technical_confirmations":
                            int(
                                best[
                                    "technical_confirmations"
                                ]
                            ),
                    }

        # ==================================
        # EQUITY
        # ==================================

        equity = balance

        if position is not None:

            current_price = None

            for item in current_markets:

                if (
                    item["symbol"]
                    == position["symbol"]
                ):

                    current_price = float(
                        item["candle"]["close"]
                    )

                    break

            if current_price is not None:

                position_value = (
                    position["amount"]
                    * current_price
                )

                equity += position_value

        equity_curve.append(
            equity
        )

        if equity > max_equity:

            max_equity = equity

        drawdown = (
            (
                max_equity
                - equity
            )
            / max_equity
        ) * 100

        if drawdown > max_drawdown:

            max_drawdown = drawdown

    # ======================================
    # CLOSE END-OF-BACKTEST POSITION
    # ======================================

    if position is not None:

        last_price = None

        for symbol, candles in (
            market_data.items()
        ):

            if symbol == position["symbol"]:

                last_price = float(
                    candles[-1]["close"]
                )

                break

        if last_price is not None:

            result = close_position(
                position,
                last_price,
            )

            balance += result[
                "net_sell_value"
            ]

            completed_trades.append(
                {
                    "symbol":
                        position["symbol"],

                    "entry_price":
                        position["entry_price"],

                    "exit_price":
                        last_price,

                    "profit":
                        result["profit"],

                    "profit_percent":
                        result[
                            "profit_percent"
                        ],

                    "reason":
                        "END OF BACKTEST",

                    "setup_score":
                        position[
                            "setup_score"
                        ],

                    "market_score":
                        position[
                            "market_score"
                        ],

                    "news_score":
                        position[
                            "news_score"
                        ],

                    "rsi":
                        position["rsi"],

                    "ema20":
                        position["ema20"],

                    "ema50":
                        position["ema50"],

                    "macd":
                        position["macd"],

                    "macd_signal":
                        position[
                            "macd_signal"
                        ],

                    "atr_percent":
                        position[
                            "atr_percent"
                        ],

                    "technical_confirmations":
                        position[
                            "technical_confirmations"
                        ],
                }
            )

    # ======================================
    # RESULTS
    # ======================================

    total_profit = (
        balance
        - STARTING_BALANCE
    )

    winning_trades = sum(
        1
        for trade in completed_trades
        if trade["profit"] > 0
    )

    losing_trades = sum(
        1
        for trade in completed_trades
        if trade["profit"] <= 0
    )

    total_trades = len(
        completed_trades
    )

    win_rate = (
        winning_trades
        / total_trades
        * 100
        if total_trades > 0
        else 0
    )

    # ======================================
    # PRINT RESULTS
    # ======================================

    print()
    print("=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)

    print(
        f"Starting balance : "
        f"₹{STARTING_BALANCE:.2f}"
    )

    print(
        f"Ending balance   : "
        f"₹{balance:.2f}"
    )

    print(
        f"Profit           : "
        f"₹{total_profit:.2f}"
    )

    print(
        f"Completed trades : "
        f"{total_trades}"
    )

    print(
        f"Wins             : "
        f"{winning_trades}"
    )

    print(
        f"Losses           : "
        f"{losing_trades}"
    )

    print(
        f"Win rate         : "
        f"{win_rate:.2f}%"
    )

    print(
        f"Max drawdown     : "
        f"{max_drawdown:.2f}%"
    )

    # ======================================
    # TRADE SUMMARY
    # ======================================

    print()
    print("TRADE SUMMARY")
    print("-" * 60)

    for trade in completed_trades:

        print(
            f"{trade['symbol']} | "
            f"Entry: "
            f"{trade['entry_price']:.6f} | "
            f"Exit: "
            f"{trade['exit_price']:.6f} | "
            f"P/L: "
            f"₹{trade['profit']:.2f} | "
            f"{trade['profit_percent']:.2f}% | "
            f"{trade['reason']}"
        )

    # ======================================
    # DIAGNOSTICS
    # ======================================

    print_decision_diagnostics(
        completed_trades
    )


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()