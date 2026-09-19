import requests
import time
import hmac
import hashlib
import json

from config import API_KEY, API_SECRET, BASE_URL


# ======================================
# PUBLIC API
# ======================================

def get_ticker():
    """
    Get current ticker information for all markets.
    """

    url = BASE_URL + "/exchange/ticker"

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ======================================
# PRIVATE API
# ======================================

def get_balance():
    """
    Get account balances from CoinDCX.
    """

    url = BASE_URL + "/exchange/v1/users/balances"

    body = {
        "timestamp": int(
            time.time() * 1000
        )
    }

    body_json = json.dumps(body)

    signature = hmac.new(
        API_SECRET.encode(),
        body_json.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": API_KEY,
        "X-AUTH-SIGNATURE": signature
    }

    response = requests.post(
        url,
        data=body_json,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ======================================
# MARKET DETAILS
# ======================================

def get_market_details():
    """
    Get CoinDCX market details.
    """

    url = BASE_URL + "/exchange/v1/markets_details"

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ======================================
# FIND MARKET
# ======================================

def find_market(symbol):
    """
    Find a CoinDCX market using several possible
    symbol formats.

    Examples:
        LSKUSDT
        STEEMUSDT
        STEEM_USDT
        FORTH-USDT
    """

    requested = str(symbol).upper()

    markets = get_market_details()

    normalized_requested = (
        requested
        .replace("-", "")
        .replace("_", "")
    )

    for market in markets:

        market_symbol = str(
            market.get("symbol", "")
        ).upper()

        coindcx_name = str(
            market.get("coindcx_name", "")
        ).upper()

        normalized_symbol = (
            market_symbol
            .replace("-", "")
            .replace("_", "")
        )

        normalized_coindcx_name = (
            coindcx_name
            .replace("-", "")
            .replace("_", "")
        )

        if requested == market_symbol:
            return market

        if requested == coindcx_name:
            return market

        if normalized_requested == normalized_symbol:
            return market

        if (
            normalized_requested
            == normalized_coindcx_name
        ):
            return market

    return None


# ======================================
# FIND PAIR
# ======================================

def get_pair(symbol):
    """
    Return the CoinDCX candle pair for a symbol.
    """

    market = find_market(symbol)

    if market is None:
        return None

    return market.get("pair")


# ======================================
# GET CANDLES
# ======================================

def get_candles(
    symbol,
    interval="1m",
    limit=200
):
    """
    Get the most recent candle data.

    CoinDCX supports a maximum of 1000
    candles per request.
    """

    if limit > 1000:
        raise ValueError(
            "get_candles() supports a maximum "
            "of 1000 candles per request."
        )

    market = find_market(symbol)

    if market is None:
        raise Exception(
            f"Market {symbol} not found."
        )

    pair = market.get("pair")

    if not pair:
        raise Exception(
            f"No candle pair found for {symbol}."
        )

    url = (
        "https://public.coindcx.com"
        "/market_data/candles"
    )

    params = {
        "pair": pair,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ======================================
# HISTORICAL CANDLES
# ======================================

def get_historical_candles(
    symbol,
    interval="1m",
    total_limit=5000
):
    """
    Download a larger historical candle set
    using multiple requests.

    CoinDCX may return 999 candles even when
    1000 are requested, so a batch smaller than
    the requested batch size does NOT automatically
    mean that historical data has ended.

    Returns candles sorted from oldest to newest.
    """

    if total_limit <= 0:
        return []

    market = find_market(symbol)

    if market is None:
        raise Exception(
            f"Market {symbol} not found."
        )

    pair = market.get("pair")

    if not pair:
        raise Exception(
            f"No candle pair found for {symbol}."
        )

    # --------------------------------------
    # INTERVAL DURATIONS
    # --------------------------------------

    interval_minutes = {
        "1m": 1,
        "15m": 15,
        "1h": 60,
        "1d": 1440
    }

    if interval not in interval_minutes:
        raise ValueError(
            f"Unsupported interval: {interval}"
        )

    candle_ms = (
        interval_minutes[interval]
        * 60
        * 1000
    )

    url = (
        "https://public.coindcx.com"
        "/market_data/candles"
    )

    all_candles = []

    end_time = int(
        time.time() * 1000
    )

    # --------------------------------------
    # DOWNLOAD BATCHES
    # --------------------------------------

    while len(all_candles) < total_limit:

        remaining = (
            total_limit
            - len(all_candles)
        )

        batch_limit = min(
            remaining,
            1000
        )

        start_time = (
            end_time
            - (
                batch_limit
                * candle_ms
            )
        )

        params = {
            "pair": pair,
            "interval": interval,
            "limit": batch_limit,
            "startTime": start_time,
            "endTime": end_time
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        batch = response.json()

        if not batch:
            print(
                "No more historical candles "
                f"available for {symbol}."
            )
            break

        all_candles.extend(batch)

        # ----------------------------------
        # FIND OLDEST CANDLE
        # ----------------------------------

        oldest_time = min(
            candle["time"]
            for candle in batch
        )

        # ----------------------------------
        # MOVE BACKWARD
        # ----------------------------------

        next_end_time = (
            oldest_time
            - candle_ms
        )

        # Safety check against a repeated
        # or overlapping API response.
        if next_end_time >= end_time:

            print(
                "Historical candle pagination "
                "stopped because the API returned "
                "a non-progressing time range."
            )

            break

        end_time = next_end_time

        print(
            f"  Historical progress: "
            f"{min(len(all_candles), total_limit)}"
            f"/{total_limit}"
        )

        time.sleep(0.2)

    # --------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------

    unique_candles = {
        candle["time"]: candle
        for candle in all_candles
    }

    candles = list(
        unique_candles.values()
    )

    # --------------------------------------
    # SORT OLDEST -> NEWEST
    # --------------------------------------

    candles.sort(
        key=lambda candle: candle["time"]
    )

    # --------------------------------------
    # RETURN REQUESTED AMOUNT
    # --------------------------------------

    return candles[-total_limit:]