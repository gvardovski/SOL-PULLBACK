import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import hashlib
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, UTC
from paper_engine import load_position
from dotenv import load_dotenv
from cloud_engine import engine_tick


load_dotenv()

DASHBOARD_USERNAME = os.getenv("DASHBOARD_USERNAME")
DASHBOARD_PASSWORD_HASH = os.getenv("DASHBOARD_PASSWORD_HASH")

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="SOL Pullback v4",
    page_icon="🚀",
    layout="wide"
)

# =====================================================
# AUTHENTICATION
# =====================================================

def check_login(username, password):

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    return (
        username == DASHBOARD_USERNAME and
        password_hash == DASHBOARD_PASSWORD_HASH
    )

# Инициализация состояния
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Если не залогинен — показываем форму
if not st.session_state.authenticated:

    st.title("🔐 SOL Pullback v4 Login")

    with st.form("login_form"):

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "Login"
        )

        if login_button:

            if check_login(username, password):

                st.session_state.authenticated = True
                st.success("Login successful")
                st.rerun()

            else:
                st.error("Invalid username or password")

    st.stop()

# =====================================================
# AUTO REFRESH (WORKING)
# =====================================================

refresh_count = st_autorefresh(
    interval=30 * 1000,  # 30 seconds
    key="sol_dashboard_refresh"
)

try:
    signal = engine_tick()

except Exception as e:
    st.error(f"Engine error: {e}")
    st.stop()

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

TRADES_FILE = os.path.join(DATA_DIR, "trades.csv")
EQUITY_FILE = os.path.join(DATA_DIR, "equity.csv")
SYSTEM_FILE = os.path.join(DATA_DIR, "system.json")

# =====================================================
# UPTIME
# =====================================================

uptime_str = "00:00:00"

try:
    if os.path.exists(SYSTEM_FILE):

        with open(SYSTEM_FILE, "r") as f:
            system = json.load(f)

        start_time = datetime.fromisoformat(system["start_time"])

        uptime = datetime.now(UTC) - start_time

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            uptime_str = f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

except Exception as e:
    uptime_str = f"error: {e}"

# =====================================================
# LOAD DATA
# =====================================================

