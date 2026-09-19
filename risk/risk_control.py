from datetime import datetime

from database.database import get_connection


# ============================================================
# ADAPTIVE RISK MANAGER
# ============================================================
#
# This module is the central risk-management system for
# CryptoAI Pro.
#
# Main goals:
# 1. Protect the account.
# 2. Adjust risk according to market conditions.
# 3. Reduce risk during drawdowns and losing streaks.
# 4. Keep position sizes within strict safety limits.
# 5. Remain compatible with the existing PaperTrader.
#
# ============================================================


# ============================================================
# ACCOUNT SAFETY SETTINGS
# ============================================================

MAX_DAILY_LOSS = 20.0
MAX_DAILY_SELLS = 5


# ============================================================
# ADAPTIVE RISK SETTINGS
# ============================================================

# Normal risk used when conditions are healthy.
BASE_RISK_PER_TRADE = 0.02

# Absolute safety limits.
MIN_RISK_PER_TRADE = 0.005
MAX_RISK_PER_TRADE = 0.02

# Maximum amount of account capital that can be used
# for one position.
MAX_POSITION_SIZE = 0.50

# Minimum position size when a trade is accepted.
MIN_POSITION_SIZE = 0.10


# ============================================================
# MARKET VOLATILITY SETTINGS
# ============================================================
#
# stop_loss_distance_percent is used as a simple volatility
# proxy for now.
#
# A larger stop distance means the market is behaving more
# aggressively, so the position should become smaller.
#

LOW_VOLATILITY_PERCENT = 1.5
HIGH_VOLATILITY_PERCENT = 4.0


# ============================================================
# PERFORMANCE ADAPTATION
# ============================================================

# Reduce risk after a losing streak.
LOSING_STREAK_1_RISK_MULTIPLIER = 0.80
LOSING_STREAK_2_RISK_MULTIPLIER = 0.60
LOSING_STREAK_3_RISK_MULTIPLIER = 0.50

# Reduce risk when account drawdown becomes significant.
DRAWDOWN_WARNING_PERCENT = 10.0
DRAWDOWN_DANGER_PERCENT = 20.0

DRAWDOWN_WARNING_MULTIPLIER = 0.75
DRAWDOWN_DANGER_MULTIPLIER = 0.50


# ============================================================
# SETUP QUALITY
# ============================================================
#
# The decision engine can later provide a strategy score.
# For now this is optional.
#

STRONG_SETUP_SCORE = 80
WEAK_SETUP_SCORE = 50

STRONG_SETUP_MULTIPLIER = 1.00
WEAK_SETUP_MULTIPLIER = 0.75


# ============================================================
# DAILY RISK CHECK
# ============================================================

def check_risk():
    """
    Check whether the bot is allowed to open a new position.

    Returns:
        True  -> trading is allowed
        False -> trading should be stopped
    """

    connection = get_connection()
    cursor = connection.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # OPEN POSITION CHECK
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT coin
        FROM positions
        WHERE id = 1
        """
    )

    open_position = cursor.fetchone()

    if open_position is not None:

        connection.close()

        return True

    # --------------------------------------------------------
    # TODAY'S COMPLETED TRADES
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            action,
            profit
        FROM trades
        WHERE time LIKE ?
        ORDER BY id
        """,
        (f"{today}%",)
    )

    trades = cursor.fetchall()

    connection.close()

    total_loss = 0.0
    completed_trades = 0

    for action, profit in trades:

        if action == "SELL":

            completed_trades += 1

            if profit is not None and profit < 0:

                total_loss += abs(profit)

    # --------------------------------------------------------
    # DAILY LOSS LIMIT
    # --------------------------------------------------------

    if total_loss >= MAX_DAILY_LOSS:

        print(
            "RISK STOP: Daily loss limit reached 🔴"
        )

        return False

    # --------------------------------------------------------
    # DAILY TRADE LIMIT
    # --------------------------------------------------------

    if completed_trades >= MAX_DAILY_SELLS:

        print(
            "RISK STOP: Daily completed-trade limit reached 🔴"
        )

        return False

    return True


# ============================================================
# GET RECENT TRADING PERFORMANCE
# ============================================================

