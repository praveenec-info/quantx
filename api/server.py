import json
import math
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd

from analysis.correlation import calculate_correlation, calculate_rolling_correlation
from analysis.indicators import add_moving_averages
from analysis.returns import add_return_columns
from analysis.risk import classify_market_regime, calculate_risk_metrics
from backtesting.engine import run_backtest
from backtesting.strategies import generate_signals
from data.data_loader import DataFetchError, SUPPORTED_ASSETS, fetch_market_data, validate_date_range


ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"


def _json_value(value):
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return None
    if hasattr(value, "item"):
        return _json_value(value.item())
    return value


def _records(data):
    frame = data.copy()
    if "Date" in frame:
        frame["Date"] = pd.to_datetime(frame["Date"]).dt.strftime("%Y-%m-%d")
    return [{key: _json_value(value) for key, value in row.items()} for row in frame.to_dict(orient="records")]


def _asset_payload(asset, start, end):
    data = fetch_market_data(asset, start, end)
    enriched = add_return_columns(add_moving_averages(data))
    enriched = classify_market_regime(enriched)
    metrics = calculate_risk_metrics(enriched)
    latest = enriched.iloc[-1]
    metrics.update({
        "price": float(latest["Close"]),
        "daily_return": _json_value(latest["Daily_Return"]),
        "cumulative_return": _json_value(latest["Cumulative_Return"]),
        "rolling_return": _json_value(latest["Rolling_Return"]),
        "regime": str(latest["Regime"]),
    })
    return {
        "asset": asset,
        "name": SUPPORTED_ASSETS[asset]["name"],
        "ticker": SUPPORTED_ASSETS[asset]["ticker"],
        "start": str(enriched["Date"].min().date()),
        "end": str(enriched["Date"].max().date()),
        "metrics": metrics,
        "records": _records(enriched),
    }


def _backtest_payload(request):
    asset = str(request.get("asset", "nvidia")).lower()
    strategy = str(request.get("strategy", "sma_crossover"))
    start = request.get("start")
    end = request.get("end")
    data = fetch_market_data(asset, start, end)
    signal_data = generate_signals(
        data,
        strategy,
        fast_period=int(request.get("fast_period", 20)),
        slow_period=int(request.get("slow_period", 50)),
        momentum_period=int(request.get("momentum_period", 20)),
        mean_window=int(request.get("mean_window", 20)),
        entry_zscore=float(request.get("entry_zscore", -1.0)),
    )
    series, metrics = run_backtest(
        signal_data,
        initial_capital=float(request.get("initial_capital", 100000)),
        position_size=float(request.get("position_size", 1.0)),
        transaction_cost=float(request.get("transaction_cost", 0.001)),
    )
    return {
        "asset": asset,
        "strategy": strategy,
        "metrics": metrics,
        "records": _records(series[["Date", "Close", "Signal", "Position", "Equity", "Benchmark_Equity", "Entry_Price", "Exit_Price"]]),
    }


def _correlation_payload(start, end, window=30):
    assets = {asset: fetch_market_data(asset, start, end) for asset in SUPPORTED_ASSETS}
    matrix = calculate_correlation(assets)
    rolling = {}
    names = list(assets)
    for index, left_name in enumerate(names):
        for right_name in names[index + 1:]:
            values = calculate_rolling_correlation(assets[left_name], assets[right_name], window)
            rolling[f"{left_name}_{right_name}"] = _records(pd.DataFrame({"Date": values.index, "Correlation": values.values}))
    return {"matrix": {row: {column: _json_value(matrix.loc[row, column]) for column in matrix.columns} for row in matrix.index}, "rolling": rolling}


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        try:
            if parsed.path == "/api/health":
                self._json({"status": "ok"})
            elif parsed.path == "/api/assets":
                self._json({"assets": [{"id": key, **value} for key, value in SUPPORTED_ASSETS.items()]})
            elif parsed.path in {"/api/historical-data", "/api/analysis"}:
                asset = params.get("asset", ["nvidia"])[0].lower()
                start = params.get("start", [None])[0]
                end = params.get("end", [None])[0]
                validate_date_range(start, end)
                payload = _asset_payload(asset, start, end)
                if parsed.path == "/api/historical-data":
                    payload = {key: payload[key] for key in ("asset", "name", "ticker", "start", "end", "records")}
                self._json(payload)
            elif parsed.path == "/api/correlation":
                start = params.get("start", [None])[0]
                end = params.get("end", [None])[0]
                window = int(params.get("window", [30])[0])
                validate_date_range(start, end)
                if window <= 0:
                    raise ValueError("window must be positive")
                self._json(_correlation_payload(start, end, window))
            elif parsed.path.startswith("/api/"):
                self._json({"error": f"API endpoint not found: {parsed.path}"}, 404)
            else:
                self._serve_frontend(parsed.path)
        except (ValueError, DataFetchError) as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": f"internal server error: {exc}"}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/backtest":
            self._json({"error": "endpoint not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length))
            self._json(_backtest_payload(request))
        except (ValueError, TypeError, DataFetchError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, 400)
        except Exception as exc:
            self._json({"error": f"internal server error: {exc}"}, 500)

    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_frontend(self, request_path):
        relative = request_path.lstrip("/") or "index.html"
        target = (FRONTEND_DIR / relative).resolve()
        if FRONTEND_DIR not in target.parents and target != FRONTEND_DIR:
            self.send_error(403)
            return
        if not target.is_file():
            self.send_error(404)
            return
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(str(target))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), ApiHandler)
    print(f"QuantX running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
