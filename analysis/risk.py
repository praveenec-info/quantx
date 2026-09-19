import numpy as np

from analysis.returns import calculate_daily_returns


def calculate_historical_volatility(data):
    return float(calculate_daily_returns(data).dropna().std())


def calculate_annualized_volatility(data, trading_days=252):
    return calculate_historical_volatility(data) * np.sqrt(trading_days)


def calculate_sharpe_ratio(data, risk_free_rate=0.0, trading_days=252):
    returns = calculate_daily_returns(data).dropna()
    if returns.empty or returns.std() == 0:
        return 0.0
    excess_returns = returns - risk_free_rate / trading_days
    return float(excess_returns.mean() / excess_returns.std() * np.sqrt(trading_days))


def calculate_maximum_drawdown(data):
    close = data["Close"].dropna()
    if close.empty:
        return 0.0
    drawdown = close / close.cummax() - 1
    return float(drawdown.min())


def calculate_risk_metrics(data, risk_free_rate=0.0):
    return {
        "historical_volatility": calculate_historical_volatility(data),
        "annualized_volatility": calculate_annualized_volatility(data),
        "sharpe_ratio": calculate_sharpe_ratio(data, risk_free_rate),
        "maximum_drawdown": calculate_maximum_drawdown(data),
    }


def classify_market_regime(data, trend_window=50, volatility_window=20):
    if trend_window <= 0 or volatility_window <= 0:
        raise ValueError("regime windows must be positive")
    result = data.copy()
    returns = result["Close"].pct_change()
    trend = result["Close"].rolling(trend_window, min_periods=1).mean()
    volatility = returns.rolling(volatility_window, min_periods=2).std() * np.sqrt(252)
    baseline = volatility.expanding(min_periods=2).median()
    regimes = []
    for close, trend_value, volatility_value, baseline_value in zip(result["Close"], trend, volatility, baseline):
        if pd_is_valid(volatility_value) and pd_is_valid(baseline_value) and volatility_value > baseline_value * 1.5:
            regimes.append("High Volatility")
        elif close >= trend_value:
            regimes.append("Bull Market")
        elif pd_is_valid(volatility_value) and pd_is_valid(baseline_value) and volatility_value < baseline_value * 0.75:
            regimes.append("Low Volatility")
        else:
            regimes.append("Bear Market")
    result["Regime"] = regimes
    return result


def pd_is_valid(value):
    return value == value and np.isfinite(value)
