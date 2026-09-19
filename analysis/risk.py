import numpy as np
import pandas as pd


def calculate_daily_returns(data):
    """
    Calculate daily percentage returns.
    """
    return data["Close"].pct_change().dropna()


def calculate_historical_volatility(data):
    """
    Calculate historical daily volatility.
    """
    returns = calculate_daily_returns(data)

    return returns.std()


def calculate_annualized_volatility(data, trading_days=252):
    """
    Calculate annualized volatility.
    """
    daily_volatility = calculate_historical_volatility(data)

    return daily_volatility * np.sqrt(trading_days)


def calculate_sharpe_ratio(data, risk_free_rate=0.0, trading_days=252):
    """
    Calculate annualized Sharpe ratio.
    """
    returns = calculate_daily_returns(data)

    excess_returns = returns - (risk_free_rate / trading_days)

    if excess_returns.std() == 0:
        return 0.0

    return (
        excess_returns.mean()
        / excess_returns.std()
        * np.sqrt(trading_days)
    )


def calculate_maximum_drawdown(data):
    """
    Calculate maximum drawdown.
    """
    returns = calculate_daily_returns(data)

    cumulative_returns = (1 + returns).cumprod()

    running_max = cumulative_returns.cummax()

    drawdown = (
        cumulative_returns - running_max
    ) / running_max

    return drawdown.min()


def calculate_rolling_returns(data, window=20):
    """
    Calculate rolling returns.
    """
    return data["Close"].pct_change(periods=window)


def calculate_risk_metrics(data):
    """
    Calculate all major risk metrics.
    """
    return {
        "historical_volatility": calculate_historical_volatility(data),
        "annualized_volatility": calculate_annualized_volatility(data),
        "sharpe_ratio": calculate_sharpe_ratio(data),
        "maximum_drawdown": calculate_maximum_drawdown(data),
    }