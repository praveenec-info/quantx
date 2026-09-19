import os

import pandas as pd
import yfinance as yf


RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
SUPPORTED_ASSETS = {
    "gold": {"name": "Gold", "ticker": "GC=F"},
    "bitcoin": {"name": "Bitcoin", "ticker": "BTC-USD"},
    "nvidia": {"name": "NVIDIA", "ticker": "NVDA"},
}
REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


class DataFetchError(RuntimeError):
    """Raised when market data cannot be downloaded or normalized."""


def validate_date_range(start=None, end=None):
    # The browser sends local calendar dates. Compare against the same local
    # calendar day instead of UTC, which can still be on the previous date.
    today = pd.Timestamp.now().normalize()
    start_date = pd.Timestamp(start).normalize() if start else today - pd.DateOffset(years=5)
    end_date = pd.Timestamp(end).normalize() if end else today
    if start_date > end_date:
        raise ValueError("start date must be before or equal to end date")
    if end_date > today:
        raise ValueError("end date cannot be in the future")
    return start_date, end_date


def normalize_market_data(raw_data):
    if raw_data is None or raw_data.empty:
        raise DataFetchError("The data provider returned no rows")
    data = raw_data.copy()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [column[0] for column in data.columns]
    data = data.reset_index()
    if "Date" not in data.columns and "index" in data.columns:
        data = data.rename(columns={"index": "Date"})
    if "Close" not in data.columns and "Adj Close" in data.columns:
        data = data.rename(columns={"Adj Close": "Close"})
    elif "Adj Close" in data.columns:
        data = data.drop(columns=["Adj Close"])
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise DataFetchError(f"Downloaded data is missing columns: {', '.join(missing)}")
    data = data[REQUIRED_COLUMNS]
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce", utc=True).dt.tz_localize(None)
    for column in REQUIRED_COLUMNS[1:]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["Date", "Close"]).drop_duplicates("Date")
    data = data.sort_values("Date").reset_index(drop=True)
    if data.empty:
        raise DataFetchError("No valid market rows remained after normalization")
    return data


def fetch_market_data(asset, start=None, end=None, use_cache=True):
    asset_key = asset.lower()
    if asset_key not in SUPPORTED_ASSETS:
        raise ValueError(f"unsupported asset: {asset}")
    start_date, end_date = validate_date_range(start, end)
    filename = f"{asset_key}.csv"
    processed_path = os.path.join(PROCESSED_DIR, filename.replace(".csv", "_cleaned.csv"))
    if use_cache and os.path.exists(processed_path):
        cached = normalize_market_data(pd.read_csv(processed_path))
        filtered = cached[(cached["Date"] >= start_date) & (cached["Date"] <= end_date)]
        if not filtered.empty and cached["Date"].min() <= start_date:
            return filtered.reset_index(drop=True)
    try:
        raw = yf.download(
            SUPPORTED_ASSETS[asset_key]["ticker"],
            start=start_date.strftime("%Y-%m-%d"),
            end=(end_date + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            auto_adjust=False,
            progress=False,
            threads=False,
        )
    except Exception as exc:
        raise DataFetchError(f"market-data request failed: {exc}") from exc
    data = normalize_market_data(raw)
    data = data[(data["Date"] >= start_date) & (data["Date"] <= end_date)].reset_index(drop=True)
    if data.empty:
        raise DataFetchError("No market data exists for the requested date range")
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    data.to_csv(os.path.join(RAW_DIR, filename), index=False)
    data.to_csv(processed_path, index=False)
    return data


def load_data(filename="nvidia.csv"):
    asset = os.path.splitext(filename)[0].lower()
    if asset not in SUPPORTED_ASSETS:
        asset = "nvidia"
    return {SUPPORTED_ASSETS[asset]["ticker"]: fetch_market_data(asset)}


if __name__ == "__main__":
    for asset_name in SUPPORTED_ASSETS:
        fetch_market_data(asset_name)
