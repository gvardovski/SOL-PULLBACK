import os
import json
import pandas as pd
from datetime import datetime

from telegram_bot import (
    send_buy_alert,
    send_close_alert
)

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

POSITION_FILE = os.path.join(DATA_DIR, "position.json")
TRADES_FILE = os.path.join(DATA_DIR, "trades.csv")
EQUITY_FILE = os.path.join(DATA_DIR, "equity.csv")

# =====================================================
# INIT
# =====================================================

def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(TRADES_FILE):
        pd.DataFrame(columns=[
            "entry_time",
            "exit_time",
            "side",
            "entry",
            "exit",
            "quantity",
            "pnl",
            "reason"
        ]).to_csv(TRADES_FILE, index=False)

    if not os.path.exists(EQUITY_FILE):
        pd.DataFrame(columns=[
            "time",
            "equity"
        ]).to_csv(EQUITY_FILE, index=False)

init_storage()

# =====================================================
# POSITION
# =====================================================

def load_position():
    if not os.path.exists(POSITION_FILE):
        return None

    with open(POSITION_FILE, "r") as f:
        return json.load(f)

def save_position(position):
    with open(POSITION_FILE, "w") as f:
        json.dump(position, f, indent=4)

def delete_position():
    if os.path.exists(POSITION_FILE):
        os.remove(POSITION_FILE)

# =====================================================
# OPEN LONG
# =====================================================

def open_long(price, quantity, stop, target):
    position = {
        "side": "LONG",
        "entry": float(price),
        "quantity": float(quantity),
        "stop": float(stop),
        "target": float(target),
        "entry_time": datetime.utcnow().isoformat()
    }

    save_position(position)

    # Telegram
    send_buy_alert(
        price=price,
        stop=stop,
        target=target,
        quantity=quantity
    )

    print(f"🟢 OPEN LONG @ {price:.2f}")

    return position

# =====================================================
# SAVE TRADE
# =====================================================

def save_trade(trade):
    df = pd.DataFrame([trade])

    df.to_csv(
        TRADES_FILE,
        mode="a",
        header=not os.path.exists(TRADES_FILE) or os.path.getsize(TRADES_FILE) == 0,
        index=False
    )

# =====================================================
# CLOSE POSITION
# =====================================================

def close_position(exit_price, reason):
    position = load_position()

    if position is None:
        return None

    entry = float(position["entry"])
    quantity = float(position["quantity"])

    pnl = (exit_price - entry) * quantity

    trade = {
        "entry_time": position["entry_time"],
        "exit_time": datetime.utcnow().isoformat(),
        "side": "LONG",
        "entry": round(entry, 4),
        "exit": round(exit_price, 4),
        "quantity": round(quantity, 6),
        "pnl": round(pnl, 2),
        "reason": reason
    }

    save_trade(trade)

    # Telegram
    send_close_alert(
        reason=reason,
        entry=entry,
        exit_price=exit_price,
        pnl=pnl
    )

    delete_position()

    print(f"🔴 CLOSE {reason} @ {exit_price:.2f} | PnL: {pnl:.2f}")

    return trade

# =====================================================
# CHECK POSITION
# =====================================================

def check_position(current_price):
    position = load_position()

    if position is None:
        return None

    stop = float(position["stop"])
    target = float(position["target"])

    if current_price <= stop:
        return close_position(current_price, "STOP LOSS")

    if current_price >= target:
        return close_position(current_price, "TAKE PROFIT")

    return "HOLD"

# =====================================================
# EQUITY
# =====================================================

def update_equity(balance):
    row = pd.DataFrame([{
        "time": datetime.utcnow().isoformat(),
        "equity": round(balance, 2)
    }])

    row.to_csv(
        EQUITY_FILE,
        mode="a",
        header=not os.path.exists(EQUITY_FILE) or os.path.getsize(EQUITY_FILE) == 0,
        index=False
    )

# =====================================================
# ACCOUNT BALANCE
# =====================================================

def calculate_balance(start_balance=10000):
    if not os.path.exists(TRADES_FILE):
        return start_balance

    try:
        trades = pd.read_csv(TRADES_FILE)

        if "pnl" not in trades.columns:
            return start_balance

        pnl = pd.to_numeric(trades["pnl"], errors="coerce").fillna(0).sum()

        return round(start_balance + pnl, 2)

    except Exception:
        return start_balance