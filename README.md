# Supply Chain Inventory Analytics

A Big Data Analytics project focused on optimizing supply chain operations, supplier performance, and inventory health using Python and an interactive Streamlit dashboard.

---

## 📌 Project Overview
Modern supply chain management relies on data-driven decision-making to mitigate stockouts, minimize holding costs, and optimize vendor fulfillment cycles. This project analyzes four core dimensions of supply chain operations:

- **Purchase Data**: Tracking orders, purchase costs, volume, and purchasing patterns.
- **Supplier Data**: Evaluating lead times, reliability, and supplier compliance metrics.
- **Inventory Data**: Monitoring stock levels, stock turnover ratios, and identifying high-risk or obsolete inventory.
- **Delivery Data**: Tracking transit times, delayed shipments, and on-time in-full (OTIF) fulfillment rates.

---

## 📂 Project Structure

```text
Supply-Chain-Inventory-Analytics/
│
├── data/                      # Raw and processed datasets (purchase, supplier, inventory, delivery)
│   └── .gitkeep
│
├── src/                       # Data processing and analytical pipelines
│   ├── data_cleaning.py       # Ingestion, schema validation, and preprocessing
│   ├── analytics.py           # Exploratory data analysis, KPI metrics, and aggregations
│   └── recommendations.py     # Actionable business insights and decision-support logic
│
├── dashboard/                 # Presentation layer
│   └── app.py                 # Streamlit business analytics dashboard entry point
│
└── README.md                  # Project documentation and architectural overview
```

---

## 🛠️ Tech Stack (Planned)
- **Language**: Python 3.x
- **Data Processing & Analytics**: Pandas, NumPy
- **Dashboard & Visualization**: Streamlit, Plotly / Matplotlib / Seaborn
