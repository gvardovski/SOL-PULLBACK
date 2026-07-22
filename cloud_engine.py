from live_signal import get_signal
from trade_simulator import calculate_trade
from paper_engine import (
    load_position,
    open_long,
    check_position,
    calculate_balance,
    update_equity
)

# =====================================================
# SETTINGS
# =====================================================

START_BALANCE = 10_000

# =====================================================
# MAIN ENGINE
# =====================================================

def engine_tick():
    """
    One cloud-safe engine cycle.

    Flow:
    1. Get live signal from Bybit
    2. Validate data
    3. Check existing position
    4. Exit if TP/SL hit
    5. Open new trade if BUY signal
    6. Update equity curve
    7. Return signal for dashboard rendering
    """

    # -------------------------------------------------
    # GET SIGNAL
    # -------------------------------------------------

    signal = get_signal()

    # Provider/API error
    if signal.get("signal") == "ERROR":
        return signal

    price = signal.get("price")

    # Invalid price
    if price is None:
        return {
            "signal": "ERROR",
            "error": "Price is None"
        }

    # -------------------------------------------------
    # CURRENT STATE
    # -------------------------------------------------

    balance = calculate_balance(START_BALANCE)

    position = load_position()

    # -------------------------------------------------
    # EXIT LOGIC
    # -------------------------------------------------

    if position is not None:
        # check TP/SL on current price
        check_position(price)

    # -------------------------------------------------
    # ENTRY LOGIC
    # -------------------------------------------------

    else:
        if signal.get("signal") == "BUY":

            trade = calculate_trade(
                capital=balance,
                risk_percent=1.0,      # risk 1% of balance
                atr_multiplier=1.0,
                reward_ratio=4.0,
                price=price,
                atr=signal.get("atr", 1.0)
            )

            open_long(
                price=trade["price"],
                quantity=trade["quantity"],
                stop=trade["stop"],
                target=trade["target"]
            )

    # -------------------------------------------------
    # UPDATE EQUITY
    # -------------------------------------------------

    update_equity(calculate_balance(START_BALANCE))

    # Return the same signal for dashboard UI
    return signal