import pandas as pd

from analysis.indicators import calculate_sma, calculate_ema
from analysis.returns import (
    calculate_daily_returns,
    calculate_cumulative_returns,
)
from analysis.risk import (
    calculate_historical_volatility,
    calculate_annualized_volatility,
    calculate_sharpe_ratio,
    calculate_maximum_drawdown,
)
from analysis.correlation import calculate_correlation


def create_sample_data():
    return pd.DataFrame(
        {
            "Close": [
                100,
                102,
                101,
                105,
                108,
                110,
                107,
                112,
                115,
                118,
            ]
        }
    )


def test_sma():
    data = create_sample_data()

    result = calculate_sma(data, period=3)

    assert len(result) == len(data)
    assert result.iloc[2] == (100 + 102 + 101) / 3


def test_ema():
    data = create_sample_data()

    result = calculate_ema(data, period=3)

    assert len(result) == len(data)
    assert result.notna().any()


def test_daily_returns():
    data = create_sample_data()

    result = calculate_daily_returns(data)

    assert len(result) == len(data)
    assert pd.isna(result.iloc[0])


def test_cumulative_returns():
    data = create_sample_data()

    result = calculate_cumulative_returns(data)

    assert len(result) == len(data)


def test_historical_volatility():
    data = create_sample_data()

    result = calculate_historical_volatility(data)

    assert result >= 0


def test_annualized_volatility():
    data = create_sample_data()

    result = calculate_annualized_volatility(data)

    assert result >= 0


def test_sharpe_ratio():
    data = create_sample_data()

    result = calculate_sharpe_ratio(data)

    assert isinstance(result, float)


def test_maximum_drawdown():
    data = create_sample_data()

    result = calculate_maximum_drawdown(data)

    assert result <= 0


def test_correlation_aligns_assets_by_date():
    first = pd.DataFrame({"Date": pd.date_range("2024-01-01", periods=4), "Close": [1, 2, 3, 4]})
    second = pd.DataFrame({"Date": pd.date_range("2024-01-02", periods=4), "Close": [2, 3, 4, 5]})

    result = calculate_correlation({"first": first, "second": second})

    assert list(result.columns) == ["first", "second"]
    assert result.loc["first", "second"] == 1.0
