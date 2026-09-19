import pandas as pd


def buy_and_hold(data, initial_capital=100000):

    data = data.copy()

    # Make sure dates are sorted
    data = data.sort_values("Date").reset_index(drop=True)

    # Calculate daily return
    data["Daily_Return"] = data["Close"].pct_change()

    # First day has no previous price
    data["Daily_Return"] = data["Daily_Return"].fillna(0)

    # Calculate Buy & Hold portfolio value
    data["Benchmark_Equity"] = (
        initial_capital
        * (1 + data["Daily_Return"]).cumprod()
    )

    # Final portfolio value
    final_value = data["Benchmark_Equity"].iloc[-1]

    # Total return
    total_return = (
        final_value / initial_capital
    ) - 1

    # Maximum drawdown
    running_max = data["Benchmark_Equity"].cummax()

    drawdown = (
        data["Benchmark_Equity"] / running_max
    ) - 1

    maximum_drawdown = drawdown.min()

    results = {
        "Initial Capital": initial_capital,
        "Final Value": final_value,
        "Total Return": total_return,
        "Maximum Drawdown": maximum_drawdown
    }

    return data, results


def compare_with_strategy(
    strategy_data,
    benchmark_data
):

    comparison = pd.DataFrame({

        "Date": strategy_data["Date"],

        "Strategy Equity":
            strategy_data["Equity"],

        "Buy & Hold Equity":
            benchmark_data["Benchmark_Equity"]
    })

    return comparison