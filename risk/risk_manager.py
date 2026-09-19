def calculate_trade(amount, price):

    risk_percent = 2   # risk only 2%


    risk_amount = amount * (risk_percent / 100)


    stop_loss = price * 0.97
    take_profit = price * 1.06


    quantity = risk_amount / (price - stop_loss)


    return {
        "buy_price": price,
        "quantity": round(quantity, 6),
        "stop_loss": round(stop_loss, 6),
        "take_profit": round(take_profit, 6)
    }
