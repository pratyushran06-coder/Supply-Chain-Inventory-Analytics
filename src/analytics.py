"""
Analytics & Metrics Computation Module
Part of Supply-Chain-Inventory-Analytics

Provides reusable analytical functions across:
- Ingestion and date parsing (load_data)
- Inventory health & KPIs (calculate_inventory_metrics, calculate_product_inventory)
- Logistics & delivery reliability (calculate_delivery_metrics)
- Vendor performance evaluations (calculate_supplier_performance)
- Procurement spending patterns (calculate_purchase_metrics)
- Risk identification (get_stockout_risk, get_excess_inventory)
- Data-driven business recommendations (generate_recommendations)
"""

import os
from typing import Tuple, Dict, Any, List
import numpy as np
import pandas as pd


def _resolve_data_dir(data_dir: str | None = None) -> str:
    """Helper to locate the data directory reliably whether called directly or imported."""
    if data_dir and os.path.exists(data_dir):
        return os.path.abspath(data_dir)

    # Check relative to this script: ../data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, "..", "data")
    if os.path.exists(candidate):
        return os.path.abspath(candidate)

    # Check current working directory: ./data
    cwd_candidate = os.path.abspath("data")
    if os.path.exists(cwd_candidate):
        return cwd_candidate

    raise FileNotFoundError(f"Could not locate 'data/' directory. Tried: {candidate} and {cwd_candidate}")


