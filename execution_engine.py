import time
from datetime import datetime

from live_signal import get_signal
from trade_simulator import calculate_trade

from paper_engine import (
    load_position,
    open_long,
    check_position,
    update_equity,
    calculate_balance
)

from telegram_bot import send_signal_alert

# =====================================================
# SETTINGS
# =====================================================

START_BALANCE = 10000
RISK_PER_TRADE = 1       # %
ATR_MULTIPLIER = 1.0
REWARD_RATIO = 4
LOOP_SECONDS = 60

# =====================================================
# ENGINE
# =====================================================

print("🚀 SOL Pullback v4 Paper Engine Started")

last_signal_time = None

def run():

    print("🚀 SOL Pullback v4 Paper Engine Started")

    last_signal_time = None

    while True:

        try:

            # Current balance
            balance = calculate_balance(START_BALANCE)

            # Get live signal
            signal = get_signal()
            price = signal["price"]

            # Current position
            position = load_position()

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"Price: {price:.2f} | "
                f"Signal: {signal['signal']} | "
                f"Position: {'YES' if position else 'NO'} | "
                f"Balance: {balance:.2f}"
            )

            # EXIT
            if position is not None:

                result = check_position(price)

                if result not in [None, "HOLD"]:
                    balance = calculate_balance(START_BALANCE)
                    print(f"📊 New balance: {balance:.2f}")

            # ENTRY
            else:

                if signal["signal"] == "BUY":

                    signal_key = datetime.utcnow().strftime('%Y-%m-%d-%H')

                    if signal_key != last_signal_time:

                        last_signal_time = signal_key

                        send_signal_alert(price)

                        trade = calculate_trade(
                            capital=balance,
                            risk_percent=RISK_PER_TRADE,
                            atr_multiplier=ATR_MULTIPLIER,
                            reward_ratio=REWARD_RATIO
                        )

                        open_long(
                            price=trade["price"],
                            quantity=trade["quantity"],
                            stop=trade["stop"],
                            target=trade["target"]
                        )

            # Update equity
            balance = calculate_balance(START_BALANCE)
            update_equity(balance)

            time.sleep(LOOP_SECONDS)

        except Exception as e:

            print(f"❌ Engine error: {e}")
            time.sleep(30)


if __name__ == "__main__":
    run()