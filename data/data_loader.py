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

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Error getting {symbol} data: {e}")
        return None

    if "Time Series (Daily)" not in data:
        print(f"Error getting {symbol} data:")
        print(data)
        return None

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

    raw_path = os.path.join(
        RAW_DIR,
        filename
    )

    processed_path = os.path.join(
        PROCESSED_DIR,
        filename.replace(
            ".csv",
            "_cleaned.csv"
        )
    )

    df.to_csv(raw_path, index=False)
    df.to_csv(processed_path, index=False)

    print(f"{filename} saved successfully")
    print(f"Rows: {len(df)}")

    return df


def load_data(filename="nvidia.csv"):
    """
    Load stock data and return it as a dictionary.
    """

    processed_filename = filename.replace(
        ".csv",
        "_cleaned.csv"
    )

    processed_path = os.path.join(
        PROCESSED_DIR,
        processed_filename
    )

    # If processed data exists
    if os.path.exists(processed_path):

        df = pd.read_csv(processed_path)

        return {
            "NVDA": df
        }

    # If raw data exists
    raw_path = os.path.join(
        RAW_DIR,
        filename
    )

    if os.path.exists(raw_path):

        df = pd.read_csv(raw_path)

        return {
            "NVDA": df
        }

    # Sample data for testing
    sample_data = pd.DataFrame({

        "Date": pd.date_range(
            start="2025-01-01",
            periods=10,
            freq="D"
        ),

        "Open": [
            100, 101, 102, 103, 104,
            105, 106, 107, 108, 109
        ],

        "High": [
            102, 103, 104, 105, 106,
            107, 108, 109, 110, 111
        ],

        "Low": [
            99, 100, 101, 102, 103,
            104, 105, 106, 107, 108
        ],

        "Close": [
            101, 102, 103, 104, 105,
            106, 107, 108, 109, 110
        ],

        "Volume": [
            1000, 1100, 1200, 1300, 1400,
            1500, 1600, 1700, 1800, 1900
        ]
    })

    return {
        "NVDA": sample_data
    }


# NVIDIA data download
get_stock_data("NVDA", "nvidia.csv")