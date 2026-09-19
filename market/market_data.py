from api.coindcx_api import get_ticker, get_candles


# ============================================================
# CRYPTOAI PRO - MARKET DATA
# ============================================================

# Current Random Forest training universe.
#
# IMPORTANT:
# The ML model should only make predictions for markets
# represented in its training data.
ML_SUPPORTED_MARKETS = [
    "BTCUSDT",
    "ETHUSDT",
    "LSKUSDT"
]


# ============================================================
# GET ALL TICKERS
# ============================================================

def get_market_tickers():
    """
    Get all available CoinDCX market ticker data.

    Returns:
        list: Market ticker data.
    """

    try:

        market = get_ticker()

        if not market:
            return []

        return market

    except Exception as error:

        print(
            f"Market ticker error: {error}"
        )

        return []


# ============================================================
# SELECT BEST COIN
# ============================================================

def select_best_coin(
    min_change_percent=5.0,
    min_volume=10000.0,
    allowed_markets=None
):
    """
    Select the strongest suitable USDT market.

    Selection criteria:
    - USDT market
    - Optional allowed market universe
    - Minimum 24h percentage change
    - Minimum 24h volume
    - Valid positive price
    - Highest 24h percentage change

    Args:
        min_change_percent:
            Minimum 24h change.

        min_volume:
            Minimum 24h volume.

        allowed_markets:
            Optional list/set of market symbols.

            Example:
            [
                "BTCUSDT",
                "ETHUSDT",
                "LSKUSDT"
            ]

            If None, all USDT markets are allowed.

    Returns:
        dict or None
    """

    market = get_market_tickers()

    if not market:
        return None

    # Convert once for faster membership checks.
    if allowed_markets is not None:

        allowed_markets = {
            str(symbol).upper()
            for symbol in allowed_markets
        }

    best_coin = None

    for coin in market:

        try:

            symbol = str(
                coin["market"]
            ).upper()

            # --------------------------------------------
            # USDT ONLY
            # --------------------------------------------

            if not symbol.endswith("USDT"):
                continue

            # --------------------------------------------
            # OPTIONAL ML UNIVERSE FILTER
            # --------------------------------------------

            if (
                allowed_markets is not None
                and
                symbol not in allowed_markets
            ):
                continue

            # --------------------------------------------
            # VALUES
            # --------------------------------------------

            change = float(
                coin["change_24_hour"]
            )

            volume = float(
                coin["volume"]
            )

            last_price = float(
                coin["last_price"]
            )

            # --------------------------------------------
            # FILTERS
            # --------------------------------------------

            if change < min_change_percent:
                continue

            if volume < min_volume:
                continue

            if last_price <= 0:
                continue

            # --------------------------------------------
            # BEST MARKET
            # --------------------------------------------

            if (
                best_coin is None
                or
                change
                > best_coin["change_24_hour"]
            ):

                best_coin = {

                    "market":
                        symbol,

                    "last_price":
                        last_price,

                    "change_24_hour":
                        change,

                    "volume":
                        volume
                }

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            continue

    return best_coin


# ============================================================
# SELECT BEST ML-SUPPORTED COIN
# ============================================================

def select_best_ml_coin(
    min_change_percent=0.0,
    min_volume=10000.0
):
    """
    Select the strongest market from the current
    Random Forest training universe.

    The current model was trained on:
    BTCUSDT
    ETHUSDT
    LSKUSDT

    Returns:
        dict or None
    """

    return select_best_coin(

        min_change_percent=
            min_change_percent,

        min_volume=
            min_volume,

        allowed_markets=
            ML_SUPPORTED_MARKETS
    )


# ============================================================
# GET CANDLES
# ============================================================

def get_coin_candles(
    coin,
    interval="1m",
    limit=200
):
    """
    Get historical candles for a selected coin.

    Args:
        coin:
            Coin market symbol.

        interval:
            Candle interval.

        limit:
            Number of candles.

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
            f"Candle error for "
            f"{coin}: {error}"
        )

        return []


# ============================================================
# FETCH MARKET DATA
# ============================================================

def fetch_market_data(
    min_change_percent=5.0,
    min_volume=10000.0,
    interval="1m",
    limit=200,
    ml_mode=False
):
    """
    Complete market-data pipeline.

    Args:
        min_change_percent:
            Minimum 24h market change.

        min_volume:
            Minimum 24h volume.

        interval:
            Candle interval.

        limit:
            Number of candles.

        ml_mode:
            False:
                Scan all USDT markets.

            True:
                Scan only markets represented
                in the current ML training data.

    Returns:
        dict or None
    """

    # --------------------------------------------------------
    # MARKET SELECTION
    # --------------------------------------------------------

    if ml_mode:

        best_coin = (
            select_best_ml_coin(

                min_change_percent=
                    min_change_percent,

                min_volume=
                    min_volume
            )
        )

    else:

        best_coin = (
            select_best_coin(

                min_change_percent=
                    min_change_percent,

                min_volume=
                    min_volume
            )
        )

    if best_coin is None:
        return None

    # --------------------------------------------------------
    # CANDLES
    # --------------------------------------------------------

    candles = get_coin_candles(

        best_coin["market"],

        interval=interval,

        limit=limit
    )

    if not candles:
        return None

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "market":
            best_coin,

        "candles":
            candles,

        "ml_supported":
            (
                best_coin["market"]
                in ML_SUPPORTED_MARKETS
            ),

        "ml_mode":
            ml_mode
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CRYPTOAI PRO MARKET DATA TEST")
    print("=" * 60)

    print()
    print(
        "ML-supported markets:"
    )

    for symbol in ML_SUPPORTED_MARKETS:

        print(
            f"  - {symbol}"
        )

    # --------------------------------------------------------
    # NORMAL MARKET SCAN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("NORMAL MARKET SCAN")
    print("=" * 60)

    normal_selected = (
        select_best_coin(

            min_change_percent=5.0,

            min_volume=10000.0
        )
    )

    if normal_selected:

        print(
            f"Selected: "
            f"{normal_selected['market']}"
        )

        print(
            f"24h change: "
            f"{normal_selected['change_24_hour']:.2f}%"
        )

    else:

        print(
            "No suitable normal "
            "market found."
        )

    # --------------------------------------------------------
    # ML MARKET SCAN
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("ML-SUPPORTED MARKET SCAN")
    print("=" * 60)

    ml_selected = (
        select_best_ml_coin(

            # Use 0 here because BTC/ETH may not
            # move +5% every day.
            min_change_percent=0.0,

            min_volume=10000.0
        )
    )

    if ml_selected:

        print(
            f"Selected: "
            f"{ml_selected['market']}"
        )

        print(
            f"Last price: "
            f"{ml_selected['last_price']}"
        )

        print(
            f"24h change: "
            f"{ml_selected['change_24_hour']:.2f}%"
        )

        print(
            f"24h volume: "
            f"{ml_selected['volume']:.2f}"
        )

        candles = get_coin_candles(

            ml_selected["market"],

            interval="1m",

            limit=200
        )

        print(
            f"Candles received: "
            f"{len(candles)}"
        )

    else:

        print(
            "No suitable ML-supported "
            "market found."
        )

    print()
    print("=" * 60)
    print("MARKET DATA TEST COMPLETE")
    print("=" * 60)