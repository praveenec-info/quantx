import streamlit as st
import pandas as pd
import numpy as np

from charts import (
    plot_price,
    plot_sma_ema,
    plot_daily_returns,
    plot_cumulative_returns,
    plot_volatility,
    plot_drawdown,
    plot_correlation,
    plot_equity_curve,
    plot_buy_sell_signals
)

from components import (
    asset_selector,
    strategy_selector,
    date_range_selector,
    display_metrics,
    signal_table
)


st.set_page_config(
    page_title="Multi-Asset Trading Analytics",
    page_icon="📈",
    layout="wide"
)


# --------------------------------------------------
# MOCK DATA
# Replace this later using Member 1, 2 and 3 outputs
# --------------------------------------------------

@st.cache_data
def generate_mock_data(asset):
    np.random.seed(42)

    dates = pd.date_range(
        start="2024-01-01",
        periods=500,
        freq="D"
    )

    if asset == "Gold":
        base_price = 2000

    elif asset == "Bitcoin":
        base_price = 40000

    else:
        base_price = 500

    random_returns = np.random.normal(
        loc=0.0005,
        scale=0.02,
        size=len(dates)
    )

    prices = base_price * np.exp(
        np.cumsum(random_returns)
    )

    data = pd.DataFrame({
        "Date": dates,
        "Price": prices
    })

    # Technical Indicators
    data["SMA"] = (
        data["Price"]
        .rolling(window=20)
        .mean()
    )

    data["EMA"] = (
        data["Price"]
        .ewm(span=20, adjust=False)
        .mean()
    )

    # Returns
    data["Daily_Return"] = (
        data["Price"]
        .pct_change()
    )

    data["Cumulative_Return"] = (
        (1 + data["Daily_Return"])
        .cumprod() - 1
    )

    # Volatility
    data["Rolling_Volatility"] = (
        data["Daily_Return"]
        .rolling(window=30)
        .std()
        * np.sqrt(252)
    )

    # Drawdown
    running_max = data["Price"].cummax()

    data["Drawdown"] = (
        data["Price"] / running_max
    ) - 1

    # Example Trading Signals
    data["Signal"] = ""

    data.loc[
        data["Price"] > data["SMA"],
        "Signal"
    ] = "BUY"

    data.loc[
        data["Price"] < data["SMA"],
        "Signal"
    ] = "SELL"

    # Example Strategy
    strategy_returns = (
        data["Daily_Return"]
        * np.where(
            data["Price"] > data["SMA"],
            1,
            0
        )
    )

    initial_capital = 100000

    data["Strategy_Value"] = (
        initial_capital
        * (1 + strategy_returns.fillna(0))
        .cumprod()
    )

    data["Buy_Hold_Value"] = (
        initial_capital
        * (1 + data["Daily_Return"].fillna(0))
        .cumprod()
    )

    return data


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📈 Multi-Asset Trading Analytics Dashboard")

