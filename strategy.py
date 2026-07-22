import pandas as pd


def add_indicators(df, htf):

    # 1H trend

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


    # ATR

    tr = pd.concat(
        [
            df.high-df.low,
            abs(df.high-df.close.shift()),
            abs(df.low-df.close.shift())
        ],
        axis=1
    ).max(axis=1)


    df["atr"] = (
        tr
        .rolling(14)
        .mean()
    )


    # 4H regime

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


    htf["bull_regime"] = (
        htf.ema50 >
        htf.ema200
    )


    df = pd.merge_asof(
        df.sort_index(),
        htf[
            [
                "bull_regime"
            ]
        ]
        .sort_index(),
        left_index=True,
        right_index=True,
        direction="backward"
    )


    return df



def get_signal(row):


    regime = (
        row.bull_regime
    )


    trend = (
        row.ma7 >
        row.ma14 >
        row.ma30
    )


    pullback = (
        row.low <= row.ma14
    )


    trigger = (
        row.close >
        row.ma7
        and
        row.high >
        row.high_prev
    )


    if (
        regime
        and trend
        and pullback
        and trigger
    ):

        return "BUY"


    return None