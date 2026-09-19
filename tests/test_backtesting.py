import pandas as pd
import pytest

from backtesting.strategies import (
    sma_crossover_strategy,
    ema_trend_strategy,
    momentum_strategy,
    mean_reversion_strategy,
)
from backtesting.engine import run_backtest
from backtesting.strategies import generate_signals


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


def test_backtest_uses_next_day_signal_and_calculates_portfolio():
    data = create_sample_data()
    data["Date"] = pd.date_range("2024-01-01", periods=len(data))
    data["Signal"] = 1

    series, metrics = run_backtest(data, initial_capital=1000, transaction_cost=0.01)

    assert series.loc[0, "Position"] == 0
    assert series["Equity"].iloc[-1] > 0
    assert metrics["strategy"]["number_of_trades"] == 1
    assert metrics["strategy"]["final_value"] < metrics["benchmark"]["final_value"]


def test_backtest_rejects_invalid_capital():
    data = create_sample_data()
    data["Date"] = pd.date_range("2024-01-01", periods=len(data))
    data["Signal"] = 1

    with pytest.raises(ValueError, match="capital"):
        run_backtest(data, initial_capital=0)


@pytest.mark.parametrize("strategy", ["sma_crossover", "ema_trend", "momentum", "mean_reversion"])
def test_each_strategy_runs_through_engine(strategy):
    data = create_sample_data()
    data["Date"] = pd.date_range("2024-01-01", periods=len(data))
    signals = generate_signals(data, strategy, fast_period=3, slow_period=5, momentum_period=3, mean_window=3)

    series, metrics = run_backtest(signals, initial_capital=1000)

    assert len(series) == len(data)
    assert metrics["strategy"]["final_value"] > 0
    