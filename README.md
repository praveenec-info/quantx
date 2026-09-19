# QuantX: Multi-Asset Financial Intelligence

QuantX is a working quantitative-finance dashboard for historical analysis and rule-based backtesting of Gold, Bitcoin, and NVIDIA. It downloads historical OHLCV data with `yfinance`, normalizes it in Python, calculates indicators and risk metrics, and serves the results to the browser dashboard.

## Architecture

```text
frontend/        Browser UI, controls, SVG charts, API client
api/server.py    HTTP API and static frontend server
data/            yfinance fetch, validation, normalization, local cache
analysis/        indicators, returns, risk, regime, correlation
backtesting/     strategies, next-day execution engine, benchmark
tests/            deterministic unit and API-contract tests
```

The browser never fetches Yahoo Finance directly. It calls the Python API, which fetches and processes data before returning JSON.

## Technologies

- Python 3.11+
- pandas and NumPy for data processing
- yfinance for historical market data
- Python standard-library HTTP server
- HTML, CSS, and JavaScript for the dashboard
- pytest for tests

## Installation and startup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m api.server
```

Open `http://127.0.0.1:8000`.

The server hosts both the API and `frontend/`, so no separate frontend server is required. To use another port:

```powershell
$env:PORT=8001
python -m api.server
```

## Real market data

Supported assets and Yahoo Finance tickers:

- Gold: `GC=F`
- Bitcoin: `BTC-USD`
- NVIDIA: `NVDA`

Requests validate asset names and date ranges, reject future dates, normalize OHLCV columns, remove invalid rows, and cache valid CSV data under ignored `data/raw/` and `data/processed/` paths. Network errors, empty provider responses, and malformed data are returned as API errors instead of crashing the dashboard.

## API endpoints

- `GET /api/health`
- `GET /api/assets`
- `GET /api/historical-data?asset=nvidia&start=2024-01-01&end=2025-01-01`
- `GET /api/analysis?asset=nvidia&start=2024-01-01&end=2025-01-01`
- `GET /api/correlation?start=2024-01-01&end=2025-01-01&window=30`
- `POST /api/backtest`

Example backtest request:

```json
{
  "asset": "nvidia",
  "strategy": "sma_crossover",
  "start": "2024-01-01",
  "end": "2025-01-01",
  "fast_period": 20,
  "slow_period": 50,
  "momentum_period": 20,
  "mean_window": 20,
  "entry_zscore": -1.0,
  "initial_capital": 100000,
  "position_size": 1.0,
  "transaction_cost": 0.001
}
```

## Calculations

The analysis API returns SMA, EMA, daily returns, cumulative returns, rolling returns, historical volatility, annualized volatility, Sharpe ratio, maximum drawdown, and a transparent market-regime label.

Regime rules are descriptive, not predictive:

- Bull Market: close is at or above its rolling trend average.
- Bear Market: close is below its rolling trend average when no volatility rule applies.
- High Volatility: rolling annualized volatility is more than 1.5 times its expanding median.
- Low Volatility: rolling annualized volatility is less than 0.75 times its expanding median.

Correlation uses aligned dates and Pearson correlation of daily returns for Gold, Bitcoin, and NVIDIA. Rolling pair correlations are also calculated by the API.

## Backtesting

Available strategies:

- SMA Crossover
- EMA Trend
- Momentum
- Mean Reversion

The engine supports fast/slow periods, momentum period, mean-reversion window and entry z-score, position size, initial capital, transaction costs, and date range. It returns entry prices, exit prices, signals, portfolio value, strategy metrics, and a buy-and-hold benchmark.

Assumptions:

- Signals are generated using information available at the close of day `t`.
- Positions execute on day `t+1`, avoiding look-ahead bias.
- Returns use close-to-close percentage changes.
- Transaction cost is applied to position changes.
- Position size is a long-only fraction from 0 to 1.
- This is historical research software, not financial advice or a prediction system.

## Testing

Run the complete deterministic suite:

```powershell
python -m pytest
```

The tests cover data normalization and failure handling, all indicators and risk metrics, date-aligned correlation, all strategy signal generators, next-day execution, transaction costs, portfolio values, API payloads, and invalid inputs. Provider calls are mocked in unit tests; the running application uses real `yfinance` calls.
