import pandas as pd


def align_close_prices(asset_data):
    frames = []
    for asset, data in asset_data.items():
        frame = data[["Date", "Close"]].copy()
        frame["Date"] = pd.to_datetime(frame["Date"])
        frame = frame.rename(columns={"Close": asset})
        frames.append(frame.set_index("Date"))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1, join="inner").dropna().sort_index()


def calculate_correlation(asset_data):
    prices = align_close_prices(asset_data)
    if prices.empty:
        return pd.DataFrame()
    return prices.pct_change().dropna().corr()


def calculate_rolling_correlation(data1, data2, window=30):
    if window <= 0:
        raise ValueError("window must be positive")
    left = data1[["Date", "Close"]].rename(columns={"Close": "left"}).set_index("Date")
    right = data2[["Date", "Close"]].rename(columns={"Close": "right"}).set_index("Date")
    aligned = pd.concat([left.pct_change(), right.pct_change()], axis=1, join="inner").dropna()
    return aligned["left"].rolling(window).corr(aligned["right"])
