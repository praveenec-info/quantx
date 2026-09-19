import pandas as pd


# ==========================================
# SMA CROSSOVER STRATEGY
# ==========================================

def sma_crossover(data, short_window=20, long_window=50):

    data = data.copy()

    data["SMA_Short"] = (
        data["Close"]
        .rolling(window=short_window)
        .mean()
    )

    data["SMA_Long"] = (
        data["Close"]
        .rolling(window=long_window)
        .mean()
    )

    data["Signal"] = 0

    data.loc[
        data["SMA_Short"] > data["SMA_Long"],
        "Signal"
    ] = 1

    return data


# ==========================================
# EMA TREND STRATEGY
# ==========================================

def ema_trend(data, short_window=20, long_window=50):

    data = data.copy()

    data["EMA_Short"] = (
        data["Close"]
        .ewm(span=short_window, adjust=False)
        .mean()
    )

    data["EMA_Long"] = (
        data["Close"]
        .ewm(span=long_window, adjust=False)
        .mean()
    )

    data["Signal"] = 0

    data.loc[
        data["EMA_Short"] > data["EMA_Long"],
        "Signal"
    ] = 1

    return data


# ==========================================
# MOMENTUM STRATEGY
# ==========================================

def momentum_strategy(data, lookback=20):

    data = data.copy()

    data["Momentum"] = (
        data["Close"].pct_change(lookback)
    )

    data["Signal"] = 0

    data.loc[
        data["Momentum"] > 0,
        "Signal"
    ] = 1

    return data


# ==========================================
# MEAN REVERSION STRATEGY
# ==========================================

def mean_reversion(data, window=20):

    data = data.copy()

    data["Mean"] = (
        data["Close"]
        .rolling(window=window)
        .mean()
    )

    data["Signal"] = 0

    # Buy when price is below its moving average
    data.loc[
        data["Close"] < data["Mean"],
        "Signal"
    ] = 1

    return data