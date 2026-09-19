from backtesting.engine import run_backtest


def buy_and_hold(data, initial_capital=100000.0):
    prepared = data.copy()
    prepared["Signal"] = 1
    series, metrics = run_backtest(
        prepared,
        initial_capital=initial_capital,
        position_size=1.0,
        transaction_cost=0.0,
    )
    return series.rename(columns={"Equity": "Benchmark_Equity"}), metrics["benchmark"]
