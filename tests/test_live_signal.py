from market.market_data import (
    select_best_coin,
    get_coin_candles
)

from indicators.indicators import calculate_indicators
from strategy.decision_engine import make_decision


def main():
    print("=" * 60)
    print("CRYPTOAI PRO - LIVE SIGNAL TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Select strongest live market
    # ---------------------------------------------------------

    market = select_best_coin(
        min_change_percent=5.0,
        min_volume=10000.0
    )

    if market is None:
        print("\nNo suitable market found.")
        return

    coin = market["market"]
    current_price = market["last_price"]

    print(f"\nSelected market: {coin}")
    print(f"Current price: {current_price}")

    print(
        f"24h change: "
        f"{market['change_24_hour']:.2f}%"
    )

    print(
        f"24h volume: "
        f"{market['volume']:.2f}"
    )

    # ---------------------------------------------------------
    # 2. Get candles
    # ---------------------------------------------------------

    candles = get_coin_candles(
        coin,
        interval="1m",
        limit=200
    )

    if not candles:
        print("\nNo candles received.")
        return

    print(f"Candles received: {len(candles)}")

    # ---------------------------------------------------------
    # 3. Calculate indicators
    # ---------------------------------------------------------

    indicators = calculate_indicators(candles)

    # calculate_indicators returns a Pandas DataFrame.
    # Therefore we must check None and .empty separately.

    if indicators is None or indicators.empty:
        print("\nCould not calculate indicators.")
        return

    print(
        f"Indicator rows: {len(indicators)}"
    )

    # ---------------------------------------------------------
    # 4. Market momentum score
    # ---------------------------------------------------------

    market_change = market["change_24_hour"]

    if market_change >= 20:
        market_score = 40

    elif market_change >= 10:
        market_score = 30

    elif market_change >= 5:
        market_score = 20

    else:
        market_score = 0

    # ---------------------------------------------------------
    # 5. News score
    #
    # V2 will later replace this with real live news.
    # ---------------------------------------------------------

    news_score = 0

    # ---------------------------------------------------------
    # 6. Fee check
    #
    # Current test assumes the trade is fee-acceptable.
    # Real fee validation will be connected later.
    # ---------------------------------------------------------

    fee_ok = True

    # ---------------------------------------------------------
    # 7. Decision Engine
    # ---------------------------------------------------------

    decision = make_decision(
        market_score=market_score,
        news_score=news_score,
        fee_ok=fee_ok,
        indicators=indicators
    )

    # ---------------------------------------------------------
    # 8. Display result
    # ---------------------------------------------------------

    print("\n" + "-" * 60)
    print("LIVE SIGNAL RESULT")
    print("-" * 60)

    print(f"Market: {coin}")
    print(f"Price: {current_price}")
    print(f"Market score: {market_score}")
    print(f"News score: {news_score}")
    print(f"Fee OK: {fee_ok}")

    print("\nDecision:")
    print(decision)

    print("-" * 60)

    print("\nLive signal test completed.")
    print("NO TRADE WAS EXECUTED.")


if __name__ == "__main__":
    main()