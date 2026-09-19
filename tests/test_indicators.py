from api.coindcx_api import get_candles
from indicators.indicators import calculate_indicators


print("Fetching candle data...")

symbol = "LSKUSDT"

candles = get_candles(symbol)

print(f"Received {len(candles)} candles.")

if not candles:
    print("No candle data received.")
else:

    print("\nCalculating indicators...")

    result = calculate_indicators(candles)

    print("\nIndicator result:")
    print(result)