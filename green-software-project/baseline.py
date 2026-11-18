
import pandas as pd
import time


def run_baseline(df):
    timings = {}

    # 1. Remove duplicate transactions using a Python set
    start = time.perf_counter()

    seen = set()
    unique_rows = []

    for row in df.itertuples(index=False):
        if row.transaction_id not in seen:
            seen.add(row.transaction_id)
            unique_rows.append(row)

    deduplicated = pd.DataFrame(
        unique_rows,
        columns=df.columns
    )

    timings["duplicate_removal"] = time.perf_counter() - start

    # 2. Filter transactions using Python loops
    start = time.perf_counter()

    filtered_rows = []

    for row in deduplicated.itertuples(index=False):
        if row.quantity >= 2 and row.unit_price >= 100:
            filtered_rows.append(row)

    filtered = pd.DataFrame(
        filtered_rows,
        columns=df.columns
    )

    timings["filtering"] = time.perf_counter() - start

    # 3. Calculate revenue using Python loops
    start = time.perf_counter()

    revenues = []

    for row in filtered.itertuples(index=False):
        revenues.append(
            round(row.quantity * row.unit_price, 2)
        )

    filtered["revenue"] = revenues

    timings["revenue_calculation"] = time.perf_counter() - start

    # 4. Aggregate results using a Python dictionary
    start = time.perf_counter()

    aggregation = {}

    for row in filtered.itertuples(index=False):
        key = (row.region, row.category)

        if key not in aggregation:
            aggregation[key] = {
                "transaction_count": 0,
                "total_revenue": 0.0
            }

        aggregation[key]["transaction_count"] += 1
        aggregation[key]["total_revenue"] += row.revenue

    results = []

    for key, values in aggregation.items():
        results.append({
            "region": key[0],
            "category": key[1],
            "transaction_count": values["transaction_count"],
            "total_revenue": round(values["total_revenue"], 2)
        })

    output = pd.DataFrame(results)

    output = output.sort_values(
        ["region", "category"]
    ).reset_index(drop=True)

    timings["aggregation"] = time.perf_counter() - start

    return output, timings
