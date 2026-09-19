import pandas as pd

from backtesting.strategies import (
    sma_crossover_strategy,
    ema_trend_strategy,
    momentum_strategy,
    mean_reversion_strategy,
)


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
                116,
                120,
                122,
                119,
                125,
            ]
        }
    )


def test_sma_crossover_strategy():
    data = create_sample_data()

    result = sma_crossover_strategy(data)

    assert isinstance(result, pd.Series)
    assert len(result) == len(data)


def test_ema_trend_strategy():
    data = create_sample_data()

    result = ema_trend_strategy(data)

    assert isinstance(result, pd.Series)
    assert len(result) == len(data)


def test_momentum_strategy():
    data = create_sample_data()

    result = momentum_strategy(data)

    assert isinstance(result, pd.Series)
    assert len(result) == len(data)


def test_mean_reversion_strategy():
    data = create_sample_data()

    result = mean_reversion_strategy(data)

    assert isinstance(result, pd.Series)
    assert len(result) == len(data)
    