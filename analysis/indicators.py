import pandas as pd


def _validate_period(period):
    if not isinstance(period, int) or period <= 0:
        raise ValueError("period must be a positive integer")


def calculate_sma(data, period=20):
    _validate_period(period)
    return data["Close"].rolling(window=period, min_periods=period).mean()


def calculate_ema(data, period=20):
    _validate_period(period)
    return data["Close"].ewm(span=period, adjust=False, min_periods=period).mean()


def add_moving_averages(data, sma_period=20, ema_period=20):
    result = data.copy()
    result["SMA"] = calculate_sma(result, sma_period)
    result["EMA"] = calculate_ema(result, ema_period)
    return result
