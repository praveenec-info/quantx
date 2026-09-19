import pandas as pd

from backtesting.strategies import (
    sma_crossover,
    ema_trend,
    momentum_strategy,
    mean_reversion
)

from backtesting.engine import run_backtest


# ==========================================
# LOAD DATA
# ==========================================

def load_asset(file_path):

    data = pd.read_csv(file_path)

    data["Date"] = pd.to_datetime(data["Date"])

    data = data.sort_values("Date")

    return data


# ==========================================
# RUN ALL STRATEGIES
# ==========================================

def test_all_strategies(data):

    strategies = {

        "SMA Crossover":
            sma_crossover(data),

        "EMA Trend":
            ema_trend(data),

        "Momentum":
            momentum_strategy(data),

        "Mean Reversion":
            mean_reversion(data)
    }

    results = []

    for name, strategy_data in strategies.items():

        backtest_data, result = run_backtest(
            strategy_data
        )

        result["Strategy"] = name

        results.append(result)

    results_df = pd.DataFrame(results)

    return results_df


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():

    assets = {

        "Gold":
            "data/processed/gold_clean.csv",

        "Bitcoin":
            "data/processed/bitcoin_clean.csv",

        "NVIDIA":
            "data/processed/nvidia_clean.csv"
    }

    all_results = []

    for asset_name, file_path in assets.items():

        print()
        print("====================================")
        print(asset_name)
        print("====================================")

        data = load_asset(file_path)

        results = test_all_strategies(data)

        results["Asset"] = asset_name

        print(results)

        all_results.append(results)

    final_results = pd.concat(
        all_results,
        ignore_index=True
    )

    final_results.to_csv(
        "backtesting/backtest_results.csv",
        index=False
    )

    print()
    print("====================================")
    print("BACKTESTING COMPLETED")
    print("====================================")

    print(final_results)


if __name__ == "__main__":
    main()