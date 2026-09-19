import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def get_stock_data(symbol, filename):

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"Error getting {symbol} data:")
        print(data)
        return

    records = []

    for date, values in data["Time Series (Daily)"].items():

        records.append({
            "Date": date,
            "Open": values["1. open"],
            "High": values["2. high"],
            "Low": values["3. low"],
            "Close": values["4. close"],
            "Volume": values["5. volume"]
        })

    df = pd.DataFrame(records)

    df["Date"] = pd.to_datetime(df["Date"])

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna()
    df = df.drop_duplicates()
    df = df.sort_values("Date")
    df = df.reset_index(drop=True)

    raw_path = os.path.join(RAW_DIR, filename)
    processed_path = os.path.join(
        PROCESSED_DIR,
        filename.replace(".csv", "_cleaned.csv")
    )

    df.to_csv(raw_path, index=False)
    df.to_csv(processed_path, index=False)

    print(f"{filename} saved successfully")
    print(f"Rows: {len(df)}")


# NVIDIA
get_stock_data("NVDA", "nvidia.csv")
