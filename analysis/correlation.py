import pandas as pd


def calculate_correlation(data):
    """
    Calculate correlation matrix between assets.

    Expected input:
    DataFrame where each column represents
    an asset's closing price.
    """
    returns = data.pct_change()

    return returns.corr()


def calculate_rolling_correlation(
    data1,
    data2,
    window=30
):
    """
    Calculate rolling correlation between two assets.
    """
    returns1 = data1["Close"].pct_change()
    returns2 = data2["Close"].pct_change()

    return returns1.rolling(window).corr(returns2)