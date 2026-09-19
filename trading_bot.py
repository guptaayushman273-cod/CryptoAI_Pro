import time

from logging_config import setup_logger

from market.market_data import (
    get_market_tickers,
    select_best_coin,
    get_coin_candles
)

from indicators.indicators import calculate_indicators

from strategy.news_ai import analyze_news
from strategy.decision_engine import make_decision

from trader.fee_manager import check_trade
from trader.paper_trader import PaperTrader
from trader.position_monitor import PositionMonitor

from database.database import (
    init_db,
    get_position
)

from risk.risk_control import check_risk


# ============================================================
# SETTINGS
# ============================================================

STARTING_BALANCE = 200.0

TAKE_PROFIT_PERCENT = 5.0
STOP_LOSS_PERCENT = 3.0

MARKET_CHANGE_MIN_PERCENT = 5.0
MARKET_VOLUME_MIN = 10000.0

CANDLE_INTERVAL = "1m"
CANDLE_LIMIT = 200

SCAN_INTERVAL = 60


# ============================================================
# LOGGER
# ============================================================

logger = setup_logger()


# ============================================================
# DATABASE
# ============================================================

init_db()


# ============================================================
# PAPER TRADER
# ============================================================

bot = PaperTrader(STARTING_BALANCE)


# ============================================================
# POSITION STATE
# ============================================================

holding = False
current_trade = None
position_monitor = None


# ============================================================
# RESTORE OPEN POSITION
# ============================================================

saved_position = get_position()

if saved_position:

    logger.info("=" * 60)
    logger.info("EXISTING POSITION FOUND IN DATABASE")
    logger.info("=" * 60)

    try:

        bot.restore_position(
            coin=saved_position["coin"],
            buy_price=saved_position["price"],
            amount=saved_position["amount"],
            position_value=saved_position.get(
                "position_value"
            ),
            stop_loss_price=saved_position.get(
                "stop_loss_price"
            ),
            opened_at=saved_position.get(
                "opened_at"
            )
        )

        holding = True

        current_trade = {
            "coin": saved_position["coin"],
            "price": saved_position["price"],
            "amount": saved_position["amount"],
            "position_value": saved_position.get(
                "position_value"
            ),
            "stop_loss_price": saved_position.get(
                "stop_loss_price"
            ),
            "opened_at": saved_position.get(
                "opened_at"
            )
        }

        position_monitor = PositionMonitor(
            current_trade
        )

        logger.info(
            f"Restored position: "
            f"{current_trade['coin']}"
        )

        logger.info(
            f"Buy price: "
            f"{current_trade['price']}"
        )

        logger.info(
            f"Amount: "
            f"{current_trade['amount']}"
        )

        logger.info(
            f"Stop-loss: "
            f"{current_trade['stop_loss_price']}"
        )

    except Exception as e:

        logger.error(
            f"Could not restore position: {e}"
        )

        holding = False
        current_trade = None
        position_monitor = None

else:

    logger.info(
        "No open position found in database."
    )


# ============================================================
# FIND CURRENT PRICE
# ============================================================

def find_current_price(
    market_data,
    target_coin
):

    for market in market_data:

        try:

            if market["market"] == target_coin:

                price = float(
                    market["last_price"]
                )

                if price > 0:
                    return price

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            continue

    return None


# ============================================================
# MARKET SCORE
# ============================================================

def calculate_market_score(
    change_percent
):

    try:

        change_percent = float(
            change_percent
        )

    except (
        TypeError,
        ValueError
    ):

        return 0

    if change_percent <= 0:
        return 0

    return min(
        40,
        change_percent
    )


# ============================================================
# MAIN BOT
# ============================================================

logger.info("")
logger.info("=" * 60)
logger.info("CRYPTOAI PRO V2 - PAPER TRADING BOT")
logger.info("=" * 60)
logger.info("")


