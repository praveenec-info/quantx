import streamlit as st


def asset_selector():
    return st.sidebar.selectbox(
        "Select Asset",
        ["Gold", "Bitcoin", "NVIDIA"]
    )


def strategy_selector():
    return st.sidebar.selectbox(
        "Select Strategy",
        [
            "SMA Crossover",
            "EMA Trend",
            "Momentum",
            "Mean Reversion"
        ]
    )


def date_range_selector(data):
    min_date = data["Date"].min().date()
    max_date = data["Date"].max().date()

    return st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )


def display_metrics(total_return, volatility, sharpe_ratio, max_drawdown):
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Return",
        f"{total_return:.2f}%"
    )

    col2.metric(
        "Volatility",
        f"{volatility:.2f}%"
    )

    col3.metric(
        "Sharpe Ratio",
        f"{sharpe_ratio:.2f}"
    )

    col4.metric(
        "Max Drawdown",
        f"{max_drawdown:.2f}%"
    )


def signal_table(data):
    st.subheader("Trading Signals")

    if "Signal" not in data.columns:
        st.info("Trading signals are not available.")
        return

    signal_data = data[
        data["Signal"].isin(["BUY", "SELL"])
    ][["Date", "Price", "Signal"]]

    if signal_data.empty:
        st.info("No BUY or SELL signals available.")
    else:
        st.dataframe(
            signal_data.tail(20),
            use_container_width=True
        )