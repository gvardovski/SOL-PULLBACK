import ccxt
import pandas as pd


exchange = ccxt.binance()


SYMBOL = "SOL/USDT"


def load_market():

    candles = exchange.fetch_ohlcv(
        SYMBOL,
        timeframe="1h",
        limit=100
    )


    df = pd.DataFrame(
        candles,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )


    return df



def calculate_trade(
    capital=10000,
    risk_percent=1,
    atr_multiplier=1.0,
    reward_ratio=4
):


    df = load_market()


    price = df.close.iloc[-1]


    # ATR calculation

    tr = pd.concat(
        [
            df.high - df.low,

            abs(
                df.high -
                df.close.shift()
            ),

            abs(
                df.low -
                df.close.shift()
            )

        ],
        axis=1
    ).max(axis=1)


    atr = tr.rolling(14).mean().iloc[-1]



    risk_money = (
        capital *
        risk_percent /
        100
    )


    stop_distance = (
        atr *
        atr_multiplier
    )


    quantity = (
        risk_money /
        stop_distance
    )


    position_value = (
        quantity *
        price
    )


    stop = (
        price -
        stop_distance
    )


    target = (
        price +
        stop_distance *
        reward_ratio
    )


    profit = (
        target-price
    )*quantity


    loss = (
        price-stop
    )*quantity



    return {

        "price":round(price,2),

        "atr":round(atr,3),

        "quantity":round(quantity,3),

        "position":
            round(position_value,2),

        "risk":
            round(loss,2),

        "stop":
            round(stop,2),

        "target":
            round(target,2),

        "profit":
            round(profit,2),

        "rr":
            reward_ratio

    }