def check_trade(
    buy_amount,
    buy_price,
    sell_price
):

    fee_percent = 0.1

    fee = fee_percent / 100


    quantity = buy_amount / buy_price


    sell_value = quantity * sell_price


    buy_fee = buy_amount * fee

    sell_fee = sell_value * fee


    total_fee = buy_fee + sell_fee


    profit_before_fee = sell_value - buy_amount


    final_profit = profit_before_fee - total_fee



    return {

        "buy_amount": round(buy_amount,2),

        "sell_value": round(sell_value,2),

        "fees": round(total_fee,2),

        "profit_before_fee": round(profit_before_fee,2),

        "final_profit": round(final_profit,2),

        "allowed": final_profit > 0

    }
