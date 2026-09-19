import plotly.express as px
import plotly.graph_objects as go


def plot_price(data, asset_name):
    fig = px.line(
        data,
        x="Date",
        y="Price",
        title=f"{asset_name} Historical Price"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price"
    )

    return fig


def plot_sma_ema(data, asset_name):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Price"],
            mode="lines",
            name="Price"
        )
    )

    if "SMA" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["SMA"],
                mode="lines",
                name="SMA"
            )
        )

    if "EMA" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["EMA"],
                mode="lines",
                name="EMA"
            )
        )

    fig.update_layout(
        title=f"{asset_name} - Price, SMA and EMA",
        xaxis_title="Date",
        yaxis_title="Price"
    )

    return fig


def plot_daily_returns(data):
    fig = px.line(
        data,
        x="Date",
        y="Daily_Return",
        title="Daily Returns"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Daily Return"
    )

    return fig


def plot_cumulative_returns(data):
    fig = px.line(
        data,
        x="Date",
        y="Cumulative_Return",
        title="Cumulative Returns"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cumulative Return"
    )

    return fig


def plot_volatility(data):
    fig = px.line(
        data,
        x="Date",
        y="Rolling_Volatility",
        title="Rolling Volatility"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Volatility"
    )

    return fig


def plot_drawdown(data):
    fig = px.area(
        data,
        x="Date",
        y="Drawdown",
        title="Drawdown"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Drawdown"
    )

    return fig


def plot_correlation(correlation_matrix):
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        title="Asset Correlation Heatmap"
    )

    return fig


def plot_equity_curve(data):
    fig = go.Figure()

    if "Strategy_Value" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["Strategy_Value"],
                mode="lines",
                name="Strategy"
            )
        )

    if "Buy_Hold_Value" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data["Date"],
                y=data["Buy_Hold_Value"],
                mode="lines",
                name="Buy & Hold"
            )
        )

    fig.update_layout(
        title="Strategy vs Buy & Hold",
        xaxis_title="Date",
        yaxis_title="Portfolio Value"
    )

    return fig


def plot_buy_sell_signals(data, asset_name):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Price"],
            mode="lines",
            name="Price"
        )
    )

    if "Signal" in data.columns:

        buy_data = data[data["Signal"] == "BUY"]
        sell_data = data[data["Signal"] == "SELL"]

        fig.add_trace(
            go.Scatter(
                x=buy_data["Date"],
                y=buy_data["Price"],
                mode="markers",
                name="BUY",
                marker=dict(
                    symbol="triangle-up",
                    size=12
                )
            )
        )

        fig.add_trace(
            go.Scatter(
                x=sell_data["Date"],
                y=sell_data["Price"],
                mode="markers",
                name="SELL",
                marker=dict(
                    symbol="triangle-down",
                    size=12
                )
            )
        )

    fig.update_layout(
        title=f"{asset_name} Buy / Sell Signals",
        xaxis_title="Date",
        yaxis_title="Price"
    )

    return fig