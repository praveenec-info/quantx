import pandas as pd


def calculate_daily_returns(data):
    return data["Close"].pct_change()


def calculate_cumulative_returns(data):
    return (1 + calculate_daily_returns(data).fillna(0)).cumprod() - 1


def calculate_rolling_returns(data, window=20):
    if not isinstance(window, int) or window <= 0:
        raise ValueError("window must be a positive integer")
    return data["Close"].pct_change(periods=window)


def add_return_columns(data, rolling_window=20):
    result = data.copy()
    result["Daily_Return"] = calculate_daily_returns(result)
    result["Cumulative_Return"] = calculate_cumulative_returns(result)
    result["Rolling_Return"] = calculate_rolling_returns(result, rolling_window)
    return result
