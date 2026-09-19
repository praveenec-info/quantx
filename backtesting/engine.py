import pandas as pd
import numpy as np


def run_backtest(
    data,
    initial_capital=100000,
    transaction_cost=0.001
):

    data = data.copy()

    # Make sure data is sorted
    data = data.sort_values("Date").reset_index(drop=True)

    # Daily market return
    data["Market_Return"] = data["Close"].pct_change()

    # Use previous day's signal
    # This avoids look-ahead bias
    data["Position"] = data["Signal"].shift(1)

    data["Position"] = data["Position"].fillna(0)

    # Detect trades
    data["Trade"] = (
        data["Position"]
        .diff()
        .abs()
        .fillna(0)
    )

    # Transaction cost
    data["Transaction_Cost"] = (
        data["Trade"] * transaction_cost
    )

    # Strategy return
    data["Strategy_Return"] = (
        data["Position"] * data["Market_Return"]
        - data["Transaction_Cost"]
    )

    data["Strategy_Return"] = (
        data["Strategy_Return"].fillna(0)
    )

    # Portfolio value
    data["Equity"] = (
        initial_capital
        * (1 + data["Strategy_Return"]).cumprod()
    )

    # Buy and hold
    data["Buy_Hold_Return"] = (
        data["Market_Return"].fillna(0)
    )

    data["Buy_Hold_Equity"] = (
        initial_capital
        * (1 + data["Buy_Hold_Return"]).cumprod()
    )

    # Number of trades
    number_of_trades = int(
        data["Trade"].sum()
    )

    # Final values
    final_strategy_value = data["Equity"].iloc[-1]

    final_buy_hold_value = (
        data["Buy_Hold_Equity"].iloc[-1]
    )

    # Total returns
    strategy_return = (
        final_strategy_value / initial_capital - 1
    )

    buy_hold_return = (
        final_buy_hold_value / initial_capital - 1
    )

    # Maximum drawdown
    running_max = data["Equity"].cummax()

    drawdown = (
        data["Equity"] / running_max - 1
    )

    max_drawdown = drawdown.min()

    results = {
        "Initial Capital": initial_capital,
        "Final Strategy Value": final_strategy_value,
        "Strategy Return": strategy_return,
        "Buy & Hold Value": final_buy_hold_value,
        "Buy & Hold Return": buy_hold_return,
        "Number of Trades": number_of_trades,
        "Maximum Drawdown": max_drawdown
    }

    return data, results