def load_trades():
    if os.path.exists(TRADES_FILE):
        try:
            return pd.read_csv(TRADES_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def load_equity():
    if os.path.exists(EQUITY_FILE):
        try:
            return pd.read_csv(EQUITY_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

trades = load_trades()
equity = load_equity()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("⚙️ Engine Status")

if os.path.exists(os.path.join(DATA_DIR, "position.json")):
    st.sidebar.success("🟢 Position active")
else:
    st.sidebar.info("⏳ Waiting for signal")

st.sidebar.write("Auto refresh:", "30s")
st.sidebar.write("Refresh count:", refresh_count)
st.sidebar.write("Uptime:", uptime_str)

st.sidebar.divider()

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

# =====================================================
# TITLE
# =====================================================

st.title("🚀 SOL Trend Pullback v4")
st.caption("Automatic Paper Trading Dashboard")

# =====================================================
# LIVE SIGNAL
# =====================================================

st.header("📡 Live Signal")

c1, c2, c3 = st.columns(3)

# ---------- PRICE ----------

price = signal.get("price")

if price is not None:
    c1.metric("SOL Price", f"${price:.2f}")
else:
    c1.metric("SOL Price", "N/A")

# ---------- REGIME ----------

regime = signal.get("regime", "N/A")

if regime == "BULL":
    c2.success("🟢 BULL")
elif regime == "BEAR":
    c2.error("🔴 BEAR")
else:
    c2.warning("⚪ N/A")

# ---------- SIGNAL ----------

sig = signal.get("signal", "WAIT")

if sig == "BUY":
    c3.success("🚀 BUY")
elif sig == "ERROR":
    c3.error("❌ ERROR")
else:
    c3.info("WAIT")

# ---------- ERROR MESSAGE ----------

if sig == "ERROR":
    st.error(signal.get("error", "Unknown error"))

# =====================================================
# INDICATORS
# =====================================================

st.subheader("📈 Indicators")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "EMA20",
        signal.get("ema20", "-")
    )

with c2:
    st.metric(
        "EMA50",
        signal.get("ema50", "-")
    )

with c3:
    st.metric(
        "ADX",
        signal.get("adx", "-")
    )

with c4:
    st.metric(
        "ATR",
        signal.get("atr", "-")
    )

# =====================================================
# PAPER POSITION
# =====================================================

st.divider()
st.header("📌 Paper Position")

position = load_position()

if position is None:
    st.warning("No active position")

else:
    st.success("🟢 LONG POSITION")

    current_price = signal.get("price")

    if current_price is None:
        st.warning("Live price unavailable")
        st.stop()

    entry = float(position["entry"])
    quantity = float(position["quantity"])

    pnl = (current_price - entry) * quantity
    pnl_percent = (current_price - entry) / entry * 100

    p1, p2, p3, p4 = st.columns(4)

    p1.metric("Entry", f"${entry:.2f}")
    p2.metric("Current", f"${current_price:.2f}")
    p3.metric("PnL", f"${pnl:.2f}")
    p4.metric("Return", f"{pnl_percent:.2f}%")

    st.json({
        "entry": position["entry"],
        "quantity": position["quantity"],
        "stop": position["stop"],
        "target": position["target"],
        "opened": position["time"]
    })

# =====================================================
# PERFORMANCE
# =====================================================

st.divider()
st.header("📊 Performance")

total_return = 0
drawdown = 0
winrate = 0
profit_factor = 0

# ---------- Equity metrics ----------

if not equity.empty and "equity" in equity.columns:
    equity["equity"] = pd.to_numeric(
        equity["equity"],
        errors="coerce"
    )

    equity = equity.dropna(subset=["equity"])

    if len(equity) > 1:
        start = equity["equity"].iloc[0]
        end = equity["equity"].iloc[-1]

        total_return = (end / start - 1) * 100

        drawdown = (
            equity["equity"] /
            equity["equity"].cummax() - 1
        ).min() * 100

# ---------- Trade metrics ----------

if not trades.empty and "pnl" in trades.columns:
    trades["pnl"] = pd.to_numeric(
        trades["pnl"],
        errors="coerce"
    )

    trades = trades.dropna(subset=["pnl"])

    if len(trades) > 0:
        wins = trades[trades.pnl > 0]
        losses = trades[trades.pnl < 0]

        winrate = len(wins) / len(trades) * 100

        if len(losses) > 0:
            profit_factor = (
                wins.pnl.sum() /
                abs(losses.pnl.sum())
            )

# ---------- Display ----------

m1, m2, m3, m4 = st.columns(4)

m1.metric("Return", f"{total_return:.2f}%")
m2.metric("Win Rate", f"{winrate:.1f}%")
m3.metric("Profit Factor", f"{profit_factor:.2f}")
m4.metric("Max DD", f"{drawdown:.2f}%")

# =====================================================
# EQUITY CURVE
# =====================================================

st.divider()

if not equity.empty and "time" in equity.columns:
    st.subheader("📈 Equity Curve")

    equity["time"] = pd.to_datetime(
        equity["time"],
        errors="coerce",
        format="mixed"
    )

    equity = equity.dropna(subset=["time"])

    equity = equity.sort_values("time")

    fig = px.line(
        equity,
        x="time",
        y="equity",
        title="Paper Equity"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

else:
    st.info("Equity data not available yet")

# =====================================================
# TRADE HISTORY
# =====================================================

st.divider()
st.subheader("📜 Trade History")

if not trades.empty:
    st.dataframe(
        trades.sort_index(ascending=False),
        width='stretch'
    )
else:
    st.info("No closed trades yet")

# =====================================================
# FOOTER
# =====================================================

st.caption(
    "SOL Pullback v4 • Kraken live data • Auto-refresh every 30s • Paper Trading"
)