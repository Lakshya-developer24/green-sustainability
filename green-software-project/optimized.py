
import pandas as pd
import numpy as np
import time


def run_optimized(df):
    timings = {}

    # 1. Remove duplicate transactions using Pandas
    start = time.perf_counter()

    deduplicated = df.drop_duplicates(
        subset=["transaction_id"],
        keep="first"
    ).copy()

    timings["duplicate_removal"] = time.perf_counter() - start

    # 2. Filter transactions using vectorized conditions
    start = time.perf_counter()

    filtered = deduplicated.loc[
        (deduplicated["quantity"] >= 2) &
        (deduplicated["unit_price"] >= 100)
    ].copy()

    timings["filtering"] = time.perf_counter() - start

    # 3. Calculate revenue using vectorized multiplication
    start = time.perf_counter()

    filtered["revenue"] = np.round(
        filtered["quantity"].to_numpy() *
        filtered["unit_price"].to_numpy(),
        2
    )

    timings["revenue_calculation"] = time.perf_counter() - start

    # 4. Aggregate using Pandas groupby
    start = time.perf_counter()

    output = (
        filtered
        .groupby(["region", "category"], as_index=False)
        .agg(
            transaction_count=("transaction_id", "count"),
            total_revenue=("revenue", "sum")
        )
    )

    output["total_revenue"] = output["total_revenue"].round(2)

    output = output.sort_values(
        ["region", "category"]
    ).reset_index(drop=True)

    timings["aggregation"] = time.perf_counter() - start

    return output, timings
