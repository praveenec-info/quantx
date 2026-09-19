import pandas as pd
import pytest

from api.server import _asset_payload, _backtest_payload


@pytest.fixture
def market_data():
    dates = pd.date_range("2024-01-01", periods=80, freq="D")
    close = [100 + index + (index % 5) for index in range(80)]
    return pd.DataFrame({
        "Date": dates,
        "Open": close,
        "High": [value + 1 for value in close],
        "Low": [value - 1 for value in close],
        "Close": close,
        "Volume": [1000] * 80,
    })


def test_asset_payload_contains_real_analysis(monkeypatch, market_data):
    monkeypatch.setattr("api.server.fetch_market_data", lambda *args, **kwargs: market_data.copy())

    payload = _asset_payload("nvidia", "2024-01-01", "2024-03-20")

    assert payload["records"]
    assert "annualized_volatility" in payload["metrics"]
    assert "Regime" in payload["records"][0]
    assert payload["metrics"]["price"] == market_data["Close"].iloc[-1]


def test_backtest_payload_uses_requested_parameters(monkeypatch, market_data):
    monkeypatch.setattr("api.server.fetch_market_data", lambda *args, **kwargs: market_data.copy())

    payload = _backtest_payload({
        "asset": "nvidia",
        "strategy": "momentum",
        "momentum_period": 3,
        "initial_capital": 10000,
        "transaction_cost": 0.01,
    })

    assert payload["metrics"]["strategy"]["final_value"] > 0
    assert "Benchmark_Equity" in payload["records"][0]


def test_invalid_strategy_parameters_are_rejected(monkeypatch, market_data):
    monkeypatch.setattr("api.server.fetch_market_data", lambda *args, **kwargs: market_data.copy())

    with pytest.raises(ValueError, match="smaller"):
        _backtest_payload({"asset": "nvidia", "strategy": "sma_crossover", "fast_period": 50, "slow_period": 20})