def get_recent_performance(limit=10):
    """
    Read recent completed trades from the database.

    Returns a dictionary containing:
        wins
        losses
        win_rate
        losing_streak
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT profit
        FROM trades
        WHERE action = 'SELL'
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    connection.close()

    profits = []

    for row in rows:

        profit = row[0]

        if profit is not None:

            profits.append(float(profit))

    if not profits:

        return {
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "losing_streak": 0
        }

    wins = 0
    losses = 0

    for profit in profits:

        if profit > 0:
            wins += 1

        elif profit < 0:
            losses += 1

    win_rate = (
        wins / len(profits)
    ) * 100

    # --------------------------------------------------------
    # LOSING STREAK
    # --------------------------------------------------------

    losing_streak = 0

    for profit in profits:

        if profit < 0:

            losing_streak += 1

        else:

            break

    return {
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "losing_streak": losing_streak
    }


# ============================================================
# CALCULATE DRAWDOWN
# ============================================================

def calculate_drawdown(
    current_balance,
    peak_balance
):
    """
    Calculate account drawdown percentage.

    Example:

        Peak = ₹200
        Current = ₹180

        Drawdown = 10%
    """

    if peak_balance <= 0:

        return 0.0

    if current_balance < 0:

        current_balance = 0.0

    drawdown = (
        (peak_balance - current_balance)
        / peak_balance
    ) * 100

    return max(0.0, drawdown)


# ============================================================
# VOLATILITY MULTIPLIER
# ============================================================

def get_volatility_multiplier(
    stop_loss_distance_percent
):
    """
    Adjust risk according to market volatility.

    We use the stop-loss distance as a simple volatility
    indicator for this first adaptive version.

    Smaller stop distance:
        normal risk

    Larger stop distance:
        reduced risk
    """

    if stop_loss_distance_percent <= 0:

        return 0.0

    if stop_loss_distance_percent <= LOW_VOLATILITY_PERCENT:

        return 1.00

    if stop_loss_distance_percent >= HIGH_VOLATILITY_PERCENT:

        return 0.50

    # Gradually reduce risk between the two thresholds.

    volatility_range = (
        HIGH_VOLATILITY_PERCENT
        - LOW_VOLATILITY_PERCENT
    )

    position_in_range = (
        stop_loss_distance_percent
        - LOW_VOLATILITY_PERCENT
    ) / volatility_range

    multiplier = (
        1.00
        - (position_in_range * 0.50)
    )

    return multiplier


# ============================================================
# LOSING STREAK MULTIPLIER
# ============================================================

def get_losing_streak_multiplier(
    losing_streak
):
    """
    Reduce risk after consecutive losing trades.
    """

    if losing_streak >= 3:

        return LOSING_STREAK_3_RISK_MULTIPLIER

    if losing_streak == 2:

        return LOSING_STREAK_2_RISK_MULTIPLIER

    if losing_streak == 1:

        return LOSING_STREAK_1_RISK_MULTIPLIER

    return 1.00


# ============================================================
# DRAWDOWN MULTIPLIER
# ============================================================

def get_drawdown_multiplier(
    drawdown_percent
):
    """
    Reduce risk when the account is experiencing drawdown.
    """

    if drawdown_percent >= DRAWDOWN_DANGER_PERCENT:

        return DRAWDOWN_DANGER_MULTIPLIER

    if drawdown_percent >= DRAWDOWN_WARNING_PERCENT:

        return DRAWDOWN_WARNING_MULTIPLIER

    return 1.00


# ============================================================
# SETUP QUALITY MULTIPLIER
# ============================================================

def get_setup_quality_multiplier(
    setup_score=None
):
    """
    Adjust risk based on strategy confidence.

    This is optional because the current system may not always
    provide a score.

    No score:
        normal risk

    Weak score:
        lower risk

    Strong score:
        normal risk
    """

    if setup_score is None:

        return 1.00

    if setup_score < WEAK_SETUP_SCORE:

        return 0.75

    if setup_score >= STRONG_SETUP_SCORE:

        return STRONG_SETUP_MULTIPLIER

    return WEAK_SETUP_MULTIPLIER


# ============================================================
# ADAPTIVE RISK PERCENTAGE
# ============================================================

def calculate_adaptive_risk(
    balance,
    entry_price,
    stop_loss_price,
    peak_balance=None,
    losing_streak=None,
    setup_score=None
):
    """
    Calculate the final risk percentage for a trade.

    The calculation combines:

        Base risk
            ↓
        Market volatility
            ↓
        Account drawdown
            ↓
        Losing streak
            ↓
        Setup quality
            ↓
        Safety limits

    Returns a decimal.

    Example:

        0.02 = 2%
        0.01 = 1%
        0.005 = 0.5%
    """

    if balance <= 0:

        return 0.0

    if entry_price <= 0:

        return 0.0

    if stop_loss_price <= 0:

        return 0.0

    risk_distance = abs(
        entry_price - stop_loss_price
    )

    if risk_distance <= 0:

        return 0.0

    # --------------------------------------------------------
    # STOP-LOSS DISTANCE
    # --------------------------------------------------------

    stop_loss_distance_percent = (
        risk_distance
        / entry_price
    ) * 100

    # --------------------------------------------------------
    # BASE RISK
    # --------------------------------------------------------

    risk_percent = BASE_RISK_PER_TRADE

    # --------------------------------------------------------
    # VOLATILITY ADJUSTMENT
    # --------------------------------------------------------

    volatility_multiplier = get_volatility_multiplier(
        stop_loss_distance_percent
    )

    risk_percent *= volatility_multiplier

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    if losing_streak is None:

        performance = get_recent_performance()

        losing_streak = performance["losing_streak"]

    losing_streak_multiplier = (
        get_losing_streak_multiplier(
            losing_streak
        )
    )

    risk_percent *= losing_streak_multiplier

    # --------------------------------------------------------
    # DRAWDOWN
    # --------------------------------------------------------

    if peak_balance is not None:

        drawdown_percent = calculate_drawdown(
            balance,
            peak_balance
        )

        drawdown_multiplier = (
            get_drawdown_multiplier(
                drawdown_percent
            )
        )

        risk_percent *= drawdown_multiplier

    # --------------------------------------------------------
    # SETUP QUALITY
    # --------------------------------------------------------

    setup_multiplier = (
        get_setup_quality_multiplier(
            setup_score
        )
    )

    risk_percent *= setup_multiplier

    # --------------------------------------------------------
    # FINAL SAFETY LIMIT
    # --------------------------------------------------------

    risk_percent = max(
        MIN_RISK_PER_TRADE,
        risk_percent
    )

    risk_percent = min(
        MAX_RISK_PER_TRADE,
        risk_percent
    )

    return risk_percent


# ============================================================
# ADAPTIVE POSITION SIZE
# ============================================================

def calculate_adaptive_position_size(
    balance,
    entry_price,
    stop_loss_price,
    peak_balance=None,
    losing_streak=None,
    setup_score=None
):
    """
    Calculate position value using adaptive risk.

    Returns the amount of account capital that should be
    placed into the trade.
    """

    if balance <= 0:

        return 0.0

    if entry_price <= 0:

        return 0.0

    if stop_loss_price <= 0:

        return 0.0

    risk_per_unit = abs(
        entry_price
        - stop_loss_price
    )

    if risk_per_unit <= 0:

        return 0.0

    # --------------------------------------------------------
    # ADAPTIVE RISK
    # --------------------------------------------------------

    risk_percent = calculate_adaptive_risk(
        balance=balance,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price,
        peak_balance=peak_balance,
        losing_streak=losing_streak,
        setup_score=setup_score
    )

    if risk_percent <= 0:

        return 0.0

    # --------------------------------------------------------
    # MAXIMUM MONEY WE ARE WILLING TO LOSE
    # --------------------------------------------------------

    max_risk_amount = (
        balance
        * risk_percent
    )

    # --------------------------------------------------------
    # QUANTITY
    # --------------------------------------------------------

    quantity = (
        max_risk_amount
        / risk_per_unit
    )

    # --------------------------------------------------------
    # POSITION VALUE
    # --------------------------------------------------------

    position_value = (
        quantity
        * entry_price
    )

    # --------------------------------------------------------
    # HARD MAXIMUM
    # --------------------------------------------------------

    max_allowed_value = (
        balance
        * MAX_POSITION_SIZE
    )

    position_value = min(
        position_value,
        max_allowed_value
    )

    # --------------------------------------------------------
    # MINIMUM POSITION
    # --------------------------------------------------------
    #
    # Only apply the minimum if the calculated position is
    # large enough to respect the minimum without exceeding
    # the account balance.
    #

    min_allowed_value = (
        balance
        * MIN_POSITION_SIZE
    )

    if (
        position_value > 0
        and position_value < min_allowed_value
    ):

        position_value = min_allowed_value

    # --------------------------------------------------------
    # NEVER USE MORE THAN THE ACCOUNT
    # --------------------------------------------------------

    position_value = min(
        position_value,
        balance
    )

    return position_value


# ============================================================
# BACKWARD-COMPATIBLE POSITION SIZE
# ============================================================

def calculate_position_size(
    balance,
    entry_price,
    stop_loss_price
):
    """
    Existing project interface.

    PaperTrader already imports this function.

    It now uses the Adaptive Risk Manager automatically.

    This means existing code does not need to know about the
    internal adaptive calculations.
    """

    return calculate_adaptive_position_size(
        balance=balance,
        entry_price=entry_price,
        stop_loss_price=stop_loss_price
    )