import numpy as np
import pandas as pd
from pathlib import Path


def generate_dataset():
    rng = np.random.default_rng(42)

    total_records = 500_000
    duplicate_records = 25_000
    unique_records = total_records - duplicate_records

    print("Generating synthetic e-commerce transactions...")

    # Generate unique transaction records
    data = {
        "transaction_id": [
            f"TXN{i:07d}" for i in range(unique_records)
        ],
        "customer_id": rng.integers(1000, 51000, unique_records),
        "product_id": rng.integers(100, 10100, unique_records),
        "quantity": rng.integers(1, 11, unique_records),
        "unit_price": np.round(
            rng.uniform(50, 5000, unique_records), 2
        ),
        "transaction_date": rng.choice(
            pd.date_range("2025-01-01", "2025-12-31"),
            unique_records
        ),
        "region": rng.choice(
            ["North", "South", "East", "West", "Central"],
            unique_records
        ),
        "category": rng.choice(
            ["Electronics", "Clothing", "Groceries",
             "Furniture", "Books"],
            unique_records
        )
    }

    df = pd.DataFrame(data)

    # Add duplicate transaction records
    duplicate_rows = df.sample(
        n=duplicate_records,
        random_state=42
    )

    df = pd.concat(
        [df, duplicate_rows],
        ignore_index=True
    )

    # Shuffle the records
    df = df.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    # Save dataset
    output_path = Path("data/transactions.csv")
    df.to_csv(output_path, index=False)

    print("\nDataset generated successfully.")
    print(f"Total records: {len(df):,}")
    print(f"Unique records before duplication: {unique_records:,}")
    print(f"Duplicate records added: {duplicate_records:,}")
    print(f"Dataset saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    generate_dataset()
