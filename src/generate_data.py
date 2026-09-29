"""
Data Generation Script for Supply Chain & Inventory Analytics
Generates realistic, reproducible synthetic data across 5 core entities:
1. products.csv
2. suppliers.csv
3. purchases.csv
4. deliveries.csv
5. inventory.csv
"""

import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def set_seed(seed: int = 42):
    """Set random seed for reproducibility."""
    np.random.seed(seed)


def generate_products() -> pd.DataFrame:
    """Generate 50 realistic products across diverse categories."""
    categories_spec = [
        (
            "Electronics & Components",
            [
                ("Microcontroller MCU-32", 18.50, 150, 14, "Fast-Moving"),
                ("Lithium-Ion Battery Cell 3.7V", 6.20, 400, 12, "Fast-Moving"),
                ("Industrial PCB Motherboard", 85.00, 50, 21, "Medium-Moving"),
                ("Capacitor Assortment Pack 100uF", 3.40, 500, 10, "Fast-Moving"),
                ("Thermal Heat Sink 50mm", 7.80, 250, 8, "Medium-Moving"),
                ("High-Speed Fiber Optic Transceiver", 120.00, 30, 25, "Slow-Moving"),
                ("Power Inverter Module 500W", 65.50, 60, 18, "Medium-Moving"),
                ("Step-Down Voltage Regulator IC", 2.10, 800, 7, "Fast-Moving"),
                ("OLED Graphic Display Panel 2.4in", 24.00, 120, 15, "Medium-Moving"),
                ("Precision Brushless DC Motor", 45.00, 80, 20, "Medium-Moving"),
            ],
        ),
        (
            "Mechanical & Industrial Tools",
            [
                ("Heavy-Duty Ball Bearing 6205-2RS", 12.50, 300, 10, "Fast-Moving"),
                ("Hydraulic Pressure Relief Valve", 110.00, 40, 22, "Slow-Moving"),
                ("Cast Iron V-Belt Pulley 120mm", 32.00, 90, 14, "Medium-Moving"),
                ("Tungsten Carbide CNC Drill Bit Set", 75.00, 70, 16, "Medium-Moving"),
                ("Stainless Steel Flange DN50", 42.50, 85, 15, "Medium-Moving"),
                ("Pneumatic Air Cylinder 50x100mm", 58.00, 55, 18, "Medium-Moving"),
                ("Industrial Timing Belt HTD-8M", 19.80, 180, 9, "Fast-Moving"),
                ("High-Torque Planetary Gearbox", 240.00, 20, 28, "Slow-Moving"),
                ("Linear Motion Guide Rail 1000mm", 95.00, 35, 24, "Slow-Moving"),
                ("Brass Gate Valve 1-Inch", 26.50, 110, 12, "Medium-Moving"),
            ],
        ),
        (
            "Raw Materials & Chemicals",
            [
                ("High-Density Polyethylene Granules (25kg)", 48.00, 200, 11, "Fast-Moving"),
                ("Industrial Synthetic Lubricant ISO 68 (20L)", 92.00, 60, 14, "Medium-Moving"),
                ("Epoxy Resin Hardener Blend (10kg)", 64.00, 80, 15, "Medium-Moving"),
                ("Aluminum Alloy Ingot 6061 (kg)", 5.20, 600, 12, "Fast-Moving"),
                ("Silicone Thermal Conductive Paste (1kg)", 35.00, 90, 8, "Medium-Moving"),
                ("Sulfuric Acid Technical Grade 98% (30L)", 55.00, 45, 16, "Slow-Moving"),
                ("Cold Rolled Steel Coil Strip (50m)", 140.00, 30, 20, "Slow-Moving"),
                ("Titanium Dioxide White Pigment (25kg)", 88.00, 50, 18, "Slow-Moving"),
                ("Compressed Argon Shielding Gas Cylinder", 115.00, 40, 10, "Medium-Moving"),
                ("Copper Wire Spool 1.5mm 100m", 72.00, 100, 14, "Fast-Moving"),
            ],
        ),
        (
            "Packaging Materials",
            [
                ("Heavy-Duty Corrugated Box 5-Ply (Bundle 50)", 38.50, 350, 7, "Fast-Moving"),
                ("Biodegradable Air Bubble Wrap 50m Roll", 22.00, 280, 6, "Fast-Moving"),
                ("Industrial Stretch Film Wrap 500mm", 16.50, 450, 5, "Fast-Moving"),
                ("Reinforced Gummed Paper Tape (Box 12)", 28.00, 200, 8, "Fast-Moving"),
                ("Pallet Thermal Insulated Cover", 45.00, 75, 12, "Medium-Moving"),
                ("Anti-Static ESD Shielding Bags (Pack 500)", 32.00, 160, 9, "Medium-Moving"),
                ("High-Impact Corner Edge Protectors (100pk)", 18.00, 300, 7, "Fast-Moving"),
                ("Molded Pulp Cushion Trays (Pack 200)", 25.00, 190, 10, "Medium-Moving"),
                ("Desiccant Silica Gel Packets 50g (Pack 100)", 14.50, 240, 6, "Fast-Moving"),
                ("Barcoded Shipping Thermal Labels (4x6 Roll)", 12.00, 500, 5, "Fast-Moving"),
            ],
        ),
        (
            "Office & Facility Supplies",
            [
                ("Ergonomic Industrial Anti-Fatigue Mat", 54.00, 40, 14, "Slow-Moving"),
                ("Commercial HEPA Air Filter Cartridge", 68.00, 50, 15, "Medium-Moving"),
                ("Heavy-Duty Nitrile Safety Gloves (Box 100)", 15.50, 350, 7, "Fast-Moving"),
                ("LED High-Bay Industrial Fixture 150W", 82.00, 45, 18, "Slow-Moving"),
                ("Digital Laser Non-Contact Thermometer", 36.00, 70, 10, "Medium-Moving"),
                ("High-Visibility Safety Vests Class 2 (Pack 10)", 29.00, 120, 8, "Medium-Moving"),
                ("Spill Containment Absorbent Booms (Pack 4)", 78.00, 35, 16, "Slow-Moving"),
                ("Industrial Hand Sanitizer Dispenser Refill (4L)", 21.00, 180, 8, "Fast-Moving"),
                ("RFID Warehouse Scanner Handheld Terminal", 380.00, 15, 28, "Slow-Moving"),
                ("First Aid Emergency Trauma Kit Wall-Mount", 95.00, 30, 14, "Slow-Moving"),
            ],
        ),
    ]

    products = []
    p_id = 1
    for cat_name, items in categories_spec:
        for name, cost, reorder_lvl, lead_time, velocity in items:
            products.append({
                "Product_ID": f"P{p_id:03d}",
                "Product_Name": name,
                "Category": cat_name,
                "Unit_Cost": round(float(cost), 2),
                "Reorder_Level": int(reorder_lvl),
                "Lead_Time_Days": int(lead_time),
                "_Velocity": velocity,
            })
            p_id += 1

    return pd.DataFrame(products)


