from coindcx_api import get_ticker
from news_ai import analyze_news
from decision_engine import make_decision
from fee_manager import check_trade
from paper_trader import PaperTrader



bot = PaperTrader(200)



market = get_ticker()


best = None


for coin in market:

    try:

        change = float(coin["change_24_hour"])
        volume = float(coin["volume"])

        score = 0


        if change > 10:
            score += 40

        if volume > 10000:
            score += 30


        if best is None or score > best["score"]:

            best = {

                "coin":coin["market"],
                "price":float(coin["last_price"]),
                "score":score

            }


    except:

        pass



print("Selected:")
print(best)



news = analyze_news(
    "crypto adoption growth partnership"
)



decision = make_decision(
    best["score"],
    news["score"],
    True
)



print("\nDecision:")
print(decision)



if "BUY" in decision["decision"]:

    print(
        bot.buy(
            best["coin"],
            best["price"]
        )
    )


# simulate price movement

new_price = best["price"] * 1.05


print(
    "\nAfter price change:"
)


print(
    bot.sell(new_price)
)
