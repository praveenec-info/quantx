// ==========================================
// MARKETLENS FRONTEND
// ==========================================


// Current selected asset
let selectedAsset = "gold";


// ==========================================
// SAMPLE FRONTEND DATA
// ==========================================

// These values are ONLY for displaying the UI.
// Replace them with Python/backend output later.

const marketData = {

    gold: {
        name: "Gold",
        price: "—",
        return: "—",
        volatility: "—",
        drawdown: "—"
    },

    bitcoin: {
        name: "Bitcoin",
        price: "—",
        return: "—",
        volatility: "—",
        drawdown: "—"
    },

    nvidia: {
        name: "NVIDIA",
        price: "—",
        return: "—",
        volatility: "—",
        drawdown: "—"
    }

};


// ==========================================
// SELECT ASSET
// ==========================================

function selectAsset(asset, button) {

    selectedAsset = asset;

    // Remove active state
    document.querySelectorAll(".asset-btn")
        .forEach(btn => {
            btn.classList.remove("active");
        });

    // Activate selected button
    button.classList.add("active");

    // Update asset name
    document.getElementById("selectedAsset").textContent =
        marketData[asset].name;

    updateDashboard();

}


// ==========================================
// UPDATE DASHBOARD
// ==========================================

function updateDashboard() {

    const asset = marketData[selectedAsset];

    document.getElementById("currentPrice").textContent =
        asset.price;

    document.getElementById("totalReturn").textContent =
        asset.return;

    document.getElementById("volatility").textContent =
        asset.volatility;

    document.getElementById("drawdown").textContent =
        asset.drawdown;

    document.getElementById("riskVolatility").textContent =
        asset.volatility;

    document.getElementById("riskDrawdown").textContent =
        asset.drawdown;

}


// ==========================================
// CHANGE PERIOD
// ==========================================

function changePeriod() {

    const period =
        document.getElementById("periodSelect").value;

    console.log(
        "Selected period:",
        period
    );

    /*
        Later this value will be sent
        to the Python backend.

        Example:

        /api/data?asset=gold&period=5Y
    */
}


// ==========================================
// REFRESH
// ==========================================

function refreshDashboard() {

    const button =
        document.querySelector(".refresh-btn");

    button.textContent = "↻ Updating...";

    setTimeout(() => {

        button.textContent = "↻ Refresh";

        updateDashboard();

    }, 800);

}


// ==========================================
// PRICE CHART
// ==========================================

const priceLabels = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
];


const priceValues = [
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null
];


const smaValues = [
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null
];


const emaValues = [
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null,
    null
];


const priceChart =
    new Chart(
        document.getElementById("priceChart"),
        {

            type: "line",

            data: {

                labels: priceLabels,

                datasets: [

                    {
                        label: "Price",
                        data: priceValues,

                        borderWidth: 2,

                        pointRadius: 0,

                        tension: 0.3
                    },

                    {
                        label: "SMA",
                        data: smaValues,

                        borderWidth: 1,

                        pointRadius: 0,

                        tension: 0.3
                    },

                    {
                        label: "EMA",
                        data: emaValues,

                        borderWidth: 1,

                        pointRadius: 0,

                        tension: 0.3
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        },

                        ticks: {
                            color: "#69737f"
                        }

                    },

                    y: {

                        grid: {
                            color: "#1d232b"
                        },

                        ticks: {
                            color: "#69737f"
                        }

                    }

                }

            }

        }
    );


// ==========================================
// EQUITY CURVE
// ==========================================

const equityChart =
    new Chart(
        document.getElementById("equityChart"),
        {

            type: "line",

            data: {

                labels: priceLabels,

                datasets: [

                    {
                        label: "Strategy",
                        data: Array(12).fill(null),

                        borderWidth: 2,

                        pointRadius: 0,

                        tension: 0.3
                    },

                    {
                        label: "Buy & Hold",
                        data: Array(12).fill(null),

                        borderWidth: 2,

                        pointRadius: 0,

                        tension: 0.3
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        labels: {
                            color: "#89929d"
                        }
                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        },

                        ticks: {
                            color: "#69737f"
                        }

                    },

                    y: {

                        grid: {
                            color: "#1d232b"
                        },

                        ticks: {
                            color: "#69737f"
                        }

                    }

                }

            }

        }
    );


// ==========================================
// INITIALIZE
// ==========================================

updateDashboard();