def generate_suppliers() -> pd.DataFrame:
    """Generate 15 realistic suppliers with ratings and locations."""
    supplier_data = [
        ("SUP01", "Apex Logistics & Components", "Chicago, IL, USA", 4.8),
        ("SUP02", "Nexis Global Electronics Corp", "Shenzhen, Guangdong, CN", 4.6),
        ("SUP03", "Titan Industrial Machine Parts", "Detroit, MI, USA", 4.2),
        ("SUP04", "Vanguard Raw Materials Ltd", "Houston, TX, USA", 3.8),
        ("SUP05", "OmniPack Sustainable Packaging", "Columbus, OH, USA", 4.5),
        ("SUP06", "Stuttgart Precision Engineering", "Stuttgart, Baden-Wurttemberg, DE", 4.9),
        ("SUP07", "Pacific Basin Chemical & Polymers", "Incheon, Gyeonggi, KR", 3.5),
        ("SUP08", "Frontier Industrial Tools Co", "Monterrey, Nuevo Leon, MX", 4.1),
        ("SUP09", "EcoFiber & Box Packaging Co", "Atlanta, GA, USA", 3.9),
        ("SUP10", "Keystone Heavy Hydraulics Inc", "Pittsburgh, PA, USA", 3.2),
        ("SUP11", "Tokyo Micro-Sensing Systems", "Tokyo, Kanto, JP", 4.7),
        ("SUP12", "Delta Facility Safety & MRO", "Indianapolis, IN, USA", 4.4),
        ("SUP13", "Summit Alloy & Metallurgy Group", "Cleveland, OH, USA", 3.6),
        ("SUP14", "Alliance Global Freight & Stock", "Rotterdam, South Holland, NL", 4.0),
        ("SUP15", "RapidSource Industrial Supply", "Dallas, TX, USA", 3.1),
    ]

    suppliers = []
    for s_id, name, loc, rating in supplier_data:
        suppliers.append({
            "Supplier_ID": s_id,
            "Supplier_Name": name,
            "Location": loc,
            "Rating": float(rating),
        })

    return pd.DataFrame(suppliers)


