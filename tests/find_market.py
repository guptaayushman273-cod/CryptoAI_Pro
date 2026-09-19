from coindcx_api import get_ticker

print("Downloading market list...\n")

markets = get_ticker()

print("Total Markets:", len(markets))
print()

count = 0

for market in markets:

    try:

        name = market["market"]

        if "BTC" in name.upper():

            print(name)

            count += 1

            if count >= 30:
                break

    except:
        pass
