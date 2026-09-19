def analyze_news(news):

    news = news.lower()


    bullish_words = [
        "partnership",
        "adoption",
        "approval",
        "bullish",
        "upgrade",
        "growth",
        "surge",
        "record"
    ]


    bearish_words = [
        "hack",
        "ban",
        "lawsuit",
        "crash",
        "bearish",
        "scam",
        "drop",
        "loss"
    ]


    score = 0


    for word in bullish_words:

        if word in news:
            score += 1



    for word in bearish_words:

        if word in news:
            score -= 1



    if score > 0:

        return {
            "sentiment": "BULLISH 🟢",
            "score": score
        }


    elif score < 0:

        return {
            "sentiment": "BEARISH 🔴",
            "score": score
        }


    else:

        return {
            "sentiment": "NEUTRAL 🟡",
            "score": 0
        }
