const API = "/api";
const assetNames = { gold: "Gold", bitcoin: "Bitcoin", nvidia: "NVIDIA" };
const state = { asset: "nvidia", start: "", end: "", analysis: null };

const $ = (selector) => document.querySelector(selector);
const formatPercent = (value) => value == null ? "--" : `${value >= 0 ? "+" : ""}${(value * 100).toFixed(2)}%`;
const formatNumber = (value, digits = 2) => value == null ? "--" : Number(value).toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));

function showState(selector, message, error = false) {
    const element = $(selector);
    if (element) element.innerHTML = `<p class="state-message${error ? " error" : ""}">${escapeHtml(message)}</p>`;
}

async function request(path, options = {}) {
    const response = await fetch(`${API}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
    const contentType = response.headers.get("content-type") || "unknown content type";
    const body = await response.text();
    if (!contentType.toLowerCase().includes("application/json")) {
        throw new Error(`API ${path} returned HTTP ${response.status} as ${contentType}, not JSON.`);
    }
    let payload;
    try {
        payload = JSON.parse(body);
    } catch (error) {
        throw new Error(`API ${path} returned invalid JSON with HTTP ${response.status}.`);
    }
    if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
    return payload;
}

function setLoading(loading) {
    $("#marketDataStatus").innerHTML = `<span></span> ${loading ? "Loading" : "Ready"}`;
    $("#pipelineState").textContent = loading ? "Fetching" : "Live data";
}

function drawLineChart(selector, records, lines, labelKey = "Date") {
    if (!records.length) return showState(selector, "No data returned for this range.", true);
    const width = 900;
    const height = 300;
    const values = lines.flatMap(line => records.map(row => Number(row[line.key])).filter(Number.isFinite));
    const minimum = Math.min(...values);
    const maximum = Math.max(...values);
    const range = maximum - minimum || 1;
    const points = (key) => records.map((row, index) => {
        const value = Number(row[key]);
        if (!Number.isFinite(value)) return null;
        const x = index / Math.max(records.length - 1, 1) * width;
        const y = height - ((value - minimum) / range) * (height - 25) - 10;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).filter(Boolean).join(" ");
    const svg = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Historical price chart"><line x1="0" y1="275" x2="900" y2="275" class="chart-axis"/>${lines.map(line => `<polyline points="${points(line.key)}" class="data-line ${line.className}"/><text x="${line.x || 20}" y="20" class="chart-label">${escapeHtml(line.label)}</text>`).join("")}</svg>`;
    $(selector).innerHTML = svg;
}

function renderAssetCards(payload) {
    const latest = payload.records[payload.records.length - 1];
    $("#assetGrid").innerHTML = Object.keys(assetNames).map(asset => {
        const isSelected = asset === payload.asset;
        return `<article class="asset-card ${isSelected ? "selected" : ""}"><div class="asset-icon ${asset}">${asset === "gold" ? "Au" : asset === "bitcoin" ? "₿" : "NV"}</div><h3>${assetNames[asset]}</h3><p>${asset === "gold" ? "Precious Metal" : asset === "bitcoin" ? "Cryptocurrency" : "Technology"}</p>${isSelected ? `<strong>${formatNumber(latest.Close)}</strong><span class="positive">${formatPercent(latest.Daily_Return)}</span>` : `<strong>Choose asset</strong><span class="data-note">Fetch separately</span>`}</article>`;
    }).join("");
}

function renderMetrics(metrics) {
    const values = [["Current price", formatNumber(metrics.price)], ["Daily return", formatPercent(metrics.daily_return)], ["Cumulative return", formatPercent(metrics.cumulative_return)], ["Annualized volatility", formatPercent(metrics.annualized_volatility)], ["Sharpe ratio", formatNumber(metrics.sharpe_ratio)], ["Maximum drawdown", formatPercent(metrics.maximum_drawdown)], ["Rolling return", formatPercent(metrics.rolling_return)], ["Market regime", metrics.regime || "--"]];
    $("#metricsGrid").innerHTML = values.map(([label, value]) => `<div class="metric-card"><span>${label}</span><strong>${value}</strong><small>Backend calculation</small></div>`).join("");
}

async function loadAnalysis() {
    const asset = $("#assetSelect").value;
    const start = $("#startDate").value;
    const end = $("#endDate").value;
    state.asset = asset;
    state.start = start;
    state.end = end;
    setLoading(true);
    showState("#assetGrid", "Fetching historical data...");
    try {
        const query = new URLSearchParams({ asset });
        if (start) query.set("start", start);
        if (end) query.set("end", end);
        const payload = await request(`/analysis?${query}`);
        state.analysis = payload;
        $("#dataRange").textContent = `${payload.start} to ${payload.end}`;
        $("#analysisTitle").textContent = `${payload.name} historical price`;
        $("#currentPrice").textContent = formatNumber(payload.metrics.price);
        renderAssetCards(payload);
        renderMetrics(payload.metrics);
        drawLineChart("#priceChart", payload.records, [{ key: "Close", label: "Close", className: "price-line" }, { key: "SMA", label: "SMA", className: "sma-line", x: 130 }, { key: "EMA", label: "EMA", className: "ema-line", x: 200 }]);
    } catch (error) {
        showState("#assetGrid", error.message, true);
        showState("#priceChart", "Data unavailable. Check the date range or network connection.", true);
        showState("#metricsGrid", error.message, true);
    } finally {
        setLoading(false);
    }
}

async function loadCorrelation() {
    const button = $("#correlationButton");
    button.disabled = true;
    $("#corrTable").innerHTML = "<tbody><tr><td>Calculating aligned daily-return correlations...</td></tr></tbody>";
    try {
        const query = new URLSearchParams();
        if (state.start) query.set("start", state.start);
        if (state.end) query.set("end", state.end);
        const payload = await request(`/correlation?${query}`);
        const columns = Object.keys(payload.matrix);
        $("#corrTable").innerHTML = `<thead><tr><th>Asset</th>${columns.map(column => `<th>${assetNames[column]}</th>`).join("")}</tr></thead><tbody>${columns.map(row => `<tr><th>${assetNames[row]}</th>${columns.map(column => `<td>${formatNumber(payload.matrix[row][column])}</td>`).join("")}</tr>`).join("")}</tbody>`;
    } catch (error) {
        $("#corrTable").innerHTML = `<tbody><tr><td class="error">${escapeHtml(error.message)}</td></tr></tbody>`;
    } finally {
        button.disabled = false;
    }
}

function renderBacktest(payload) {
    const strategy = payload.metrics.strategy;
    const benchmark = payload.metrics.benchmark;
    const rows = [["Total return", formatPercent(strategy.total_return), formatPercent(benchmark.total_return)], ["Final portfolio value", formatNumber(strategy.final_value), formatNumber(benchmark.final_value)], ["Volatility", formatPercent(strategy.volatility), formatPercent(benchmark.volatility)], ["Sharpe ratio", formatNumber(strategy.sharpe_ratio), formatNumber(benchmark.sharpe_ratio)], ["Maximum drawdown", formatPercent(strategy.maximum_drawdown), formatPercent(benchmark.maximum_drawdown)], ["Number of trades", strategy.number_of_trades, benchmark.number_of_trades]];
    $("#backtestResults").innerHTML = `<table><thead><tr><th>Metric</th><th>Strategy</th><th>Buy & Hold</th></tr></thead><tbody>${rows.map(row => `<tr>${row.map(value => `<td>${value}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    drawLineChart("#equityChart", payload.records, [{ key: "Equity", label: "Strategy equity", className: "price-line" }, { key: "Benchmark_Equity", label: "Buy & hold", className: "sma-line", x: 160 }]);
}

async function runBacktest() {
    $("#backtestState").textContent = "Running backtest...";
    try {
        const payload = await request("/backtest", { method: "POST", body: JSON.stringify({ asset: $("#backtestAsset").value, strategy: $("#strategy").value, start: state.start || undefined, end: state.end || undefined, fast_period: Number($("#fastPeriod").value), slow_period: Number($("#slowPeriod").value), momentum_period: Number($("#momentumPeriod").value), mean_window: Number($("#meanWindow").value), entry_zscore: Number($("#entryZscore").value), initial_capital: Number($("#capital").value), position_size: Number($("#positionSize").value), transaction_cost: Number($("#transactionCost").value) }) });
        $("#backtestState").textContent = "Backtest complete.";
        renderBacktest(payload);
    } catch (error) {
        $("#backtestState").textContent = error.message;
        $("#backtestState").classList.add("error");
        showState("#equityChart", "Backtest unavailable.", true);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const end = new Date();
    const start = new Date();
    start.setFullYear(end.getFullYear() - 2);
    $("#startDate").value = start.toISOString().slice(0, 10);
    $("#endDate").value = end.toISOString().slice(0, 10);
    $("#loadDataButton").addEventListener("click", () => document.querySelector("#assets").scrollIntoView({ behavior: "smooth" }));
    $("#refreshButton").addEventListener("click", loadAnalysis);
    $("#correlationButton").addEventListener("click", loadCorrelation);
    $("#runBacktestButton").addEventListener("click", runBacktest);
    loadAnalysis();
});
