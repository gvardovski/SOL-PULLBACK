import ccxt
import pandas as pd
import requests
from ta.trend import EMAIndicator


def load_data(
    timeframe="1h",
    limit=200
):

    url = "https://api.binance.com/api/v3/klines"


    params = {
        "symbol": "SOLUSDT",
        "interval": timeframe,
        "limit": limit
    }


    r = requests.get(
        url,
        params=params,
        timeout=10
    )

    r.raise_for_status()


    candles = r.json()


    df = pd.DataFrame(
        candles,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "buy_volume",
            "buy_quote",
            "ignore"
        ]
    )


    df["time"] = pd.to_datetime(
        df["time"],
        unit="ms"
    )


    numeric = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    df[numeric] = df[numeric].astype(float)


    return df.set_index("time")


def get_signal():


    df = load_data("1h")


    # indicators

    df["ma7"] = (
        df.close
        .rolling(7)
        .mean()
    )

    df["ma14"] = (
        df.close
        .rolling(14)
        .mean()
    )

    df["ma30"] = (
        df.close
        .rolling(30)
        .mean()
    )



    # 4H regime

    htf = load_data(
        "4h",
        300
    )


    htf["ema50"] = (
        htf.close
        .ewm(span=50)
        .mean()
    )


    htf["ema200"] = (
        htf.close
        .ewm(span=200)
        .mean()
    )


    bull = (
        htf.ema50.iloc[-1]
        >
        htf.ema200.iloc[-1]
    )



    last = df.iloc[-1]


    trend = (
        last.ma7 >
        last.ma14 >
        last.ma30
    )


    pullback = (
        last.low <= last.ma14
    )


    breakout = (
        last.close >
        last.ma7
    )


    if (
        bull
        and
        trend
        and
        pullback
        and
        breakout
    ):

        signal="BUY"

    else:

        signal="WAIT"



    return {

        "price":
            round(last.close,2),

        "ma7":
            round(last.ma7,2),

        "ma14":
            round(last.ma14,2),

        "ma30":
            round(last.ma30,2),

        "regime":
            "BULL"
            if bull
            else
            "BEAR",

        "signal":
            signal
    }