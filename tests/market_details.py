import requests

print("Downloading market details...\n")

url = "https://api.coindcx.com/exchange/v1/markets_details"

response = requests.get(url, timeout=10)

response.raise_for_status()

markets = response.json()

print("Total Markets:", len(markets))
print()

found = False

for market in markets:

    if market["symbol"] == "BTCUSDT":

        found = True

        print("=" * 60)
        print("BTCUSDT FOUND")
        print("=" * 60)

        print("Symbol :", market["symbol"])
        print("Pair   :", market["pair"])
        print("Name   :", market["coindcx_name"])
        print()

        print("Complete Data:\n")
        print(market)

        break

if not found:
    print("BTCUSDT not found.")