def load_data(data_dir: str | None = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all five supply chain CSV files with appropriate date parsing.

    Returns:
        tuple of (df_products, df_suppliers, df_purchases, df_deliveries, df_inventory)
    """
    base_dir = _resolve_data_dir(data_dir)

    df_products = pd.read_csv(os.path.join(base_dir, "products.csv"))
    df_suppliers = pd.read_csv(os.path.join(base_dir, "suppliers.csv"))

    # Purchases with date parsing
    df_purchases = pd.read_csv(
        os.path.join(base_dir, "purchases.csv"),
        parse_dates=["Purchase_Date"],
    )

    # Deliveries with date parsing
    df_deliveries = pd.read_csv(
        os.path.join(base_dir, "deliveries.csv"),
        parse_dates=["Order_Date", "Expected_Date", "Actual_Date"],
    )

    # Inventory with date parsing
    df_inventory = pd.read_csv(
        os.path.join(base_dir, "inventory.csv"),
        parse_dates=["Date"],
    )

    return df_products, df_suppliers, df_purchases, df_deliveries, df_inventory


def calculate_product_inventory(
    df_products: pd.DataFrame,
    df_inventory: pd.DataFrame,
    planning_days: int = 60,
) -> pd.DataFrame:
    """
    Calculates detailed inventory metrics for every individual product using a demand-based rule.

    Demand-Based Stock Status Determination:
    1. Average Daily Demand:
       Average_Daily_Demand = Total_Sold / Number_of_Inventory_Days
       (Calculated across all historical recorded days in the inventory dataset).

    2. Target Stock Level (Planning Horizon Buffer):
       Target_Stock_Level = Average_Daily_Demand * planning_days
       (Represents a healthy forward-looking operational buffer of 60 days of demand).

    3. Classification Rules:
       - 'Low Stock':
         Latest_Closing_Stock <= Reorder_Level
         (The stock has reached or fallen below the safety replenishment point, posing stockout risk).
       - 'Excess Stock':
         Latest_Closing_Stock > Target_Stock_Level
         (The current inventory exceeds the 60-day planned demand horizon, locking up excessive capital).
       - 'Normal':
         Reorder_Level < Latest_Closing_Stock <= Target_Stock_Level
         (Stock is comfortably buffered within standard operational planning boundaries).

    Returns:
        pd.DataFrame containing:
        - Product_ID
        - Product_Name
        - Category
        - Unit_Cost
        - Reorder_Level
        - Latest_Closing_Stock
        - Total_Sold
        - Total_Received
        - Average_Daily_Demand
        - Target_Stock_Level
        - Inventory_Value
        - Stock_Status
    """
    total_days = max(1, df_inventory["Date"].nunique())

    latest_date = df_inventory["Date"].max()
    latest_stock = df_inventory[df_inventory["Date"] == latest_date][
        ["Product_ID", "Closing_Stock"]
    ].rename(columns={"Closing_Stock": "Latest_Closing_Stock"})

    total_sold = df_inventory.groupby("Product_ID")["Sold"].sum().reset_index().rename(
        columns={"Sold": "Total_Sold"}
    )
    total_received = df_inventory.groupby("Product_ID")["Received"].sum().reset_index().rename(
        columns={"Received": "Total_Received"}
    )

    merged = df_products.copy()
    merged = pd.merge(merged, latest_stock, on="Product_ID", how="left")
    merged = pd.merge(merged, total_sold, on="Product_ID", how="left")
    merged = pd.merge(merged, total_received, on="Product_ID", how="left")

    # Fill NA if any
    merged["Latest_Closing_Stock"] = merged["Latest_Closing_Stock"].fillna(0).astype(int)
    merged["Total_Sold"] = merged["Total_Sold"].fillna(0).astype(int)
    merged["Total_Received"] = merged["Total_Received"].fillna(0).astype(int)

    # Calculate demand-based metrics
    merged["Average_Daily_Demand"] = (merged["Total_Sold"] / total_days).round(2)
    merged["Target_Stock_Level"] = (merged["Average_Daily_Demand"] * planning_days).round(2)

    # Inventory Value = Latest Closing_Stock * Unit_Cost
    merged["Inventory_Value"] = (merged["Latest_Closing_Stock"] * merged["Unit_Cost"]).round(2)

    # Stock Status Classification
    def _classify_status(row):
        if row["Latest_Closing_Stock"] <= row["Reorder_Level"]:
            return "Low Stock"
        elif row["Latest_Closing_Stock"] > row["Target_Stock_Level"]:
            return "Excess Stock"
        else:
            return "Normal"

    merged["Stock_Status"] = merged.apply(_classify_status, axis=1)

    column_order = [
        "Product_ID",
        "Product_Name",
        "Category",
        "Unit_Cost",
        "Reorder_Level",
        "Latest_Closing_Stock",
        "Total_Sold",
        "Total_Received",
        "Average_Daily_Demand",
        "Target_Stock_Level",
        "Inventory_Value",
        "Stock_Status",
    ]

    return merged[column_order]


def calculate_inventory_metrics(
    df_products: pd.DataFrame,
    df_inventory: pd.DataFrame,
    planning_days: int = 60,
) -> Dict[str, Any]:
    """
    Calculate portfolio-level inventory metrics across all products using the demand-based rule.

    Returns dictionary containing:
    - total_current_inventory: Total units in stock on the latest date
    - total_inventory_value: Total dollar value of current inventory
    - products_at_or_below_reorder: Count of products with Low Stock status
    - excess_inventory_products: Count of products with Excess Stock status
    - normal_inventory_products: Count of products with Normal status
    - average_inventory: Average current stock per product
    - total_units_sold: Cumulative units sold across the full history
    - total_units_received: Cumulative units received into inventory
    """
    prod_inv = calculate_product_inventory(df_products, df_inventory, planning_days=planning_days)

    total_current_inventory = int(prod_inv["Latest_Closing_Stock"].sum())
    total_inventory_value = round(float(prod_inv["Inventory_Value"].sum()), 2)
    products_at_or_below_reorder = int((prod_inv["Stock_Status"] == "Low Stock").sum())
    excess_inventory_products = int((prod_inv["Stock_Status"] == "Excess Stock").sum())
    normal_inventory_products = int((prod_inv["Stock_Status"] == "Normal").sum())
    average_inventory = round(float(prod_inv["Latest_Closing_Stock"].mean()), 2)

    total_units_sold = int(df_inventory["Sold"].sum())
    total_units_received = int(df_inventory["Received"].sum())

    return {
        "total_current_inventory": total_current_inventory,
        "total_inventory_value": total_inventory_value,
        "products_at_or_below_reorder": products_at_or_below_reorder,
        "excess_inventory_products": excess_inventory_products,
        "normal_inventory_products": normal_inventory_products,
        "average_inventory": average_inventory,
        "total_units_sold": total_units_sold,
        "total_units_received": total_units_received,
    }


def calculate_delivery_metrics(df_deliveries: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate logistics and delivery performance metrics.
    Calculates actual delay days using Expected_Date and Actual_Date.

    Returns dictionary containing:
    - total_deliveries: Total count of delivery records
    - on_time_deliveries: Total on-time or early deliveries
    - delayed_deliveries: Total delayed deliveries
    - on_time_delivery_percentage: % of deliveries on-time
    - delayed_delivery_percentage: % of deliveries delayed
    - average_delivery_delay_days: Average delay days for delayed orders
    - average_delivery_delay_overall: Average delay days across all shipments (non-negative)
    - max_delivery_delay: Maximum delay observed in days
    """
    total_deliveries = len(df_deliveries)
    if total_deliveries == 0:
        return {
            "total_deliveries": 0,
            "on_time_deliveries": 0,
            "delayed_deliveries": 0,
            "on_time_delivery_percentage": 0.0,
            "delayed_delivery_percentage": 0.0,
            "average_delivery_delay_days": 0.0,
            "average_delivery_delay_overall": 0.0,
            "max_delivery_delay": 0,
        }

    # Delay in days = (Actual_Date - Expected_Date)
    delay_days = (df_deliveries["Actual_Date"] - df_deliveries["Expected_Date"]).dt.days

    on_time_mask = delay_days <= 0
    delayed_mask = delay_days > 0

    on_time_deliveries = int(on_time_mask.sum())
    delayed_deliveries = int(delayed_mask.sum())

    on_time_pct = round((on_time_deliveries / total_deliveries) * 100, 2)
    delayed_pct = round((delayed_deliveries / total_deliveries) * 100, 2)

    # Average delay among delayed orders
    avg_delay_delayed = round(float(delay_days[delayed_mask].mean()), 2) if delayed_deliveries > 0 else 0.0

    # Average delay across all orders (treating early shipments as 0 days delayed)
    avg_delay_overall = round(float(np.maximum(0, delay_days).mean()), 2)

    max_delay = int(delay_days.max())

    return {
        "total_deliveries": total_deliveries,
        "on_time_deliveries": on_time_deliveries,
        "delayed_deliveries": delayed_deliveries,
        "on_time_delivery_percentage": on_time_pct,
        "delayed_delivery_percentage": delayed_pct,
        "average_delivery_delay_days": avg_delay_delayed,
        "average_delivery_delay_overall": avg_delay_overall,
        "max_delivery_delay": max_delay,
    }


def calculate_supplier_performance(
    df_suppliers: pd.DataFrame,
    df_deliveries: pd.DataFrame,
) -> pd.DataFrame:
    """
    Evaluates historical delivery reliability and performance for each supplier.

    Returns pd.DataFrame with:
    - Supplier_ID
    - Supplier_Name
    - Total_Orders
    - Total_Quantity_Supplied
    - On_Time_Deliveries
    - Delayed_Deliveries
    - On_Time_Delivery_Percentage
    - Average_Delay_Days
    - Average_Supplier_Rating
    """
    deliv = df_deliveries.copy()
    delay_days = (deliv["Actual_Date"] - deliv["Expected_Date"]).dt.days
    deliv["_Delay_Days"] = delay_days
    deliv["_Is_On_Time"] = delay_days <= 0
    deliv["_Is_Delayed"] = delay_days > 0
    deliv["_Delay_Positive"] = np.maximum(0, delay_days)

    grouped = deliv.groupby("Supplier_ID").agg(
        Total_Orders=("Delivery_ID", "count"),
        Total_Quantity_Supplied=("Quantity", "sum"),
        On_Time_Deliveries=("_Is_On_Time", "sum"),
        Delayed_Deliveries=("_Is_Delayed", "sum"),
        Average_Delay_Days=("_Delay_Positive", "mean"),
    ).reset_index()

    perf = pd.merge(df_suppliers, grouped, on="Supplier_ID", how="left")
    perf["Total_Orders"] = perf["Total_Orders"].fillna(0).astype(int)
    perf["Total_Quantity_Supplied"] = perf["Total_Quantity_Supplied"].fillna(0).astype(int)
    perf["On_Time_Deliveries"] = perf["On_Time_Deliveries"].fillna(0).astype(int)
    perf["Delayed_Deliveries"] = perf["Delayed_Deliveries"].fillna(0).astype(int)

    perf["On_Time_Delivery_Percentage"] = np.where(
        perf["Total_Orders"] > 0,
        (perf["On_Time_Deliveries"] / perf["Total_Orders"] * 100).round(2),
        0.0,
    )
    perf["Average_Delay_Days"] = perf["Average_Delay_Days"].fillna(0.0).round(2)
    perf.rename(columns={"Rating": "Average_Supplier_Rating"}, inplace=True)

    columns_order = [
        "Supplier_ID",
        "Supplier_Name",
        "Total_Orders",
        "Total_Quantity_Supplied",
        "On_Time_Deliveries",
        "Delayed_Deliveries",
        "On_Time_Delivery_Percentage",
        "Average_Delay_Days",
        "Average_Supplier_Rating",
    ]

    return perf[columns_order].sort_values(by="On_Time_Delivery_Percentage", ascending=False).reset_index(drop=True)


def calculate_purchase_metrics(df_purchases: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate procurement spending and order volume metrics.

    Returns dictionary containing:
    - total_purchase_spend: Sum of all purchase order values
    - total_purchase_quantity: Sum of all ordered units
    - average_purchase_cost: Average spend per purchase order
    - monthly_purchase_spend: pd.DataFrame with monthly spend trend
    - monthly_purchase_quantity: pd.DataFrame with monthly order quantity trend
    """
    total_spend = round(float(df_purchases["Total_Cost"].sum()), 2)
    total_quantity = int(df_purchases["Quantity"].sum())
    avg_cost = round(float(df_purchases["Total_Cost"].mean()), 2)

    purch = df_purchases.copy()
    purch["Year_Month"] = purch["Purchase_Date"].dt.strftime("%Y-%m")

    monthly_summary = purch.groupby("Year_Month").agg(
        Monthly_Spend=("Total_Cost", "sum"),
        Monthly_Quantity=("Quantity", "sum"),
        Order_Count=("Purchase_ID", "count"),
    ).reset_index().sort_values("Year_Month")

    monthly_summary["Monthly_Spend"] = monthly_summary["Monthly_Spend"].round(2)

    monthly_spend_df = monthly_summary[["Year_Month", "Monthly_Spend"]].rename(
        columns={"Monthly_Spend": "Spend"}
    )
    monthly_quantity_df = monthly_summary[["Year_Month", "Monthly_Quantity"]].rename(
        columns={"Monthly_Quantity": "Quantity"}
    )

    return {
        "total_purchase_spend": total_spend,
        "total_purchase_quantity": total_quantity,
        "average_purchase_cost": avg_cost,
        "monthly_purchase_spend": monthly_spend_df,
        "monthly_purchase_quantity": monthly_quantity_df,
    }


def get_stockout_risk(
    df_products: pd.DataFrame,
    df_inventory: pd.DataFrame,
    planning_days: int = 60,
) -> pd.DataFrame:
    """
    Identifies products whose latest closing stock is at or below their reorder level.

    Returns pd.DataFrame with columns:
    - Product_ID
    - Product_Name
    - Category
    - Current_Stock
    - Reorder_Level
    - Stock_Gap (Reorder_Level - Current_Stock)
    - Risk_Level ('High' if Current_Stock <= 50% of Reorder_Level, else 'Medium')
    """
    prod_inv = calculate_product_inventory(df_products, df_inventory, planning_days=planning_days)
    low_stock = prod_inv[prod_inv["Latest_Closing_Stock"] <= prod_inv["Reorder_Level"]].copy()

    low_stock["Current_Stock"] = low_stock["Latest_Closing_Stock"]
    low_stock["Stock_Gap"] = low_stock["Reorder_Level"] - low_stock["Current_Stock"]

    def _risk_level(row):
        if row["Current_Stock"] <= 0.5 * row["Reorder_Level"]:
            return "High"
        return "Medium"

    low_stock["Risk_Level"] = low_stock.apply(_risk_level, axis=1)

    result_cols = [
        "Product_ID",
        "Product_Name",
        "Category",
        "Current_Stock",
        "Reorder_Level",
        "Stock_Gap",
        "Risk_Level",
    ]
    return low_stock[result_cols].sort_values(by="Stock_Gap", ascending=False).reset_index(drop=True)


def get_excess_inventory(
    df_products: pd.DataFrame,
    df_inventory: pd.DataFrame,
    planning_days: int = 60,
) -> pd.DataFrame:
    """
    Identifies products with excess inventory using the demand-based rule:
    - Average_Daily_Demand = Total_Sold / Number_of_Inventory_Days
    - Target_Stock_Level = Average_Daily_Demand * planning_days (default: 60 days)
    - Excess stock is defined as Latest_Closing_Stock > Target_Stock_Level.
    - Estimated_Excess_Quantity = Current_Stock - Target_Stock_Level

    Only includes products classified as Excess Stock.

    Returns pd.DataFrame with columns:
    - Product_ID
    - Product_Name
    - Category
    - Current_Stock
    - Target_Stock_Level
    - Estimated_Excess_Quantity
    - Inventory_Value
    """
    prod_inv = calculate_product_inventory(df_products, df_inventory, planning_days=planning_days)
    excess_stock = prod_inv[prod_inv["Stock_Status"] == "Excess Stock"].copy()

    excess_stock["Current_Stock"] = excess_stock["Latest_Closing_Stock"]
    excess_stock["Estimated_Excess_Quantity"] = (
        excess_stock["Current_Stock"] - excess_stock["Target_Stock_Level"]
    ).round(2)

    result_cols = [
        "Product_ID",
        "Product_Name",
        "Category",
        "Current_Stock",
        "Target_Stock_Level",
        "Estimated_Excess_Quantity",
        "Inventory_Value",
    ]
    return excess_stock[result_cols].sort_values(by="Estimated_Excess_Quantity", ascending=False).reset_index(drop=True)


def generate_recommendations(
    inventory_metrics: Dict[str, Any] | None = None,
    delivery_metrics: Dict[str, Any] | None = None,
    supplier_performance: pd.DataFrame | None = None,
    stockout_risk: pd.DataFrame | None = None,
    excess_inventory: pd.DataFrame | None = None,
    data_dir: str | None = None,
    planning_days: int = 60,
) -> List[Dict[str, str]]:
    """
    Generates actionable, data-driven business recommendations based on calculated supply chain metrics.

    All recommendations are dynamically generated using computed values rather than static text:
    - Stockout Risk: Prompts replenishment orders for SKUs below safety thresholds.
    - Excess Inventory: Identifies SKUs tying up capital beyond the 60-day demand target.
    - Supplier Delays: Pinpoints unreliable suppliers based on on-time delivery percentages and delay days.
    - Logistics Lead Times: Recommends ERP lead-time recalibration if delivery delays exceed thresholds.
    """
    # Auto-load and compute if any arguments are omitted
    if (
        inventory_metrics is None
        or delivery_metrics is None
        or supplier_performance is None
        or stockout_risk is None
        or excess_inventory is None
    ):
        p, s, pur, d, inv = load_data(data_dir)
        inventory_metrics = calculate_inventory_metrics(p, inv, planning_days=planning_days)
        delivery_metrics = calculate_delivery_metrics(d)
        supplier_performance = calculate_supplier_performance(s, d)
        stockout_risk = get_stockout_risk(p, inv, planning_days=planning_days)
        excess_inventory = get_excess_inventory(p, inv, planning_days=planning_days)

    recommendations: List[Dict[str, str]] = []

    # 1. Stockout & Replenishment Recommendations
    if not stockout_risk.empty:
        for _, row in stockout_risk.iterrows():
            reorder_qty = int(row["Stock_Gap"] + row["Reorder_Level"])
            recommendations.append({
                "Category": "Replenishment & Safety Stock",
                "Priority": row["Risk_Level"],
                "Target": f"{row['Product_Name']} ({row['Product_ID']})",
                "Issue": (
                    f"Stockout Risk Detected: Current stock ({row['Current_Stock']:,} units) is below "
                    f"reorder level ({row['Reorder_Level']:,} units) with a gap of {row['Stock_Gap']:,} units."
                ),
                "Recommendation": (
                    f"Place immediate replenishment order of approximately {reorder_qty:,} units "
                    f"to rebuild safe buffer stock."
                ),
            })
    else:
        recommendations.append({
            "Category": "Replenishment & Safety Stock",
            "Priority": "Low",
            "Target": "All Products",
            "Issue": "Zero products currently below their configured reorder level.",
            "Recommendation": "Maintain current reorder schedules and monitor daily sales velocities.",
        })

    # 2. Excess Inventory Recommendations (60-day demand planning horizon)
    if not excess_inventory.empty:
        top_excess = excess_inventory.head(3)
        for _, row in top_excess.iterrows():
            recommendations.append({
                "Category": "Excess Stock Optimization",
                "Priority": "Medium",
                "Target": f"{row['Product_Name']} ({row['Product_ID']})",
                "Issue": (
                    f"Surplus Stock Identified: Holding {row['Current_Stock']:,} units vs 60-day target "
                    f"of {row['Target_Stock_Level']:,.1f} units (estimated excess: {row['Estimated_Excess_Quantity']:,.1f} "
                    f"units, tied-up capital: ${row['Inventory_Value']:,.2f})."
                ),
                "Recommendation": (
                    f"Temporarily pause or scale down purchase order quantities for {row['Product_Name']} "
                    f"until inventory normalizes toward the 60-day target level."
                ),
            })

    # 3. Supplier Performance & SLA Reviews
    if not supplier_performance.empty:
        poor_suppliers = supplier_performance[
            supplier_performance["On_Time_Delivery_Percentage"] < 85.0
        ].sort_values(by="On_Time_Delivery_Percentage", ascending=True)

        for _, sup in poor_suppliers.head(3).iterrows():
            recommendations.append({
                "Category": "Supplier Performance Review",
                "Priority": "High" if sup["On_Time_Delivery_Percentage"] < 75.0 else "Medium",
                "Target": f"{sup['Supplier_Name']} ({sup['Supplier_ID']})",
                "Issue": (
                    f"Sub-par Delivery Performance: On-time delivery rate is {sup['On_Time_Delivery_Percentage']:.1f}% "
                    f"with {int(sup['Delayed_Deliveries']):,} delayed deliveries (average delay: {sup['Average_Delay_Days']:.1f} days)."
                ),
                "Recommendation": (
                    f"Initiate formal vendor review with {sup['Supplier_Name']}. Establish strict SLA delivery "
                    f"commitments, delay penalty terms, or onboard alternative backup suppliers."
                ),
            })

    # 4. Logistics & ERP Lead-Time Calibration
    delayed_pct = delivery_metrics.get("delayed_delivery_percentage", 0.0)
    avg_delay = delivery_metrics.get("average_delivery_delay_days", 0.0)
    max_delay = delivery_metrics.get("max_delivery_delay", 0)

    if delayed_pct > 10.0:
        recommendations.append({
            "Category": "Lead Time Calibration",
            "Priority": "Medium",
            "Target": "Procurement & ERP Lead Times",
            "Issue": (
                f"Systemic Delivery Delays: {delayed_pct:.1f}% of all deliveries experienced delays, "
                f"averaging {avg_delay:.1f} days of delay with peak delay reaching {max_delay} days."
            ),
            "Recommendation": (
                "Adjust safety lead-time buffers in master planning by +3 to +5 days across frequent delay "
                "routes to prevent operational stockouts during peak ordering."
            ),
        })

    # 5. Top Supplier Strategic Partnership
    if not supplier_performance.empty:
        top_sup = supplier_performance.iloc[0]
        if top_sup["On_Time_Delivery_Percentage"] >= 90.0:
            recommendations.append({
                "Category": "Strategic Vendor Partnerships",
                "Priority": "Low",
                "Target": f"{top_sup['Supplier_Name']} ({top_sup['Supplier_ID']})",
                "Issue": (
                    f"Exemplary Reliability: Highest on-time delivery rate ({top_sup['On_Time_Delivery_Percentage']:.1f}%) "
                    f"across {int(top_sup['Total_Orders']):,} total purchase orders."
                ),
                "Recommendation": (
                    f"Consolidate procurement volume with {top_sup['Supplier_Name']} and negotiate long-term "
                    f"preferred pricing agreements."
                ),
            })

    return recommendations


def run_all_analytics(data_dir: str | None = None, planning_days: int = 60) -> Dict[str, Any]:
    """
    Executes the major analytics functions and returns the aggregated results
    in a structured dictionary suitable for testing and Streamlit dashboard integration.
    """
    df_products, df_suppliers, df_purchases, df_deliveries, df_inventory = load_data(data_dir)

    product_inventory = calculate_product_inventory(df_products, df_inventory, planning_days=planning_days)
    inventory_metrics = calculate_inventory_metrics(df_products, df_inventory, planning_days=planning_days)
    delivery_metrics = calculate_delivery_metrics(df_deliveries)
    supplier_performance = calculate_supplier_performance(df_suppliers, df_deliveries)
    purchase_metrics = calculate_purchase_metrics(df_purchases)
    stockout_risk = get_stockout_risk(df_products, df_inventory, planning_days=planning_days)
    excess_inventory = get_excess_inventory(df_products, df_inventory, planning_days=planning_days)
    recommendations = generate_recommendations(
        inventory_metrics=inventory_metrics,
        delivery_metrics=delivery_metrics,
        supplier_performance=supplier_performance,
        stockout_risk=stockout_risk,
        excess_inventory=excess_inventory,
        planning_days=planning_days,
    )

    return {
        "products": df_products,
        "suppliers": df_suppliers,
        "purchases": df_purchases,
        "deliveries": df_deliveries,
        "inventory": df_inventory,
        "product_inventory": product_inventory,
        "inventory_metrics": inventory_metrics,
        "delivery_metrics": delivery_metrics,
        "supplier_performance": supplier_performance,
        "purchase_metrics": purchase_metrics,
        "stockout_risk": stockout_risk,
        "excess_inventory": excess_inventory,
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    results = run_all_analytics()

    inv_m = results["inventory_metrics"]
    del_m = results["delivery_metrics"]
    pur_m = results["purchase_metrics"]
    sup_df = results["supplier_performance"]
    prod_df = results["product_inventory"]
    excess_df = results["excess_inventory"]

    print("\n" + "=" * 68)
    print("      SUPPLY CHAIN & INVENTORY ANALYTICS - SUMMARY REPORT")
    print("=" * 68)
    print(f"Total inventory                   : {inv_m['total_current_inventory']:,} units")
    print(f"Inventory value                   : ${inv_m['total_inventory_value']:,.2f}")
    print(f"Total units sold                  : {inv_m['total_units_sold']:,} units")
    print(f"Total deliveries                  : {del_m['total_deliveries']:,}")
    print(f"On-time delivery %                : {del_m['on_time_delivery_percentage']:.2f}%")
    print(f"Delayed deliveries                : {del_m['delayed_deliveries']:,}")
    print(f"Total purchase spend              : ${pur_m['total_purchase_spend']:,.2f}")
    print(f"Number of low-stock products      : {inv_m['products_at_or_below_reorder']}")
    print(f"Number of excess-stock products   : {inv_m['excess_inventory_products']}")
    print(f"Number of normal-stock products   : {inv_m['normal_inventory_products']}")
    print("=" * 68)

    print("\n--- TOP 5 SUPPLIERS BY ON-TIME DELIVERY % ---")
    top_5_suppliers = sup_df.head(5)[
        ["Supplier_ID", "Supplier_Name", "Total_Orders", "On_Time_Delivery_Percentage", "Average_Delay_Days", "Average_Supplier_Rating"]
    ]
    print(top_5_suppliers.to_string(index=False))

    print("\n--- TOP 5 PRODUCTS BY INVENTORY VALUE ---")
    top_5_products = prod_df.sort_values(by="Inventory_Value", ascending=False).head(5)[
        ["Product_ID", "Product_Name", "Category", "Latest_Closing_Stock", "Unit_Cost", "Inventory_Value", "Stock_Status"]
    ]
    print(top_5_products.to_string(index=False))

    print("\n--- TOP 5 EXCESS-INVENTORY PRODUCTS ---")
    top_5_excess = excess_df.head(5)[
        ["Product_ID", "Product_Name", "Category", "Current_Stock", "Target_Stock_Level", "Estimated_Excess_Quantity", "Inventory_Value"]
    ]
    print(top_5_excess.to_string(index=False))
    print("=" * 68 + "\n")