st.write(
    """
    Interactive dashboard for analysing Gold, Bitcoin and NVIDIA
    using technical indicators, risk metrics and trading strategies.
    """
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Dashboard Controls")

asset = asset_selector()

strategy = strategy_selector()

data = generate_mock_data(asset)

selected_dates = date_range_selector(data)


# --------------------------------------------------
# DATE FILTER
# --------------------------------------------------

if isinstance(selected_dates, tuple):

    if len(selected_dates) == 2:

        start_date = pd.to_datetime(
            selected_dates[0]
        )

        end_date = pd.to_datetime(
            selected_dates[1]
        )

        filtered_data = data[
            (data["Date"] >= start_date)
            &
            (data["Date"] <= end_date)
        ].copy()

    else:
        filtered_data = data.copy()

else:
    filtered_data = data.copy()


# --------------------------------------------------
# BASIC CALCULATIONS
# --------------------------------------------------

daily_returns = filtered_data[
    "Daily_Return"
].dropna()


if len(daily_returns) > 0:

    total_return = (
        (
            filtered_data["Price"].iloc[-1]
            /
            filtered_data["Price"].iloc[0]
        ) - 1
    ) * 100

    volatility = (
        daily_returns.std()
        * np.sqrt(252)
        * 100
    )

    if daily_returns.std() != 0:

        sharpe_ratio = (
            daily_returns.mean()
            /
            daily_returns.std()
        ) * np.sqrt(252)

    else:
        sharpe_ratio = 0

    max_drawdown = (
        filtered_data["Drawdown"].min()
        * 100
    )

else:

    total_return = 0
    volatility = 0
    sharpe_ratio = 0
    max_drawdown = 0


# --------------------------------------------------
# METRICS
# --------------------------------------------------

st.subheader(
    f"{asset} | {strategy}"
)

display_metrics(
    total_return,
    volatility,
    sharpe_ratio,
    max_drawdown
)

st.divider()


# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📈 Market Overview",
        "📊 Technical Indicators",
        "⚠️ Risk Analysis",
        "🔗 Correlation",
        "💰 Backtesting"
    ]
)


# --------------------------------------------------
# MARKET OVERVIEW
# --------------------------------------------------

with tab1:

    st.header("Market Overview")

    st.plotly_chart(
        plot_price(
            filtered_data,
            asset
        ),
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.plotly_chart(
            plot_daily_returns(
                filtered_data
            ),
            use_container_width=True
        )

    with col2:

        st.plotly_chart(
            plot_cumulative_returns(
                filtered_data
            ),
            use_container_width=True
        )


# --------------------------------------------------
# TECHNICAL INDICATORS
# --------------------------------------------------

with tab2:

    st.header(
        "Technical Indicators"
    )

    st.plotly_chart(
        plot_sma_ema(
            filtered_data,
            asset
        ),
        use_container_width=True
    )

    st.info(
        """
        SMA and EMA help identify the general market trend.
        These values can later be directly connected to
        Member 2's analysis module.
        """
    )


# --------------------------------------------------
# RISK ANALYSIS
# --------------------------------------------------

with tab3:

    st.header(
        "Risk Analysis"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.plotly_chart(
            plot_volatility(
                filtered_data
            ),
            use_container_width=True
        )

    with col2:

        st.plotly_chart(
            plot_drawdown(
                filtered_data
            ),
            use_container_width=True
        )


# --------------------------------------------------
# CORRELATION
# --------------------------------------------------

with tab4:

    st.header(
        "Asset Correlation"
    )

    # Temporary mock correlation values
    # Replace later using Member 2 correlation output

    correlation_matrix = pd.DataFrame(
        [
            [1.00, 0.22, 0.18],
            [0.22, 1.00, 0.45],
            [0.18, 0.45, 1.00]
        ],
        columns=[
            "Gold",
            "Bitcoin",
            "NVIDIA"
        ],
        index=[
            "Gold",
            "Bitcoin",
            "NVIDIA"
        ]
    )

    st.plotly_chart(
        plot_correlation(
            correlation_matrix
        ),
        use_container_width=True
    )

    st.caption(
        "Temporary demonstration data. "
        "Replace with Member 2 correlation matrix."
    )


# --------------------------------------------------
# BACKTESTING
# --------------------------------------------------

with tab5:

    st.header(
        "Strategy Backtesting"
    )

    st.subheader(
        "Strategy vs Buy & Hold"
    )

    st.plotly_chart(
        plot_equity_curve(
            filtered_data
        ),
        use_container_width=True
    )

    st.subheader(
        "Buy / Sell Signals"
    )

    st.plotly_chart(
        plot_buy_sell_signals(
            filtered_data,
            asset
        ),
        use_container_width=True
    )

    signal_table(
        filtered_data
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Multi-Asset Trading Analytics Dashboard | "
    "Gold • Bitcoin • NVIDIA"
)