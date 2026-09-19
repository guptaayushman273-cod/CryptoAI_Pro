# ============================================================
# CRYPTOAI PRO - RISK MANAGER
# ============================================================

DEFAULT_RISK_PERCENT = 2.0

# Maximum percentage of account balance that can be
# allocated to a single position.
MAX_POSITION_PERCENT = 25.0

# Stop-loss and take-profit configuration.
STOP_LOSS_PERCENT = 3.0
TAKE_PROFIT_PERCENT = 6.0

# Minimum acceptable reward/risk ratio.
MIN_RISK_REWARD_RATIO = 1.5


# ============================================================
# CALCULATE TRADE
# ============================================================

def calculate_trade(
    balance,
    price,
    risk_percent=DEFAULT_RISK_PERCENT,
    max_position_percent=MAX_POSITION_PERCENT,
    stop_loss_percent=STOP_LOSS_PERCENT,
    take_profit_percent=TAKE_PROFIT_PERCENT
):
    """
    Calculate a risk-controlled trade.

    Returns:
        dict containing:
        - approved
        - balance
        - risk amount
        - position size
        - quantity
        - buy price
        - stop loss
        - take profit
        - risk/reward ratio
    """

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    try:

        balance = float(balance)
        price = float(price)
        risk_percent = float(risk_percent)
        max_position_percent = float(
            max_position_percent
        )
        stop_loss_percent = float(
            stop_loss_percent
        )
        take_profit_percent = float(
            take_profit_percent
        )

    except (TypeError, ValueError):

        return {
            "approved": False,
            "reason": "Invalid numeric risk parameters."
        }

    if balance <= 0:

        return {
            "approved": False,
            "reason": "Account balance must be positive."
        }

    if price <= 0:

        return {
            "approved": False,
            "reason": "Market price must be positive."
        }

    if not 0 < risk_percent <= 5:

        return {
            "approved": False,
            "reason": (
                "Risk percent must be greater than "
                "0 and no more than 5%."
            )
        }

    if not 0 < max_position_percent <= 100:

        return {
            "approved": False,
            "reason": "Invalid maximum position percentage."
        }

    if stop_loss_percent <= 0:

        return {
            "approved": False,
            "reason": "Stop-loss percentage must be positive."
        }

    if take_profit_percent <= 0:

        return {
            "approved": False,
            "reason": "Take-profit percentage must be positive."
        }

    # --------------------------------------------------------
    # RISK AMOUNT
    # --------------------------------------------------------

    risk_amount = (
        balance
        * (risk_percent / 100)
    )

    # --------------------------------------------------------
    # STOP LOSS / TAKE PROFIT
    # --------------------------------------------------------

    stop_loss = (
        price
        * (
            1
            - stop_loss_percent / 100
        )
    )

    take_profit = (
        price
        * (
            1
            + take_profit_percent / 100
        )
    )

    risk_per_unit = (
        price - stop_loss
    )

    reward_per_unit = (
        take_profit - price
    )

    if risk_per_unit <= 0:

        return {
            "approved": False,
            "reason": "Invalid stop-loss calculation."
        }

    # --------------------------------------------------------
    # QUANTITY BASED ON RISK
    # --------------------------------------------------------

    risk_based_quantity = (
        risk_amount
        / risk_per_unit
    )

    risk_based_position = (
        risk_based_quantity
        * price
    )

    # --------------------------------------------------------
    # MAXIMUM POSITION CAP
    # --------------------------------------------------------

    max_position_value = (
        balance
        * (
            max_position_percent
            / 100
        )
    )

    actual_position_value = min(
        risk_based_position,
        max_position_value
    )

    quantity = (
        actual_position_value
        / price
    )

    # --------------------------------------------------------
    # ACTUAL RISK
    # --------------------------------------------------------

    actual_risk_amount = (
        quantity
        * risk_per_unit
    )

    actual_risk_percent = (
        actual_risk_amount
        / balance
        * 100
    )

    # --------------------------------------------------------
    # RISK / REWARD
    # --------------------------------------------------------

    risk_reward_ratio = (
        reward_per_unit
        / risk_per_unit
    )

    # --------------------------------------------------------
    # FINAL APPROVAL
    # --------------------------------------------------------

    approved = (
        quantity > 0
        and actual_position_value <= balance
        and risk_reward_ratio
        >= MIN_RISK_REWARD_RATIO
    )

    if approved:

        reason = (
            "Trade passed risk management."
        )

    else:

        reason = (
            "Trade rejected by risk management."
        )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "approved":
            approved,

        "reason":
            reason,

        "balance":
            round(balance, 2),

        "buy_price":
            round(price, 8),

        "quantity":
            round(quantity, 8),

        "position_value":
            round(
                actual_position_value,
                2
            ),

        "max_position_value":
            round(
                max_position_value,
                2
            ),

        "risk_percent_limit":
            round(
                risk_percent,
                2
            ),

        "risk_amount_limit":
            round(
                risk_amount,
                2
            ),

        "actual_risk_amount":
            round(
                actual_risk_amount,
                2
            ),

        "actual_risk_percent":
            round(
                actual_risk_percent,
                2
            ),

        "stop_loss":
            round(
                stop_loss,
                8
            ),

        "stop_loss_percent":
            round(
                stop_loss_percent,
                2
            ),

        "take_profit":
            round(
                take_profit,
                8
            ),

        "take_profit_percent":
            round(
                take_profit_percent,
                2
            ),

        "risk_reward_ratio":
            round(
                risk_reward_ratio,
                2
            )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CRYPTOAI PRO - RISK MANAGER TEST")
    print("=" * 60)

    test_balance = 200
    test_price = 2636.96

    result = calculate_trade(
        balance=test_balance,
        price=test_price
    )

    print()
    print(f"Account Balance: ${test_balance}")
    print(f"Market Price:    ${test_price}")

    print()
    print("Risk Analysis")
    print("-" * 40)

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )

    print()
    print("=" * 60)

    if result["approved"]:

        print("TRADE APPROVED BY RISK MANAGER")

    else:

        print("TRADE REJECTED BY RISK MANAGER")

    print("=" * 60)