def generate_purchases_and_deliveries(
    df_products: pd.DataFrame,
    df_suppliers: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    num_records: int = 10500,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate purchase orders and corresponding delivery records.
    Ensures 1-to-1 integrity between Purchase_ID, Supplier_ID, and quantities.
    """
    total_days = (end_date - start_date).days

    # Category affinities for suppliers for realistic procurement
    category_supplier_map = {
        "Electronics & Components": ["SUP01", "SUP02", "SUP06", "SUP11", "SUP15"],
        "Mechanical & Industrial Tools": ["SUP01", "SUP03", "SUP06", "SUP08", "SUP10"],
        "Raw Materials & Chemicals": ["SUP04", "SUP07", "SUP13", "SUP14", "SUP15"],
        "Packaging Materials": ["SUP05", "SUP09", "SUP14", "SUP15"],
        "Office & Facility Supplies": ["SUP01", "SUP08", "SUP12", "SUP14", "SUP15"],
    }

    # Weight product selection by velocity profile
    velocity_weights = {
        "Fast-Moving": 0.60,
        "Medium-Moving": 0.30,
        "Slow-Moving": 0.10,
    }
    prod_weights = df_products["_Velocity"].map(velocity_weights).values
    prod_weights = prod_weights / prod_weights.sum()

    purchases = []
    deliveries = []

    # Map supplier ratings to reliability probability
    # Higher rating -> higher on-time delivery rate
    supplier_ratings = dict(zip(df_suppliers["Supplier_ID"], df_suppliers["Rating"]))

    # Generate dates across the 2-year range
    random_day_offsets = np.sort(np.random.randint(0, total_days, size=num_records))

    for i in range(num_records):
        p_id_int = i + 1
        purchase_id = f"PO-{p_id_int:05d}"
        delivery_id = f"DEL-{p_id_int:05d}"

        # Choose product based on velocity weight
        prod_idx = np.random.choice(len(df_products), p=prod_weights)
        prod_row = df_products.iloc[prod_idx]
        product_id = prod_row["Product_ID"]
        category = prod_row["Category"]
        base_cost = prod_row["Unit_Cost"]
        lead_time = int(prod_row["Lead_Time_Days"])
        velocity = prod_row["_Velocity"]

        # Choose supplier mapped to category
        possible_suppliers = category_supplier_map[category]
        supplier_id = np.random.choice(possible_suppliers)
        sup_rating = supplier_ratings[supplier_id]

        # Order quantity determined by velocity
        if velocity == "Fast-Moving":
            quantity = int(np.random.choice([100, 150, 200, 250, 300, 400, 500]))
        elif velocity == "Medium-Moving":
            quantity = int(np.random.choice([40, 50, 60, 80, 100, 120]))
        else:  # Slow-Moving
            quantity = int(np.random.choice([10, 15, 20, 30, 40]))

        # Minor realistic cost variation (±3%)
        cost_variation = np.random.uniform(0.97, 1.03)
        unit_cost = round(float(base_cost * cost_variation), 2)
        total_cost = round(float(quantity * unit_cost), 2)

        # Dates
        order_date = start_date + timedelta(days=int(random_day_offsets[i]))
        expected_date = order_date + timedelta(days=lead_time)

        # Supplier rating influences delay probability:
        # Rating 4.9 -> ~95% on-time, Rating 3.1 -> ~65% on-time
        on_time_prob = min(0.96, max(0.60, 0.40 + (sup_rating / 5.0) * 0.58))
        is_on_time = np.random.rand() < on_time_prob

        if is_on_time:
            # Delivered slightly early or exactly on expected date
            early_days = int(np.random.choice([0, 0, 1, 2], p=[0.60, 0.25, 0.10, 0.05]))
            actual_date = expected_date - timedelta(days=early_days)
            if actual_date < order_date:
                actual_date = order_date + timedelta(days=1)
            delivery_status = "On-Time"
        else:
            # Delayed delivery by 1 to 14 days
            delay_days = int(np.random.exponential(scale=4.0)) + 1
            delay_days = min(delay_days, 18)
            actual_date = expected_date + timedelta(days=delay_days)
            delivery_status = "Delayed"

        purchases.append({
            "Purchase_ID": purchase_id,
            "Purchase_Date": order_date.strftime("%Y-%m-%d"),
            "Product_ID": product_id,
            "Supplier_ID": supplier_id,
            "Quantity": quantity,
            "Unit_Cost": unit_cost,
            "Total_Cost": total_cost,
        })

        deliveries.append({
            "Delivery_ID": delivery_id,
            "Purchase_ID": purchase_id,
            "Supplier_ID": supplier_id,
            "Order_Date": order_date.strftime("%Y-%m-%d"),
            "Expected_Date": expected_date.strftime("%Y-%m-%d"),
            "Actual_Date": actual_date.strftime("%Y-%m-%d"),
            "Quantity": quantity,
            "Delivery_Status": delivery_status,
        })

    df_purchases = pd.DataFrame(purchases)
    df_deliveries = pd.DataFrame(deliveries)

    return df_purchases, df_deliveries


def generate_inventory(
    df_products: pd.DataFrame,
    df_purchases: pd.DataFrame,
    df_deliveries: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
) -> pd.DataFrame:
    """
    Generate daily inventory records for all 50 products over the 2-year horizon.
    Calculates Opening_Stock, Received, Sold, and Closing_Stock with mathematical rigor.
    No negative stocks possible (Sold <= Opening_Stock + Received).

    Incorporates realistic inventory profiles:
    - First 5 products: 'Low-Stock' (initial stock 0.3-0.8 x Reorder_Level, persistent replenishment deficits)
    - Next 5 products: 'Excess-Stock' (initial stock 2.5-4.0 x Reorder_Level, surplus replenishment)
    - Remaining 40 products: 'Normal' (initial stock 1.0-1.8 x Reorder_Level, balanced operations)

    Daily demand related to product velocity:
    - Fast-Moving: ~20-35 units/day
    - Medium-Moving: ~7-15 units/day
    - Slow-Moving: ~1-5 units/day
    """
    # Map Purchase_ID -> Product_ID
    purch_to_prod = dict(zip(df_purchases["Purchase_ID"], df_purchases["Product_ID"]))

    # Map deliveries to Product_ID using Purchase_ID foreign key
    df_deliveries_merged = df_deliveries.copy()
    df_deliveries_merged["Product_ID"] = df_deliveries_merged["Purchase_ID"].map(purch_to_prod)

    # Group incoming delivery quantities by (Product_ID, Actual_Date) -> received inventory quantity
    receipts_grouped = (
        df_deliveries_merged.groupby(["Product_ID", "Actual_Date"])["Quantity"]
        .sum()
        .to_dict()
    )

    date_series = [start_date + timedelta(days=d) for d in range((end_date - start_date).days + 1)]

    # Product profiles map
    product_profiles = {}
    for idx, row in df_products.iterrows():
        p_id = row["Product_ID"]
        vel = row["_Velocity"]
        reorder_lvl = row["Reorder_Level"]

        # Assign initial stock according to profile specification:
        # 1. First 5 products: Low-Stock (0.3 - 0.8 x Reorder_Level)
        # 2. Next 5 products: Excess-Stock (2.5 - 4.0 x Reorder_Level)
        # 3. Remaining 40 products: Normal (1.0 - 1.8 x Reorder_Level)
        if idx < 5:
            profile = "Low-Stock"
            init_mult = np.random.uniform(0.35, 0.75)
        elif 5 <= idx < 10:
            profile = "Excess-Stock"
            init_mult = np.random.uniform(2.6, 3.8)
        else:
            profile = "Normal"
            init_mult = np.random.uniform(1.1, 1.7)

        initial_stock = int(round(reorder_lvl * init_mult))

        product_profiles[p_id] = {
            "idx": idx,
            "velocity": vel,
            "reorder_level": reorder_lvl,
            "profile": profile,
            "current_stock": initial_stock,
        }

    last_delivery_day = {p_id: 0 for p_id in df_products["Product_ID"]}
    inventory_rows = []
    inv_counter = 1

    for day_idx, dt in enumerate(date_series):
        dt_str = dt.strftime("%Y-%m-%d")
        day_of_week = dt.weekday()  # 0=Mon, 6=Sun

        for idx, p_row in df_products.iterrows():
            p_id = p_row["Product_ID"]
            meta = product_profiles[p_id]
            vel = meta["velocity"]
            prof = meta["profile"]
            reorder_lvl = meta["reorder_level"]

            opening_stock = meta["current_stock"]
            raw_rec = receipts_grouped.get((p_id, dt_str), 0)

            # Daily demand related to velocity with small random variation:
            # Fast-Moving: ~20-35 units/day
            # Medium-Moving: ~7-15 units/day
            # Slow-Moving: ~1-5 units/day
            if vel == "Fast-Moving":
                base_demand = int(np.random.randint(20, 36))
                daily_rate = 26.5
            elif vel == "Medium-Moving":
                base_demand = int(np.random.randint(7, 16))
                daily_rate = 11.0
            else:  # Slow-Moving
                base_demand = int(np.random.randint(1, 6))
                daily_rate = 3.0

            # Slight weekend dampening
            if day_of_week in (5, 6):
                base_demand = max(1, int(base_demand * 0.75))

            # Delivery receipts connected to actual delivery dates
            if raw_rec > 0:
                days_since_last = max(1, day_idx - last_delivery_day[p_id])
                last_delivery_day[p_id] = day_idx

                if prof == "Low-Stock":
                    # Severe supplier shortages / chronic backorders:
                    # Receipts replace only a fraction of consumption, keeping stock near/below reorder level
                    rec_amount = int(round(days_since_last * daily_rate * np.random.uniform(0.60, 0.82)))
                    if opening_stock + rec_amount > reorder_lvl:
                        rec_amount = max(1, int(reorder_lvl * np.random.uniform(0.1, 0.3)))
                    received = max(1, rec_amount)
                elif prof == "Excess-Stock":
                    # Surplus ordering & slow turnover:
                    # Replenishment pushes stock well above the 60-day demand target
                    target_excess = daily_rate * 60 * np.random.uniform(1.20, 1.50)
                    rec_amount = int(round(days_since_last * daily_rate * np.random.uniform(1.25, 1.55)))
                    if opening_stock < target_excess:
                        rec_amount = max(rec_amount, int((target_excess - opening_stock) * 0.25 + days_since_last * daily_rate))
                    received = max(5, rec_amount)
                else:
                    # Normal product:
                    # Healthy operating buffer safely between Reorder_Level and the 60-day target (~32-42 days)
                    target_stock_60 = daily_rate * 60
                    target_normal = max(reorder_lvl * 1.15, min(target_stock_60 * 0.65, reorder_lvl + 0.40 * (target_stock_60 - reorder_lvl)))
                    rec_amount = int(round(days_since_last * daily_rate * np.random.uniform(0.90, 1.10)))
                    diff = target_normal - opening_stock
                    rec_amount = max(1, int(rec_amount + diff * 0.20))
                    # Prevent accidental breach of 60-day target
                    if opening_stock + rec_amount > target_stock_60 * 0.85:
                        rec_amount = max(1, int(target_stock_60 * 0.80 - opening_stock))
                    received = max(1, rec_amount)
            else:
                received = 0

            available_stock = opening_stock + received

            # Ensure sold never exceeds available stock (No negative stock)
            sold = min(base_demand, available_stock)

            # Calculate closing stock
            closing_stock = available_stock - sold

            # Carry forward to next day
            meta["current_stock"] = closing_stock

            inventory_rows.append({
                "Inventory_ID": f"INV-{inv_counter:06d}",
                "Date": dt_str,
                "Product_ID": p_id,
                "Opening_Stock": opening_stock,
                "Received": received,
                "Sold": sold,
                "Closing_Stock": closing_stock,
            })
            inv_counter += 1

    return pd.DataFrame(inventory_rows)


def generate_full_dataset():
    """Execute complete dataset generation pipeline and output CSVs."""
    set_seed(42)

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    print("Generating Supply Chain & Inventory Analytics Synthetic Data...")

    # 1. Products (50 items)
    df_products = generate_products()

    # 2. Suppliers (15 suppliers)
    df_suppliers = generate_suppliers()

    # 3. Purchases & Deliveries (~10,500 records each)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    df_purchases, df_deliveries = generate_purchases_and_deliveries(
        df_products, df_suppliers, start_date, end_date, num_records=10500
    )

    # 4. Inventory records (50 products x 731 days = 36,550 daily records)
    df_inventory = generate_inventory(
        df_products, df_purchases, df_deliveries, start_date, end_date
    )

    # Clean internal temporary columns before exporting
    df_products_clean = df_products.drop(columns=["_Velocity"])

    # Export CSVs
    products_path = os.path.join(data_dir, "products.csv")
    suppliers_path = os.path.join(data_dir, "suppliers.csv")
    purchases_path = os.path.join(data_dir, "purchases.csv")
    deliveries_path = os.path.join(data_dir, "deliveries.csv")
    inventory_path = os.path.join(data_dir, "inventory.csv")

    df_products_clean.to_csv(products_path, index=False)
    df_suppliers.to_csv(suppliers_path, index=False)
    df_purchases.to_csv(purchases_path, index=False)
    df_deliveries.to_csv(deliveries_path, index=False)
    df_inventory.to_csv(inventory_path, index=False)

    # Print summary
    print("\n" + "=" * 60)
    print("  SUPPLY CHAIN INVENTORY ANALYTICS - SYNTHETIC DATA READY")
    print("=" * 60)
    print(f"1. Products CSV    : {len(df_products_clean):>7,d} records -> {products_path}")
    print(f"2. Suppliers CSV   : {len(df_suppliers):>7,d} records -> {suppliers_path}")
    print(f"3. Purchases CSV   : {len(df_purchases):>7,d} records -> {purchases_path}")
    print(f"4. Deliveries CSV  : {len(df_deliveries):>7,d} records -> {deliveries_path}")
    print(f"5. Inventory CSV   : {len(df_inventory):>7,d} records -> {inventory_path}")
    print("=" * 60)
    print("Data integrity verification:")
    print(f"- Negative stock instances       : {(df_inventory['Closing_Stock'] < 0).sum()}")
    print(f"- Math logic discrepancies       : {((df_inventory['Opening_Stock'] + df_inventory['Received'] - df_inventory['Sold']) != df_inventory['Closing_Stock']).sum()}")
    print(f"- Purchase total cost mismatch   : {((df_purchases['Quantity'] * df_purchases['Unit_Cost']).round(2) != df_purchases['Total_Cost']).sum()}")
    print(f"- Unique products across files   : {df_products_clean['Product_ID'].nunique()}")
    print(f"- Unique suppliers across files  : {df_suppliers['Supplier_ID'].nunique()}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    generate_full_dataset()
