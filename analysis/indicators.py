import pandas as pd


def calculate_sma(data, period=20):
    """
    Calculate Simple Moving Average.
    """
    return data["Close"].rolling(window=period).mean()


def calculate_ema(data, period=20):
    """
    Calculate Exponential Moving Average.
    """
    return data["Close"].ewm(span=period, adjust=False).mean()


def add_moving_averages(data, sma_period=20, ema_period=20):
    """
    Add SMA and EMA columns to the dataframe.
    """
    data = data.copy()

    data["SMA"] = calculate_sma(data, sma_period)
    data["EMA"] = calculate_ema(data, ema_period)

    return data