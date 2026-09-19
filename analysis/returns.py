import pandas as pd


def calculate_daily_returns(data):
    """
    Calculate daily percentage returns.
    """
    return data["Close"].pct_change()


def calculate_cumulative_returns(data):
    """
    Calculate cumulative returns.
    """
    daily_returns = calculate_daily_returns(data)

    return (1 + daily_returns).cumprod() - 1


def add_return_columns(data):
    """
    Add daily and cumulative return columns.
    """
    data = data.copy()

    data["Daily_Return"] = calculate_daily_returns(data)
    data["Cumulative_Return"] = calculate_cumulative_returns(data)

    return data