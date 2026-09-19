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


def sma_crossover_strategy(data, short_window=20, long_window=50):
    result = sma_crossover(data, short_window, long_window)
    return result["Signal"]


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


def ema_trend_strategy(data, short_window=20, long_window=50):
    result = ema_trend(data, short_window, long_window)
    return result["Signal"]


# ==========================================
# MOMENTUM STRATEGY
# ==========================================

def momentum(data, lookback=20):

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


def momentum_strategy(data, lookback=20):
    result = momentum(data, lookback)
    return result["Signal"]


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

    data.loc[
        data["Close"] < data["Mean"],
        "Signal"
    ] = 1

    return data


def mean_reversion_strategy(data, window=20):
    result = mean_reversion(data, window)
    return result["Signal"]