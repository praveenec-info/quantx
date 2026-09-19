import pandas as pd


def _validate_period(value, name):
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def sma_crossover(data, short_window=20, long_window=50):
    _validate_period(short_window, "fast period")
    _validate_period(long_window, "slow period")
    if short_window >= long_window:
        raise ValueError("fast period must be smaller than slow period")
    result = data.copy()
    result["Fast"] = result["Close"].rolling(short_window, min_periods=short_window).mean()
    result["Slow"] = result["Close"].rolling(long_window, min_periods=long_window).mean()
    result["Signal"] = (result["Fast"] > result["Slow"]).astype(int)
    result.loc[result[["Fast", "Slow"]].isna().any(axis=1), "Signal"] = 0
    return result


def ema_trend(data, short_window=20, long_window=50):
    _validate_period(short_window, "fast period")
    _validate_period(long_window, "slow period")
    if short_window >= long_window:
        raise ValueError("fast period must be smaller than slow period")
    result = data.copy()
    result["Fast"] = result["Close"].ewm(span=short_window, adjust=False, min_periods=short_window).mean()
    result["Slow"] = result["Close"].ewm(span=long_window, adjust=False, min_periods=long_window).mean()
    result["Signal"] = (result["Fast"] > result["Slow"]).astype(int)
    result.loc[result[["Fast", "Slow"]].isna().any(axis=1), "Signal"] = 0
    return result


def momentum(data, lookback=20):
    _validate_period(lookback, "momentum period")
    result = data.copy()
    result["Momentum"] = result["Close"].pct_change(lookback)
    result["Signal"] = (result["Momentum"] > 0).astype(int)
    result.loc[result["Momentum"].isna(), "Signal"] = 0
    return result


def mean_reversion(data, window=20, entry_zscore=-1.0, exit_zscore=0.0):
    _validate_period(window, "mean-reversion window")
    if entry_zscore >= exit_zscore:
        raise ValueError("entry z-score must be below exit z-score")
    result = data.copy()
    mean = result["Close"].rolling(window, min_periods=window).mean()
    deviation = result["Close"].rolling(window, min_periods=window).std()
    result["ZScore"] = (result["Close"] - mean) / deviation.replace(0, pd.NA)
    signal = []
    holding = 0
    for value in result["ZScore"]:
        if pd.isna(value):
            signal.append(0)
        elif holding == 0 and value <= entry_zscore:
            holding = 1
            signal.append(holding)
        elif holding == 1 and value >= exit_zscore:
            holding = 0
            signal.append(holding)
        else:
            signal.append(holding)
    result["Signal"] = signal
    return result


def sma_crossover_strategy(data, short_window=20, long_window=50):
    return sma_crossover(data, short_window, long_window)["Signal"]


def ema_trend_strategy(data, short_window=20, long_window=50):
    return ema_trend(data, short_window, long_window)["Signal"]


def momentum_strategy(data, lookback=20):
    return momentum(data, lookback)["Signal"]


def mean_reversion_strategy(data, window=20):
    return mean_reversion(data, window)["Signal"]


def generate_signals(data, strategy, fast_period=20, slow_period=50, momentum_period=20, mean_window=20, entry_zscore=-1.0):
    strategy_key = strategy.lower().replace(" ", "_")
    if strategy_key in {"sma_crossover", "sma"}:
        return sma_crossover(data, fast_period, slow_period)
    if strategy_key in {"ema_trend", "ema"}:
        return ema_trend(data, fast_period, slow_period)
    if strategy_key == "momentum":
        return momentum(data, momentum_period)
    if strategy_key in {"mean_reversion", "mean"}:
        return mean_reversion(data, mean_window, entry_zscore)
    raise ValueError(f"unsupported strategy: {strategy}")
