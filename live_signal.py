import ccxt
import pandas as pd
from ta.trend import EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange

# =====================================================
# EXCHANGE
# =====================================================

exchange = ccxt.bybit({
    "enableRateLimit": True
})

SYMBOL = "SOL/USDT"

# =====================================================
# LOAD DATA
# =====================================================

def load_data(timeframe="1h", limit=300):

    candles = exchange.fetch_ohlcv(
        SYMBOL,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="ms"
    )

    df = df.set_index("timestamp")

    return df

# =====================================================
# SOL TREND PULLBACK V4
# =====================================================

def get_signal():

    try:

        # 1H data
        df = load_data("1h", 300)

        # 4H trend
        df4 = load_data("4h", 200)

        # -------------------------
        # 4H regime
        # -------------------------

        ema50_4h = EMAIndicator(
            df4["close"],
            window=50
        ).ema_indicator()

        ema200_4h = EMAIndicator(
            df4["close"],
            window=200
        ).ema_indicator()

        bull_regime = (
            ema50_4h.iloc[-1] > ema200_4h.iloc[-1]
        )

        # -------------------------
        # 1H indicators
        # -------------------------

        df["ema20"] = EMAIndicator(
            df["close"],
            window=20
        ).ema_indicator()

        df["ema50"] = EMAIndicator(
            df["close"],
            window=50
        ).ema_indicator()

        df["atr"] = AverageTrueRange(
            df["high"],
            df["low"],
            df["close"],
            window=14
        ).average_true_range()

        df["adx"] = ADXIndicator(
            df["high"],
            df["low"],
            df["close"],
            window=14
        ).adx()

        last = df.iloc[-1]

        # -------------------------
        # Conditions
        # -------------------------

        trend = (
            last["close"] > last["ema20"] > last["ema50"]
        )

        pullback = (
            abs(last["close"] - last["ema20"]) / last["ema20"]
        ) < 0.01

        momentum = last["adx"] > 25

        buy = bull_regime and trend and pullback and momentum

        return {
            "symbol": SYMBOL,
            "signal": "BUY" if buy else "WAIT",
            "price": round(float(last["close"]), 2),
            "regime": "BULL" if bull_regime else "BEAR",
            "adx": round(float(last["adx"]), 1),
            "ema20": round(float(last["ema20"]), 2),
            "ema50": round(float(last["ema50"]), 2),
            "atr": round(float(last["atr"]), 2),
            "time": str(df.index[-1])
        }

    except Exception as e:

        return {
            "symbol": SYMBOL,
            "signal": "ERROR",
            "price": None,
            "regime": "N/A",
            "adx": None,
            "ema20": None,
            "ema50": None,
            "atr": None,
            "time": None,
            "error": str(e)
        }