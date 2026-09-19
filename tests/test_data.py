import pandas as pd
import pytest

from data.data_loader import DataFetchError, fetch_market_data, normalize_market_data, validate_date_range


def provider_frame():
    return pd.DataFrame({
        "Open": [100, 101],
        "High": [102, 103],
        "Low": [99, 100],
        "Close": [101, 102],
        "Volume": [1000, 1100],
    }, index=pd.to_datetime(["2024-01-02", "2024-01-03"]))


def test_normalize_market_data_has_ohlcv():
    result = normalize_market_data(provider_frame())
    assert list(result.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert len(result) == 2


def test_fetch_market_data_uses_provider(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("data.data_loader.yf.download", lambda *args, **kwargs: provider_frame())

    result = fetch_market_data("nvidia", "2024-01-01", "2024-01-05", use_cache=False)

    assert result["Close"].tolist() == [101, 102]
    assert (tmp_path / "data" / "processed" / "nvidia_cleaned.csv").exists()


def test_invalid_dates_are_rejected():
    with pytest.raises(ValueError, match="before"):
        fetch_market_data("nvidia", "2024-02-01", "2024-01-01", use_cache=False)


def test_local_current_date_is_valid():
    today = pd.Timestamp.now().strftime("%Y-%m-%d")

    start_date, end_date = validate_date_range(today, today)

    assert start_date == end_date


def test_empty_provider_data_is_rejected(monkeypatch):
    monkeypatch.setattr("data.data_loader.yf.download", lambda *args, **kwargs: pd.DataFrame())
    with pytest.raises(DataFetchError, match="no rows"):
        fetch_market_data("gold", "2024-01-01", "2024-01-05", use_cache=False)
