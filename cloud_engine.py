from live_signal import get_signal
from trade_simulator import calculate_trade
from paper_engine import (
    load_position,
    open_long,
    check_position,
    calculate_balance,
    update_equity
)

START_BALANCE = 10000

def engine_tick():

    signal = get_signal()
    price = signal["price"]

    balance = calculate_balance(START_BALANCE)

    position = load_position()

    # EXIT
    if position is not None:
        check_position(price)

    # ENTRY
    else:
        if signal["signal"] == "BUY":

            trade = calculate_trade(
                capital=balance,
                risk_percent=1,
                atr_multiplier=1,
                reward_ratio=4
            )

            open_long(
                price=trade["price"],
                quantity=trade["quantity"],
                stop=trade["stop"],
                target=trade["target"]
            )

    update_equity(calculate_balance(START_BALANCE))