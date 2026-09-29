"""
Supply Chain & Inventory Analytics - Interactive Dashboard
Built with Python, Streamlit, and Plotly.

Entry point for inventory, supplier, and delivery performance monitoring.
"""

import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure project root is in sys.path to import src.analytics
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.analytics import (
    load_data,
    calculate_product_inventory,
    calculate_inventory_metrics,
    calculate_delivery_metrics,
    calculate_supplier_performance,
    calculate_purchase_metrics,
    get_stockout_risk,
    get_excess_inventory,
    generate_recommendations,
)

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Supply Chain & Inventory Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Professional Restrained Styling (Business Analytics Standard)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main container background */
    .stApp {
        background-color: #F8FAFC;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }
    
    /* Typography hierarchy */
    h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0F172A;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    /* Header typography */
    .app-header {
        margin-bottom: 1rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #E2E8F0;
    }
    .app-title {
        font-size: 1.65rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        line-height: 1.2;
    }
    .app-subtitle {
        font-size: 0.88rem;
        color: #64748B;
        margin-top: 0.2rem;
        margin-bottom: 0;
    }
    
    /* KPI Metric Cards - Equal height, non-wrapping, clean border */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 10px 12px;
        min-height: 84px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
    }
    .kpi-title {
        font-size: 0.68rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.15;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-subtext {
        font-size: 0.72rem;
        color: #64748B;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Data Summary Banner */
    .data-summary-banner {
        font-size: 0.82rem;
        color: #475569;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #2563EB;
        border-radius: 4px;
        padding: 6px 12px;
        margin-top: 10px;
        margin-bottom: 14px;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #0F172A;
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    /* Alert cards for recommendations */
    .alert-card {
        background-color: #FFFFFF;
        border-left: 3px solid #CBD5E1;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        border-radius: 4px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .alert-high {
        border-left-color: #DC2626;
    }
    .alert-medium {
        border-left-color: #D97706;
    }
    .alert-low {
        border-left-color: #2563EB;
    }
    .alert-badge {
        display: inline-block;
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        padding: 2px 6px;
        border-radius: 3px;
        letter-spacing: 0.03em;
    }
    .badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .badge-medium {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .badge-low {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    
    /* Footer */
    .app-footer {
        margin-top: 2.5rem;
        padding-top: 0.75rem;
        border-top: 1px solid #E2E8F0;
        text-align: center;
        font-size: 0.78rem;
        color: #94A3B8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Formatting Helpers
# -----------------------------------------------------------------------------
def format_currency_compact(val: float) -> str:
    """Format large monetary values compactly ($1.46M, $45.2K, $120.00)."""
    if abs(val) >= 1_000_000_000:
        return f"${val / 1e9:.2f}B"
    elif abs(val) >= 1_000_000:
        return f"${val / 1e6:.2f}M"
    elif abs(val) >= 1_000:
        return f"${val / 1e3:.1f}K"
    else:
        return f"${val:,.2f}"


def format_number_compact(val: int | float) -> str:
    """Format integer/float units compactly."""
    if abs(val) >= 1_000_000:
        return f"{val / 1e6:.2f}M"
    elif abs(val) >= 100_000:
        return f"{val / 1e3:.1f}K"
    else:
        return f"{val:,.0f}"


# -----------------------------------------------------------------------------
# Plotly Standard Theme & Unambiguous Layout Application
# -----------------------------------------------------------------------------
# Base theme layout (NOTE: Does NOT contain 'height' to prevent duplicates)
CHART_LAYOUT = dict(
    font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", color="#334155", size=11),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=40, r=20, t=36, b=36),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
)


def apply_chart_layout(fig, height: int = 300, **kwargs):
    """
    Applies the standardized layout dictionary and assigns 'height' exactly once.
    Safely intercepts any keyword argument without duplication.
    """
    layout = CHART_LAYOUT.copy()
    h = kwargs.pop("height", height)
    layout["height"] = h
    layout.update(kwargs)
    fig.update_layout(**layout)
    return fig


# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_all_datasets():
    """Load and parse the 5 core CSV datasets."""
    try:
        return load_data()
    except Exception as e:
        st.error(f"Error loading supply chain datasets: {e}")
        st.stop()


# Load raw datasets
df_products, df_suppliers, df_purchases, df_deliveries, df_inventory = load_all_datasets()

# Precompute mapping from Purchase_ID -> Product_ID for cross-table integrity
po_to_prod = dict(zip(df_purchases["Purchase_ID"], df_purchases["Product_ID"]))

all_categories = sorted(df_products["Category"].unique().tolist())
all_suppliers = sorted(df_suppliers["Supplier_Name"].unique().tolist())
all_statuses = ["Low Stock", "Normal", "Excess Stock"]

min_date = df_inventory["Date"].min().date()
max_date = df_inventory["Date"].max().date()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Dynamic Filters
# -----------------------------------------------------------------------------
st.sidebar.markdown("### Navigation")
page_selection = st.sidebar.radio(
    label="Page",
    options=["Executive Overview", "Inventory Analysis", "Supplier & Delivery", "Recommendations"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

# Reset filters button
if st.sidebar.button("Reset Filters", use_container_width=True):
    st.session_state["filter_date_range"] = (min_date, max_date)
    st.session_state["filter_categories"] = []
    st.session_state["filter_suppliers"] = []
    st.session_state["filter_statuses"] = []
    st.rerun()

# 1. Date Range Filter
date_range = st.sidebar.date_input(
    "Date Range",
    value=st.session_state.get("filter_date_range", (min_date, max_date)),
    min_value=min_date,
    max_value=max_date,
    key="filter_date_range",
)

# 2. Category Filter
selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=all_categories,
    default=st.session_state.get("filter_categories", []),
    placeholder="All Categories",
    key="filter_categories",
)

# 3. Supplier Filter
selected_suppliers = st.sidebar.multiselect(
    "Supplier",
    options=all_suppliers,
    default=st.session_state.get("filter_suppliers", []),
    placeholder="All Suppliers",
    key="filter_suppliers",
)

# 4. Stock Status Filter
selected_statuses = st.sidebar.multiselect(
    "Stock Status",
    options=all_statuses,
    default=st.session_state.get("filter_statuses", []),
    placeholder="All Statuses",
    key="filter_statuses",
)

# -----------------------------------------------------------------------------
# Systematic Filter Propagation (Sections A, B, C, D)
# -----------------------------------------------------------------------------
# Resolve start and end dates safely
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_d, end_d = date_range
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    start_d = date_range[0]
    end_d = max_date
else:
    start_d, end_d = min_date, max_date

start_dt = pd.to_datetime(start_d)
end_dt = pd.to_datetime(end_d)

# A. Product Category: Filter products first
f_products = df_products.copy()
if selected_categories:
    f_products = f_products[f_products["Category"].isin(selected_categories)]

# B. Supplier: Filter suppliers first, then derive valid Supplier_IDs
f_suppliers = df_suppliers.copy()
if selected_suppliers:
    f_suppliers = f_suppliers[f_suppliers["Supplier_Name"].isin(selected_suppliers)]
valid_supplier_ids = set(f_suppliers["Supplier_ID"])

# C. Date:
# Filter Inventory (by Date and active products)
cat_product_ids = set(f_products["Product_ID"])
f_inventory = df_inventory[
    (df_inventory["Date"] >= start_dt)
    & (df_inventory["Date"] <= end_dt)
    & (df_inventory["Product_ID"].isin(cat_product_ids))
].copy()

# Filter Purchases (by Purchase_Date, active suppliers, and active products)
f_purchases = df_purchases[
    (df_purchases["Purchase_Date"] >= start_dt)
    & (df_purchases["Purchase_Date"] <= end_dt)
    & (df_purchases["Supplier_ID"].isin(valid_supplier_ids))
    & (df_purchases["Product_ID"].isin(cat_product_ids))
].copy()

# Filter Deliveries (by Order_Date, active suppliers, and active products via Purchase_ID)
deliv_pids = df_deliveries["Purchase_ID"].map(po_to_prod)
f_deliveries = df_deliveries[
    (df_deliveries["Order_Date"] >= start_dt)
    & (df_deliveries["Order_Date"] <= end_dt)
    & (df_deliveries["Supplier_ID"].isin(valid_supplier_ids))
    & (deliv_pids.isin(cat_product_ids))
].copy()

# D. Stock Status:
# Calculate product inventory status after applying the product/date filters
if not f_products.empty and not f_inventory.empty:
    f_prod_inv = calculate_product_inventory(f_products, f_inventory)
else:
    f_prod_inv = pd.DataFrame()

if selected_statuses:
    if not f_prod_inv.empty:
        f_prod_inv = f_prod_inv[f_prod_inv["Stock_Status"].isin(selected_statuses)]
        matching_pids = set(f_prod_inv["Product_ID"])
    else:
        matching_pids = set()

    # Synchronously filter f_products, f_inventory, f_purchases, and f_deliveries
    f_products = f_products[f_products["Product_ID"].isin(matching_pids)]
    f_inventory = f_inventory[f_inventory["Product_ID"].isin(matching_pids)]
    f_purchases = f_purchases[f_purchases["Product_ID"].isin(matching_pids)]
    valid_pur_ids = set(f_purchases["Purchase_ID"])
    f_deliveries = f_deliveries[f_deliveries["Purchase_ID"].isin(valid_pur_ids)]

# -----------------------------------------------------------------------------
# Common UI Helpers
# -----------------------------------------------------------------------------
def render_header(subtitle_override: str | None = None):
    st.markdown(
        f"""
        <div class="app-header">
            <h1 class="app-title">Supply Chain & Inventory Analytics</h1>
            <p class="app-subtitle">{subtitle_override or "Inventory, supplier and delivery performance monitoring"}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(col, label: str, value: str, subtext: str, tooltip: str = ""):
    tooltip_attr = f'title="{tooltip}"' if tooltip else ""
    col.markdown(
        f"""
        <div class="kpi-card" {tooltip_attr}>
            <div class="kpi-title">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# PAGE 1: Executive Overview
# -----------------------------------------------------------------------------
if page_selection == "Executive Overview":
    render_header()

    if f_inventory.empty or f_products.empty or f_prod_inv.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Calculate high-level metrics
        inv_metrics = calculate_inventory_metrics(f_products, f_inventory)
        deliv_metrics = calculate_delivery_metrics(f_deliveries)

        # 6 KPI Cards (Equal height, non-wrapping compact values)
        kpi_cols = st.columns(6)
        render_kpi_card(
            kpi_cols[0],
            "CURRENT STOCK",
            f"{inv_metrics['total_current_inventory']:,}",
            "Active units on hand",
            tooltip=f"{inv_metrics['total_current_inventory']:,} units",
        )
        render_kpi_card(
            kpi_cols[1],
            "INVENTORY VALUE",
            format_currency_compact(inv_metrics["total_inventory_value"]),
            "Total portfolio valuation",
            tooltip=f"${inv_metrics['total_inventory_value']:,.2f}",
        )
        render_kpi_card(
            kpi_cols[2],
            "LOW STOCK",
            f"{inv_metrics['products_at_or_below_reorder']:,}",
            "At or below reorder level",
            tooltip=f"{inv_metrics['products_at_or_below_reorder']} products",
        )
        render_kpi_card(
            kpi_cols[3],
            "EXCESS STOCK",
            f"{inv_metrics['excess_inventory_products']:,}",
            "> 60-day planned demand",
            tooltip=f"{inv_metrics['excess_inventory_products']} products",
        )
        render_kpi_card(
            kpi_cols[4],
            "ON-TIME DELIVERY",
            f"{deliv_metrics['on_time_delivery_percentage']:.1f}%",
            f"{deliv_metrics['on_time_deliveries']:,} on-time orders",
            tooltip=f"{deliv_metrics['on_time_deliveries']:,} of {deliv_metrics['total_deliveries']:,} orders",
        )
        render_kpi_card(
            kpi_cols[5],
            "DELAYED DELIVERIES",
            f"{deliv_metrics['delayed_deliveries']:,}",
            f"{deliv_metrics['delayed_delivery_percentage']:.1f}% of total deliveries",
            tooltip=f"{deliv_metrics['delayed_deliveries']:,} delayed orders",
        )

        # Dynamic Data Summary Banner
        st.markdown(
            f"""
            <div class="data-summary-banner">
                {deliv_metrics['total_deliveries']:,} deliveries &nbsp;|&nbsp; 
                {deliv_metrics['on_time_delivery_percentage']:.1f}% on-time &nbsp;|&nbsp; 
                {deliv_metrics['delayed_delivery_percentage']:.1f}% delayed &nbsp;|&nbsp; 
                {inv_metrics['total_current_inventory']:,} units currently in stock
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4 Core Charts (2x2 Grid)
        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)

        # Chart 1: Inventory Trend (Aggregated by month, last closing stock of each month)
        with c1:
            daily_total = f_inventory.groupby("Date", as_index=False)["Closing_Stock"].sum()
            daily_total["Year_Month"] = daily_total["Date"].dt.strftime("%Y-%m")
            monthly_inv = daily_total.sort_values("Date").groupby("Year_Month", as_index=False).last()

            fig_inv = px.line(
                monthly_inv,
                x="Year_Month",
                y="Closing_Stock",
                markers=True,
                color_discrete_sequence=["#2563EB"],
            )
            apply_chart_layout(
                fig_inv,
                height=265,
                title=dict(text="Inventory Trend", font=dict(size=13, color="#0F172A")),
                yaxis=dict(title=None, tickformat="~s"),
                xaxis=dict(title=None, tickangle=-45),
            )
            fig_inv.update_traces(
                line=dict(width=2),
                hovertemplate="<b>%{x}</b><br>Closing Stock: %{y:,} units<extra></extra>",
            )
            st.plotly_chart(fig_inv, use_container_width=True)

        # Chart 2: Monthly Purchase Spend (Group purchases by month and sum Total_Cost)
        with c2:
            if not f_purchases.empty:
                monthly_purch = f_purchases.copy()
                monthly_purch["Year_Month"] = monthly_purch["Purchase_Date"].dt.strftime("%Y-%m")
                monthly_spend = monthly_purch.groupby("Year_Month", as_index=False)["Total_Cost"].sum()

                fig_spend = px.bar(
                    monthly_spend,
                    x="Year_Month",
                    y="Total_Cost",
                    color_discrete_sequence=["#3B82F6"],
                )
                apply_chart_layout(
                    fig_spend,
                    height=265,
                    title=dict(text="Monthly Purchase Spend", font=dict(size=13, color="#0F172A")),
                    yaxis=dict(title=None, tickprefix="$", tickformat="~s"),
                    xaxis=dict(title=None, tickangle=-45),
                )
                fig_spend.update_traces(hovertemplate="<b>%{x}</b><br>Spend: $%{y:,.2f}<extra></extra>")
                st.plotly_chart(fig_spend, use_container_width=True)
            else:
                st.info("No purchase records match current filters.")

        # Chart 3: Delivery Status (On-Time vs Delayed)
        with c3:
            if not f_deliveries.empty:
                status_counts = f_deliveries["Delivery_Status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                color_map = {"On-Time": "#10B981", "Delayed": "#DC2626"}
                fig_deliv = px.pie(
                    status_counts,
                    names="Status",
                    values="Count",
                    hole=0.55,
                    color="Status",
                    color_discrete_map=color_map,
                )
                apply_chart_layout(
                    fig_deliv,
                    height=265,
                    title=dict(text="Delivery Status", font=dict(size=13, color="#0F172A")),
                )
                fig_deliv.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    hovertemplate="<b>%{label}:</b> %{value:,} (%{percent})<extra></extra>",
                )
                st.plotly_chart(fig_deliv, use_container_width=True)
            else:
                st.info("No delivery records match current filters.")

        # Chart 4: Supplier On-Time Delivery (All selected/active suppliers, horizontal bars)
        with c4:
            if not f_deliveries.empty:
                sup_perf = calculate_supplier_performance(f_suppliers, f_deliveries)
                sup_perf_sorted = sup_perf.sort_values(by="On_Time_Delivery_Percentage", ascending=True)
                fig_sup = px.bar(
                    sup_perf_sorted,
                    x="On_Time_Delivery_Percentage",
                    y="Supplier_Name",
                    orientation="h",
                    color="On_Time_Delivery_Percentage",
                    color_continuous_scale=["#DC2626", "#F59E0B", "#10B981"],
                )
                apply_chart_layout(
                    fig_sup,
                    height=265,
                    title=dict(text="Supplier On-Time Delivery", font=dict(size=13, color="#0F172A")),
                    coloraxis_showscale=False,
                    xaxis=dict(title=None, tickformat=".1f", ticksuffix="%", range=[60, 102]),
                    yaxis=dict(title=None, automargin=True),
                )
                fig_sup.update_traces(hovertemplate="<b>%{y}</b><br>On-Time: %{x:.1f}%<extra></extra>")
                st.plotly_chart(fig_sup, use_container_width=True)
            else:
                st.info("No supplier performance data available.")

        # Critical Alerts Section
        st.markdown("<div class='section-title'>Critical Alerts</div>", unsafe_allow_html=True)
        a_col1, a_col2, a_col3 = st.columns(3)

        # 1. Low-stock products
        with a_col1:
            st.caption("Low-Stock Products")
            stockouts = get_stockout_risk(f_products, f_inventory)
            if not stockouts.empty:
                st.dataframe(
                    stockouts[["Product_Name", "Current_Stock", "Reorder_Level", "Risk_Level"]].rename(
                        columns={
                            "Product_Name": "Product",
                            "Current_Stock": "Stock",
                            "Reorder_Level": "Reorder",
                            "Risk_Level": "Risk",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=180,
                )
            else:
                st.success("All products holding sufficient safety buffer.")

        # 2. Excess-inventory products
        with a_col2:
            st.caption("Excess-Inventory Products")
            excess_items = get_excess_inventory(f_products, f_inventory)
            if not excess_items.empty:
                display_ex = excess_items[["Product_Name", "Current_Stock", "Target_Stock_Level", "Inventory_Value"]].head(5).copy()
                display_ex["Inventory_Value"] = display_ex["Inventory_Value"].apply(format_currency_compact)
                st.dataframe(
                    display_ex.rename(
                        columns={
                            "Product_Name": "Product",
                            "Current_Stock": "Stock",
                            "Target_Stock_Level": "60d Target",
                            "Inventory_Value": "Value",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=180,
                )
            else:
                st.success("No products holding surplus inventory above target.")

        # 3. Suppliers with significant delivery delays
        with a_col3:
            st.caption("Suppliers with Significant Delays")
            if not f_deliveries.empty:
                sup_perf = calculate_supplier_performance(f_suppliers, f_deliveries)
                delayed_sups = sup_perf[sup_perf["On_Time_Delivery_Percentage"] < 88.0].sort_values(
                    by="On_Time_Delivery_Percentage"
                )
                if not delayed_sups.empty:
                    st.dataframe(
                        delayed_sups[["Supplier_Name", "On_Time_Delivery_Percentage", "Average_Delay_Days"]].rename(
                            columns={
                                "Supplier_Name": "Supplier",
                                "On_Time_Delivery_Percentage": "On-Time %",
                                "Average_Delay_Days": "Avg Delay (d)",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                        height=180,
                    )
                else:
                    st.success("All suppliers meeting on-time delivery benchmarks.")
            else:
                st.info("No delivery records to evaluate.")

# -----------------------------------------------------------------------------
# PAGE 2: Inventory Analysis
# -----------------------------------------------------------------------------
elif page_selection == "Inventory Analysis":
    render_header("Comprehensive product inventory, safety stock, and category analysis")

    if f_prod_inv.empty or f_inventory.empty or f_products.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Charts Row 1
        inv_c1, inv_c2 = st.columns(2)

        # 1. Current Stock vs Reorder Level (Top 15 products by current stock, horizontal bars)
        with inv_c1:
            top15_inv = f_prod_inv.sort_values(by="Latest_Closing_Stock", ascending=True).tail(15)
            fig_compare = go.Figure()
            fig_compare.add_trace(
                go.Bar(
                    y=top15_inv["Product_Name"],
                    x=top15_inv["Latest_Closing_Stock"],
                    name="Current Stock",
                    orientation="h",
                    marker_color="#2563EB",
                    customdata=np.stack((top15_inv["Latest_Closing_Stock"], top15_inv["Reorder_Level"]), axis=-1),
                    hovertemplate="<b>Product:</b> %{y}<br><b>Current Stock:</b> %{customdata[0]:,}<br><b>Reorder Level:</b> %{customdata[1]:,}<extra></extra>",
                )
            )
            fig_compare.add_trace(
                go.Bar(
                    y=top15_inv["Product_Name"],
                    x=top15_inv["Reorder_Level"],
                    name="Reorder Level",
                    orientation="h",
                    marker_color="#F59E0B",
                    customdata=np.stack((top15_inv["Latest_Closing_Stock"], top15_inv["Reorder_Level"]), axis=-1),
                    hovertemplate="<b>Product:</b> %{y}<br><b>Current Stock:</b> %{customdata[0]:,}<br><b>Reorder Level:</b> %{customdata[1]:,}<extra></extra>",
                )
            )
            apply_chart_layout(
                fig_compare,
                height=350,
                title=dict(text="Top 15 Products: Current Stock vs. Reorder Level", font=dict(size=13, color="#0F172A")),
                barmode="group",
                xaxis=dict(title="Units", tickformat="~s"),
                yaxis=dict(title=None, automargin=True),
            )
            st.plotly_chart(fig_compare, use_container_width=True)

        # 2. Inventory Value by Category (Horizontal bar chart)
        with inv_c2:
            cat_val = f_prod_inv.groupby("Category", as_index=False)["Inventory_Value"].sum()
            cat_val = cat_val.sort_values(by="Inventory_Value", ascending=True)
            fig_cat = px.bar(
                cat_val,
                x="Inventory_Value",
                y="Category",
                orientation="h",
                color="Inventory_Value",
                color_continuous_scale="Blues",
            )
            apply_chart_layout(
                fig_cat,
                height=350,
                title=dict(text="Inventory Value by Category", font=dict(size=13, color="#0F172A")),
                coloraxis_showscale=False,
                xaxis=dict(title="Total Value ($)", tickprefix="$", tickformat="~s"),
                yaxis=dict(title=None, automargin=True),
            )
            fig_cat.update_traces(hovertemplate="<b>%{y}</b><br>Value: $%{x:,.2f}<extra></extra>")
            st.plotly_chart(fig_cat, use_container_width=True)

        # Charts Row 2
        inv_c3, inv_c4 = st.columns(2)

        # 3. Stock Status Distribution
        with inv_c3:
            status_df = f_prod_inv["Stock_Status"].value_counts().reset_index()
            status_df.columns = ["Stock_Status", "Count"]
            color_status_map = {"Low Stock": "#DC2626", "Normal": "#10B981", "Excess Stock": "#F59E0B"}
            fig_status = px.bar(
                status_df,
                x="Stock_Status",
                y="Count",
                color="Stock_Status",
                color_discrete_map=color_status_map,
            )
            apply_chart_layout(
                fig_status,
                height=265,
                title=dict(text="Stock Status Distribution", font=dict(size=13, color="#0F172A")),
                showlegend=False,
                xaxis=dict(title=None),
                yaxis=dict(title="Products", tickformat=".0f"),
            )
            fig_status.update_traces(hovertemplate="<b>%{x}:</b> %{y} products<extra></extra>")
            st.plotly_chart(fig_status, use_container_width=True)

        # 4. Daily Demand vs Current Stock
        with inv_c4:
            fig_scatter = px.scatter(
                f_prod_inv,
                x="Average_Daily_Demand",
                y="Latest_Closing_Stock",
                color="Stock_Status",
                color_discrete_map=color_status_map,
                hover_name="Product_Name",
                size="Inventory_Value",
            )
            apply_chart_layout(
                fig_scatter,
                height=265,
                title=dict(text="Daily Demand vs. Current Stock", font=dict(size=13, color="#0F172A")),
                xaxis=dict(title="Avg Daily Demand (Units/Day)", tickformat=".1f"),
                yaxis=dict(title="Closing Stock", tickformat="~s"),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Product Inventory Table
        st.markdown("<div class='section-title'>Product Inventory Table</div>", unsafe_allow_html=True)
        display_prod = f_prod_inv.copy()
        display_prod["Formatted_Value"] = display_prod["Inventory_Value"].apply(format_currency_compact)
        display_prod_table = display_prod[[
            "Product_ID", "Product_Name", "Category", "Unit_Cost", "Latest_Closing_Stock",
            "Reorder_Level", "Target_Stock_Level", "Stock_Status", "Formatted_Value"
        ]].rename(columns={
            "Product_ID": "SKU",
            "Product_Name": "Product",
            "Category": "Category",
            "Unit_Cost": "Unit Cost ($)",
            "Latest_Closing_Stock": "Current Stock",
            "Reorder_Level": "Reorder Level",
            "Target_Stock_Level": "Target Stock (60d)",
            "Stock_Status": "Status",
            "Formatted_Value": "Inventory Value",
        })
        st.dataframe(display_prod_table, use_container_width=True, hide_index=True)

        # Detailed Audit Tables
        st.markdown("<div class='section-title'>Inventory Audit Tables</div>", unsafe_allow_html=True)
        t_col1, t_col2 = st.columns(2)

        # Low-stock products table
        with t_col1:
            st.caption("Low-Stock Products")
            low_stock_df = get_stockout_risk(f_products, f_inventory)
            if not low_stock_df.empty:
                display_low = low_stock_df[[
                    "Product_Name", "Category", "Current_Stock", "Reorder_Level", "Stock_Gap", "Risk_Level"
                ]].rename(
                    columns={
                        "Product_Name": "Product",
                        "Category": "Category",
                        "Current_Stock": "Current Stock",
                        "Reorder_Level": "Reorder Level",
                        "Stock_Gap": "Stock Gap",
                        "Risk_Level": "Risk Level",
                    }
                )
                st.dataframe(display_low, use_container_width=True, hide_index=True)
            else:
                st.success("No products currently in Low Stock status.")

        # Excess inventory table
        with t_col2:
            st.caption("Excess-Inventory Products")
            excess_stock_df = get_excess_inventory(f_products, f_inventory)
            if not excess_stock_df.empty:
                display_excess = excess_stock_df[[
                    "Product_Name", "Category", "Current_Stock", "Target_Stock_Level", "Estimated_Excess_Quantity", "Inventory_Value"
                ]].copy()
                display_excess["Inventory_Value"] = display_excess["Inventory_Value"].apply(format_currency_compact)
                display_excess = display_excess.rename(
                    columns={
                        "Product_Name": "Product",
                        "Category": "Category",
                        "Current_Stock": "Current Stock",
                        "Target_Stock_Level": "Target Stock",
                        "Estimated_Excess_Quantity": "Estimated Excess",
                        "Inventory_Value": "Inventory Value",
                    }
                )
                st.dataframe(display_excess, use_container_width=True, hide_index=True)
            else:
                st.success("No products currently in Excess Stock status.")

# -----------------------------------------------------------------------------
# PAGE 3: Supplier & Delivery
# -----------------------------------------------------------------------------
elif page_selection == "Supplier & Delivery":
    render_header("Vendor fulfillment, on-time delivery rates, and transit delay metrics")

    if f_deliveries.empty or f_suppliers.empty:
        st.warning("No data available for the selected filters.")
    else:
        sup_metrics_df = calculate_supplier_performance(f_suppliers, f_deliveries)

        # Top supplier benchmark indicators (Descriptive neutral labels)
        highest_ot = sup_metrics_df.sort_values(by="On_Time_Delivery_Percentage", ascending=False).iloc[0]
        lowest_ot = sup_metrics_df.sort_values(by="On_Time_Delivery_Percentage", ascending=True).iloc[0]
        highest_delay = sup_metrics_df.sort_values(by="Delayed_Deliveries", ascending=False).iloc[0]

        bench_cols = st.columns(3)
        render_kpi_card(
            bench_cols[0],
            "HIGHEST ON-TIME %",
            f"{highest_ot['On_Time_Delivery_Percentage']:.1f}%",
            f"{highest_ot['Supplier_Name']}",
        )
        render_kpi_card(
            bench_cols[1],
            "LOWEST ON-TIME %",
            f"{lowest_ot['On_Time_Delivery_Percentage']:.1f}%",
            f"{lowest_ot['Supplier_Name']}",
        )
        render_kpi_card(
            bench_cols[2],
            "HIGHEST DELAY COUNT",
            f"{highest_delay['Delayed_Deliveries']:,} orders",
            f"{highest_delay['Supplier_Name']}",
        )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        sup_c1, sup_c2 = st.columns(2)

        # Chart 1: Supplier On-Time Delivery
        with sup_c1:
            sorted_ot = sup_metrics_df.sort_values(by="On_Time_Delivery_Percentage", ascending=True)
            fig_ot = px.bar(
                sorted_ot,
                x="On_Time_Delivery_Percentage",
                y="Supplier_Name",
                orientation="h",
                color="On_Time_Delivery_Percentage",
                color_continuous_scale="Tealgrn",
            )
            apply_chart_layout(
                fig_ot,
                height=310,
                title=dict(text="Supplier On-Time Delivery", font=dict(size=13, color="#0F172A")),
                coloraxis_showscale=False,
                xaxis=dict(title="On-Time %", tickformat=".1f", ticksuffix="%", range=[60, 102]),
                yaxis=dict(title=None, automargin=True),
            )
            fig_ot.update_traces(hovertemplate="<b>%{y}</b><br>On-Time: %{x:.1f}%<extra></extra>")
            st.plotly_chart(fig_ot, use_container_width=True)

        # Chart 2: Average Delivery Delay
        with sup_c2:
            sorted_delay = sup_metrics_df.sort_values(by="Average_Delay_Days", ascending=True)
            fig_delay = px.bar(
                sorted_delay,
                x="Average_Delay_Days",
                y="Supplier_Name",
                orientation="h",
                color="Average_Delay_Days",
                color_continuous_scale="Reds",
            )
            apply_chart_layout(
                fig_delay,
                height=310,
                title=dict(text="Average Delivery Delay", font=dict(size=13, color="#0F172A")),
                coloraxis_showscale=False,
                xaxis=dict(title="Average Delay (Days)", tickformat=".1f"),
                yaxis=dict(title=None, automargin=True),
            )
            fig_delay.update_traces(hovertemplate="<b>%{y}</b><br>Average Delay: %{x:.1f} days<extra></extra>")
            st.plotly_chart(fig_delay, use_container_width=True)

        sup_c3, sup_c4 = st.columns(2)

        # Chart 3: Supplier Order Volume
        with sup_c3:
            sorted_vol = sup_metrics_df.sort_values(by="Total_Orders", ascending=False)
            fig_vol = px.bar(
                sorted_vol,
                x="Supplier_Name",
                y="Total_Orders",
                color_discrete_sequence=["#2563EB"],
            )
            apply_chart_layout(
                fig_vol,
                height=280,
                title=dict(text="Supplier Order Volume", font=dict(size=13, color="#0F172A")),
                xaxis=dict(title=None, tickangle=-45),
                yaxis=dict(title="Total Orders", tickformat="~s"),
            )
            fig_vol.update_traces(hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>")
            st.plotly_chart(fig_vol, use_container_width=True)

        # Chart 4: Monthly Delivery Delay Trend
        with sup_c4:
            deliv_trend = f_deliveries.copy()
            deliv_trend["Year_Month"] = deliv_trend["Order_Date"].dt.strftime("%Y-%m")
            monthly_deliv = deliv_trend.groupby("Year_Month").agg(
                Total_Orders=("Delivery_ID", "count"),
                Delayed_Orders=("Delivery_Status", lambda x: (x == "Delayed").sum()),
            ).reset_index()
            monthly_deliv["Delay_Rate"] = np.where(
                monthly_deliv["Total_Orders"] > 0,
                (monthly_deliv["Delayed_Orders"] / monthly_deliv["Total_Orders"] * 100).round(1),
                0.0,
            )

            fig_m_delay = px.line(
                monthly_deliv,
                x="Year_Month",
                y="Delay_Rate",
                markers=True,
                color_discrete_sequence=["#DC2626"],
            )
            apply_chart_layout(
                fig_m_delay,
                height=280,
                title=dict(text="Monthly Delivery Delay Trend", font=dict(size=13, color="#0F172A")),
                xaxis=dict(title=None, tickangle=-45),
                yaxis=dict(title="Delay Rate (%)", tickformat=".1f", ticksuffix="%"),
            )
            fig_m_delay.update_traces(line=dict(width=2), hovertemplate="<b>%{x}</b><br>Delay Rate: %{y:.1f}%<extra></extra>")
            st.plotly_chart(fig_m_delay, use_container_width=True)

        # Supplier Performance Table
        st.markdown("<div class='section-title'>Supplier Performance Matrix</div>", unsafe_allow_html=True)
        display_sup = sup_metrics_df.rename(
            columns={
                "Supplier_Name": "Supplier",
                "Total_Orders": "Orders",
                "Total_Quantity_Supplied": "Quantity Supplied",
                "On_Time_Delivery_Percentage": "On-Time %",
                "Delayed_Deliveries": "Delayed Orders",
                "Average_Delay_Days": "Average Delay (Days)",
                "Average_Supplier_Rating": "Supplier Rating",
            }
        )[["Supplier", "Orders", "Quantity Supplied", "On-Time %", "Delayed Orders", "Average Delay (Days)", "Supplier Rating"]]
        st.dataframe(display_sup, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# PAGE 4: Recommendations
# -----------------------------------------------------------------------------
elif page_selection == "Recommendations":
    render_header("Automated data-driven prescriptive actions and supply chain recommendations")

    if f_inventory.empty or f_products.empty or f_deliveries.empty or f_prod_inv.empty:
        st.warning("No data available for the selected filters.")
    else:
        inv_m = calculate_inventory_metrics(f_products, f_inventory)
        del_m = calculate_delivery_metrics(f_deliveries)
        sup_p = calculate_supplier_performance(f_suppliers, f_deliveries)
        stock_r = get_stockout_risk(f_products, f_inventory)
        excess_i = get_excess_inventory(f_products, f_inventory)

        recs = generate_recommendations(
            inventory_metrics=inv_m,
            delivery_metrics=del_m,
            supplier_performance=sup_p,
            stockout_risk=stock_r,
            excess_inventory=excess_i,
        )

        st.caption(f"{len(recs)} operational recommendations identified based on real calculated metrics:")

        severity_filter = st.selectbox(
            "Filter by Severity",
            options=["All Severities", "High", "Medium", "Low"],
            index=0,
        )

        filtered_recs = [
            r for r in recs if severity_filter == "All Severities" or r["Priority"].lower() == severity_filter.lower()
        ]

        if not filtered_recs:
            st.info("No recommendations match the chosen severity filter.")
        else:
            for r in filtered_recs:
                p_level = r["Priority"].lower()
                badge_class = f"badge-{p_level}" if p_level in ["high", "medium", "low"] else "badge-low"
                card_class = f"alert-{p_level}" if p_level in ["high", "medium", "low"] else "alert-low"

                st.markdown(
                    f"""
                    <div class="alert-card {card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="alert-badge {badge_class}">{r['Priority']} Priority</span>
                            <span style="font-size: 0.73rem; color: #64748B; font-weight: 600;">{r['Category']}</span>
                        </div>
                        <h4 style="margin: 4px 0 4px 0; font-size: 0.98rem; color: #0F172A;">{r['Target']}</h4>
                        <p style="margin: 0 0 4px 0; font-size: 0.85rem; color: #334155;"><b>Finding:</b> {r['Issue']}</p>
                        <p style="margin: 0; font-size: 0.85rem; color: #1E293B;"><b>Recommended Action:</b> {r['Recommendation']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        Supply Chain & Inventory Analytics | Big Data Analytics Project
    </div>
    """,
    unsafe_allow_html=True,
)