try:

    while True:

        # ====================================================
        # RISK CHECK
        # ====================================================

        try:

            if not check_risk():

                logger.error(
                    "RISK STOP - Trading stopped."
                )

                break

        except Exception as e:

            logger.error(
                f"Risk check failed: {e}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        # ====================================================
        # GET MARKET TICKERS
        # ====================================================

        logger.info("")
        logger.info("NEW MARKET SCAN")
        logger.info("=" * 60)

        try:

            market_data = get_market_tickers()

        except Exception as e:

            logger.error(
                f"Failed to get market tickers: {e}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        if not market_data:

            logger.warning(
                "No market data received."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        logger.info(
            f"Markets received: "
            f"{len(market_data)}"
        )


        # ====================================================
        # MANAGE EXISTING POSITION
        # ====================================================

        if holding and current_trade:

            coin = current_trade["coin"]

            current_price = find_current_price(
                market_data,
                coin
            )


            # ------------------------------------------------
            # PRICE NOT FOUND
            # ------------------------------------------------

            if current_price is None:

                logger.warning(
                    f"Could not find current price "
                    f"for {coin}."
                )

                logger.info(
                    "Existing position will remain open."
                )

                logger.info(
                    f"Waiting {SCAN_INTERVAL} seconds..."
                )

                time.sleep(
                    SCAN_INTERVAL
                )

                continue


            # ------------------------------------------------
            # POSITION MONITOR
            # ------------------------------------------------

            status = position_monitor.get_status(
                current_price
            )

            logger.info("")
            logger.info(
                "OPEN POSITION MONITOR"
            )
            logger.info("-" * 60)

            logger.info(
                f"Coin: {coin}"
            )

            logger.info(
                f"Buy price: "
                f"{current_trade['price']}"
            )

            logger.info(
                f"Current price: "
                f"{current_price}"
            )

            logger.info(
                f"Stop-loss: "
                f"{current_trade['stop_loss_price']}"
            )

            logger.info(
                f"Status: "
                f"{status['status']}"
            )


            # =================================================
            # STOP LOSS
            # =================================================

            if (
                status["status"]
                == "STOP_LOSS_TRIGGERED"
            ):

                logger.warning("")
                logger.warning(
                    "STOP-LOSS TRIGGERED"
                )

                logger.warning(
                    f"Current price: "
                    f"{current_price}"
                )

                logger.warning(
                    f"Stop-loss price: "
                    f"{current_trade['stop_loss_price']}"
                )

                logger.warning(
                    "Executing paper SELL..."
                )


                sell_result = bot.sell(
                    current_price
                )


                if sell_result.get(
                    "success"
                ):

                    logger.info("")
                    logger.info(
                        "STOP-LOSS SELL SUCCESSFUL"
                    )

                    logger.info(
                        f"Coin: "
                        f"{sell_result['coin']}"
                    )

                    logger.info(
                        f"Buy price: "
                        f"{sell_result['buy_price']}"
                    )

                    logger.info(
                        f"Sell price: "
                        f"{sell_result['sell_price']}"
                    )

                    logger.info(
                        f"Profit/Loss: "
                        f"₹{sell_result['profit']}"
                    )

                    logger.info(
                        f"Profit/Loss %: "
                        f"{sell_result['profit_percent']}%"
                    )

                    logger.info(
                        f"Balance: "
                        f"₹{sell_result['balance']}"
                    )


                    holding = False
                    current_trade = None
                    position_monitor = None

                else:

                    logger.error(
                        f"Stop-loss SELL failed: "
                        f"{sell_result}"
                    )


                time.sleep(
                    SCAN_INTERVAL
                )

                continue


            # =================================================
            # TAKE PROFIT
            # =================================================

            buy_price = float(
                current_trade["price"]
            )

            profit_percent = (
                (
                    current_price
                    - buy_price
                )
                / buy_price
            ) * 100


            logger.info(
                f"Current P/L: "
                f"{profit_percent:.2f}%"
            )


            if (
                profit_percent
                >= TAKE_PROFIT_PERCENT
            ):

                logger.info("")
                logger.info(
                    "TAKE-PROFIT TARGET REACHED"
                )

                logger.info(
                    f"Target: "
                    f"{TAKE_PROFIT_PERCENT}%"
                )

                logger.info(
                    f"Current P/L: "
                    f"{profit_percent:.2f}%"
                )

                logger.info(
                    "Executing paper SELL..."
                )


                sell_result = bot.sell(
                    current_price
                )


                if sell_result.get(
                    "success"
                ):

                    logger.info("")
                    logger.info(
                        "TAKE-PROFIT SELL SUCCESSFUL"
                    )

                    logger.info(
                        f"Coin: "
                        f"{sell_result['coin']}"
                    )

                    logger.info(
                        f"Buy price: "
                        f"{sell_result['buy_price']}"
                    )

                    logger.info(
                        f"Sell price: "
                        f"{sell_result['sell_price']}"
                    )

                    logger.info(
                        f"Profit/Loss: "
                        f"₹{sell_result['profit']}"
                    )

                    logger.info(
                        f"Profit/Loss %: "
                        f"{sell_result['profit_percent']}%"
                    )

                    logger.info(
                        f"Balance: "
                        f"₹{sell_result['balance']}"
                    )


                    holding = False
                    current_trade = None
                    position_monitor = None

                else:

                    logger.error(
                        f"Take-profit SELL failed: "
                        f"{sell_result}"
                    )


                time.sleep(
                    SCAN_INTERVAL
                )

                continue


            # =================================================
            # HOLD
            # =================================================

            logger.info(
                "Position remains open."
            )

            logger.info(
                "No new BUY will be attempted "
                "while holding."
            )

            logger.info(
                f"Waiting {SCAN_INTERVAL} seconds..."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        # ====================================================
        # NO POSITION
        # ====================================================

        logger.info("")
        logger.info(
            "NO OPEN POSITION"
        )

        logger.info(
            "Searching for best market..."
        )


        # ====================================================
        # SELECT MARKET
        # ====================================================

        try:

            selected_coin = select_best_coin(
                min_change_percent=(
                    MARKET_CHANGE_MIN_PERCENT
                ),
                min_volume=(
                    MARKET_VOLUME_MIN
                )
            )

        except Exception as e:

            logger.error(
                f"Market selection failed: {e}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        if not selected_coin:

            logger.warning(
                "No suitable market found."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        coin = selected_coin["market"]

        current_price = float(
            selected_coin["last_price"]
        )

        change_24_hour = float(
            selected_coin["change_24_hour"]
        )

        volume = float(
            selected_coin["volume"]
        )


        logger.info("")
        logger.info(
            f"Selected market: {coin}"
        )

        logger.info(
            f"Current price: {current_price}"
        )

        logger.info(
            f"24h change: "
            f"{change_24_hour:.2f}%"
        )

        logger.info(
            f"24h volume: "
            f"{volume:.2f}"
        )


        # ====================================================
        # CANDLES
        # ====================================================

        try:

            candles = get_coin_candles(
                coin,
                interval=CANDLE_INTERVAL,
                limit=CANDLE_LIMIT
            )

        except Exception as e:

            logger.error(
                f"Failed to get candles: {e}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        if candles is None or len(candles) == 0:

            logger.warning(
                "No candle data received."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        logger.info(
            f"Candles: {len(candles)}"
        )


        # ====================================================
        # INDICATORS
        # ====================================================

        try:

            indicators = calculate_indicators(
                candles
            )

        except Exception as e:

            logger.error(
                f"Indicator calculation failed: {e}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        if (
            indicators is None
            or indicators.empty
        ):

            logger.warning(
                "Indicator calculation returned "
                "no data."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        # ====================================================
        # MARKET SCORE
        # ====================================================

        market_score = calculate_market_score(
            change_24_hour
        )


        # ====================================================
        # NEWS
        # ====================================================

        try:

            news = analyze_news(
                "crypto adoption growth partnership"
            )

            news_score = news["score"]

        except Exception as e:

            logger.warning(
                f"News analysis failed: {e}"
            )

            news = {
                "sentiment": "NEUTRAL",
                "score": 0
            }

            news_score = 0


        # ====================================================
        # FEE CHECK
        # ====================================================

        try:

            fee = check_trade(
                STARTING_BALANCE,
                current_price,
                current_price * 1.05
            )

            fee_ok = fee["allowed"]

        except Exception as e:

            logger.warning(
                f"Fee check failed: {e}"
            )

            fee = {
                "allowed": False
            }

            fee_ok = False


        # ====================================================
        # DECISION ENGINE
        # ====================================================

        try:

            decision = make_decision(
                market_score,
                news_score,
                fee_ok,
                indicators
            )

        except Exception as e:

            logger.error(
                f"Decision engine failed: {e}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        # ====================================================
        # LIVE SIGNAL
        # ====================================================

        logger.info("")
        logger.info("=" * 60)
        logger.info("LIVE SIGNAL")
        logger.info("=" * 60)

        logger.info(
            f"Market score: "
            f"{market_score}"
        )

        logger.info(
            f"News score: "
            f"{news_score}"
        )

        logger.info(
            f"News sentiment: "
            f"{news.get('sentiment')}"
        )

        logger.info(
            f"Fee OK: "
            f"{fee_ok}"
        )

        logger.info(
            f"Decision: "
            f"{decision.get('decision')}"
        )

        logger.info(
            f"Score: "
            f"{decision.get('score')}"
        )

        logger.info(
            f"Technical confirmations: "
            f"{decision.get('technical_confirmations')}"
        )

        logger.info(
            f"ATR: "
            f"{decision.get('atr_percent')}%"
        )


        logger.info("Reasons:")

        reasons = decision.get(
            "reason",
            []
        )

        if isinstance(
            reasons,
            str
        ):

            reasons = [reasons]


        for reason in reasons:

            logger.info(
                f"  - {reason}"
            )


        # ====================================================
        # BUY DECISION
        # ====================================================

        decision_name = str(
            decision.get(
                "decision",
                ""
            )
        )


        is_buy_candidate = (
            decision_name.startswith(
                "BUY CANDIDATE"
            )
        )


        if not is_buy_candidate:

            logger.info("")
            logger.info(
                "No paper trade."
            )

            logger.info(
                f"Waiting {SCAN_INTERVAL} seconds..."
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        # ====================================================
        # STOP-LOSS PRICE
        # ====================================================

        stop_loss_price = (
            current_price
            * (
                1
                - STOP_LOSS_PERCENT / 100
            )
        )


        logger.info("")
        logger.info(
            "BUY CANDIDATE CONFIRMED"
        )

        logger.info(
            f"Entry price: "
            f"{current_price}"
        )

        logger.info(
            f"Stop-loss: "
            f"{stop_loss_price}"
        )


        # ====================================================
        # PAPER BUY
        # ====================================================

        try:

            buy_result = bot.buy(
                coin,
                current_price,
                stop_loss_price
            )

        except Exception as e:

            logger.error(
                f"Paper BUY failed: {e}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        if not buy_result.get(
            "success"
        ):

            logger.warning(
                f"Paper BUY rejected: "
                f"{buy_result}"
            )

            time.sleep(
                SCAN_INTERVAL
            )

            continue


        # ====================================================
        # BUY SUCCESS
        # ====================================================

        logger.info("")
        logger.info("=" * 60)
        logger.info(
            "PAPER BUY SUCCESSFUL"
        )
        logger.info("=" * 60)

        logger.info(
            f"Coin: "
            f"{buy_result['coin']}"
        )

        logger.info(
            f"Entry price: "
            f"{buy_result['price']}"
        )

        logger.info(
            f"Amount: "
            f"{buy_result['amount']}"
        )

        logger.info(
            f"Position value: "
            f"₹{buy_result['position_value']:.2f}"
        )

        logger.info(
            f"Stop-loss: "
            f"{buy_result['stop_loss_price']}"
        )

        logger.info(
            f"Remaining balance: "
            f"₹{buy_result['remaining_balance']:.2f}"
        )


        # ====================================================
        # CREATE POSITION MONITOR
        # ====================================================

        current_trade = {
            "coin": buy_result["coin"],
            "price": buy_result["price"],
            "amount": buy_result["amount"],
            "position_value": (
                buy_result["position_value"]
            ),
            "stop_loss_price": (
                buy_result["stop_loss_price"]
            ),
            "opened_at": None
        }


        holding = True

        position_monitor = PositionMonitor(
            current_trade
        )


        logger.info("")
        logger.info(
            "POSITION MONITOR CREATED"
        )

        logger.info(
            f"Monitoring: {coin}"
        )

        logger.info(
            "New BUY orders are disabled "
            "while this position is open."
        )

        logger.info(
            f"Waiting {SCAN_INTERVAL} seconds..."
        )

        time.sleep(
            SCAN_INTERVAL
        )


except KeyboardInterrupt:

    logger.info("")
    logger.info(
        "BOT STOPPED BY USER"
    )


except Exception as e:

    logger.exception(
        f"BOT STOPPED DUE TO ERROR: {e}"
    )


finally:

    logger.info("")
    logger.info(
        "CRYPTOAI PRO BOT SHUTDOWN"
    )