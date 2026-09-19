from api.coindcx_api import get_ticker, get_candles


def get_market_tickers():
    """
    Get all available market ticker data.

    Returns:
        list: Market ticker data.
    """

    try:
        market = get_ticker()

        if not market:
            return []

        return market

    except Exception as error:
        print(f"Market ticker error: {error}")
        return []


def select_best_coin(
    min_change_percent=5.0,
    min_volume=10000.0
):
    """
    Select the strongest USDT market.

    Selection is based on:
    - Minimum 24h percentage change
    - Minimum 24h volume
    - Highest market change

    Returns:
        dict or None
    """

    market = get_market_tickers()

    if not market:
        return None

    best_coin = None

    for coin in market:

        try:
            symbol = coin["market"]

            if not symbol.endswith("USDT"):
                continue

            change = float(
                coin["change_24_hour"]
            )

            volume = float(
                coin["volume"]
            )

            last_price = float(
                coin["last_price"]
            )

            if change < min_change_percent:
                continue

            if volume < min_volume:
                continue

            if last_price <= 0:
                continue

            if (
                best_coin is None
                or change > best_coin["change_24_hour"]
            ):
                best_coin = {
                    "market": symbol,
                    "last_price": last_price,
                    "change_24_hour": change,
                    "volume": volume
                }

        except (
            KeyError,
            TypeError,
            ValueError
        ):
            continue

    return best_coin


def get_coin_candles(
    coin,
    interval="1m",
    limit=200
):
    """
    Get historical candles for a selected coin.

    Args:
        coin: Coin market symbol.
        interval: Candle interval.
        limit: Number of candles.

    Returns:
        list: Candle data.
    """

    try:
        candles = get_candles(
            coin,
            interval=interval,
            limit=limit
        )

        if not candles:
            return []

        return candles

    except Exception as error:
        print(
            f"Candle error for {coin}: {error}"
        )
        return []


def fetch_market_data(
    min_change_percent=5.0,
    min_volume=10000.0,
    interval="1m",
    limit=200
):
    """
    Complete market-data pipeline.

    Returns:
        dict or None
    """

    best_coin = select_best_coin(
        min_change_percent=min_change_percent,
        min_volume=min_volume
    )

    if best_coin is None:
        return None

    candles = get_coin_candles(
        best_coin["market"],
        interval=interval,
        limit=limit
    )

    if not candles:
        return None

    return {
        "market": best_coin,
        "candles": candles
    }


if __name__ == "__main__":

    print("=" * 60)
    print("CRYPTOAI PRO MARKET DATA TEST")
    print("=" * 60)

    selected = select_best_coin(
        min_change_percent=5.0,
        min_volume=10000.0
    )

    if selected:

        print(
            f"\nSelected market: "
            f"{selected['market']}"
        )

        print(
            f"Last price: "
            f"{selected['last_price']}"
        )

        print(
            f"24h change: "
            f"{selected['change_24_hour']:.2f}%"
        )

        print(
            f"24h volume: "
            f"{selected['volume']:.2f}"
        )

        candles = get_coin_candles(
            selected["market"],
            interval="1m",
            limit=200
        )

        print(
            f"Candles received: "
            f"{len(candles)}"
        )

    else:

        print(
            "\nNo suitable market found."
        )

    print(
        "\nMarket data test completed."
    )