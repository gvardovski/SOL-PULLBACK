import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text: str):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")


def send_buy_alert(price, stop, target, quantity):

    text = f"""
🚀 *SOL LONG OPENED*

💰 Entry: `{price:.2f}`
📦 Quantity: `{quantity:.3f}`

🛑 Stop: `{stop:.2f}`
🎯 Target: `{target:.2f}`

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    send_message(text)


def send_close_alert(reason, entry, exit_price, pnl):

    emoji = "🎯" if reason == "TAKE PROFIT" else "🛑"

    text = f"""
{emoji} *SOL POSITION CLOSED*

📌 Reason: *{reason}*

➡️ Entry: `{entry:.2f}`
⬅️ Exit: `{exit_price:.2f}`

💵 PnL: `{pnl:.2f} USDT`

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    send_message(text)


def send_signal_alert(price):

    text = f"""
📡 *BUY SIGNAL DETECTED*

SOL/USDT

Current price: `{price:.2f}`

Pullback + breakout conditions satisfied.
"""

    send_message(text)