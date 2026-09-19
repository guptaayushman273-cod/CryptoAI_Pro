from coindcx_api import get_pair
from coindcx_api import get_candles

coin = "BTCUSDT"

pair = get_pair(coin)

print("Coin :", coin)
print("Pair :", pair)
print()

print("Downloading candles...\n")

candles = get_candles(
    coin,
    interval="1m",
    limit=10
)

print("Candles Downloaded:", len(candles))
print()

if len(candles):

    print("First Candle\n")

    print(candles[0])

else:

    print("No candles returned.")
