import pandas as pd

from data.data_loader import load_data


def test_data_is_loaded():
    data = load_data()

    assert isinstance(data, dict)
    assert len(data) > 0


def test_required_columns_exist():
    data = load_data()

    required_columns = ["Close"]

    for asset, df in data.items():
        for column in required_columns:
            assert column in df.columns, f"{column} missing in {asset}"