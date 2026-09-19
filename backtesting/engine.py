import numpy as np
import pandas as pd


def _performance_metrics(returns, equity, number_of_trades):
    clean_returns = returns.replace([np.inf, -np.inf], np.nan).fillna(0)
    volatility = float(clean_returns.std() * np.sqrt(252))
    sharpe = float(clean_returns.mean() / clean_returns.std() * np.sqrt(252)) if clean_returns.std() else 0.0
    drawdown = equity / equity.cummax() - 1
    return {
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1),
        "final_value": float(equity.iloc[-1]),
        "volatility": volatility,
        "sharpe_ratio": sharpe,
        "maximum_drawdown": float(drawdown.min()),
        "number_of_trades": int(number_of_trades),
    }


def run_backtest(data, initial_capital=100000.0, position_size=1.0, transaction_cost=0.001):
    if initial_capital <= 0:
        raise ValueError("initial capital must be positive")
    if not 0 < position_size <= 1:
        raise ValueError("position size must be greater than 0 and at most 1")
    if transaction_cost < 0:
        raise ValueError("transaction cost cannot be negative")
    required = {"Date", "Close", "Signal"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"backtest data is missing columns: {', '.join(sorted(missing))}")
    result = data.sort_values("Date").drop_duplicates("Date").reset_index(drop=True).copy()
    result["Signal"] = result["Signal"].fillna(0).clip(0, 1)
    result["Position"] = result["Signal"].shift(1).fillna(0) * position_size
    result["Market_Return"] = result["Close"].pct_change().fillna(0)
    result["Position_Change"] = result["Position"].diff().fillna(result["Position"]).abs()
    result["Transaction_Cost"] = result["Position_Change"] * transaction_cost
    result["Strategy_Return"] = result["Position"] * result["Market_Return"] - result["Transaction_Cost"]
    result["Equity"] = initial_capital * (1 + result["Strategy_Return"]).cumprod()
    result["Benchmark_Return"] = result["Market_Return"]
    result["Benchmark_Equity"] = initial_capital * (1 + result["Benchmark_Return"]).cumprod()
    result["Trade"] = result["Position_Change"] > 0
    result["Entry_Price"] = result["Close"].where((result["Position"] > 0) & (result["Position"].shift(1).fillna(0) == 0))
    result["Exit_Price"] = result["Close"].where((result["Position"] == 0) & (result["Position"].shift(1).fillna(0) > 0))
    strategy_metrics = _performance_metrics(result["Strategy_Return"], result["Equity"], result["Trade"].sum())
    benchmark_metrics = _performance_metrics(result["Benchmark_Return"], result["Benchmark_Equity"], 1)
    return result, {"strategy": strategy_metrics, "benchmark": benchmark_metrics}
