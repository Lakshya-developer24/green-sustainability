import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# Load existing experiment results
df = pd.read_csv("results/experiment_results.csv")

# Calculate emissions consistently from measured energy
df["calculated_emissions_kg"] = (
    df["energy_per_execution_kwh"]
    * df["carbon_intensity_g_per_kwh"]
    / 1000
)

# Calculate average results across batches
summary = df.groupby("implementation").agg(
    execution_time=("average_execution_time_seconds", "mean"),
    energy=("energy_per_execution_kwh", "mean"),
    emissions=("calculated_emissions_kg", "mean")
)

stages = [
    "duplicate_removal_seconds",
    "filtering_seconds",
    "revenue_calculation_seconds",
    "aggregation_seconds"
]

stage_summary = df.groupby("implementation")[stages].mean()

baseline = summary.loc["baseline"]
optimized = summary.loc["optimized"]

metrics = {
    "Energy consumption": (
        baseline["energy"], optimized["energy"]
    ),
    "Carbon emissions": (
        baseline["emissions"], optimized["emissions"]
    ),
    "Execution time": (
        baseline["execution_time"], optimized["execution_time"]
    )
}

reductions = {
    name: (values[0] - values[1]) / values[0] * 100
    for name, values in metrics.items()
}

output_dir = Path("results/charts")
output_dir.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (9, 5),
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False
})

def comparison_chart(values, labels, title, ylabel, filename):
    fig, ax = plt.subplots()

    bars = ax.bar(
        ["Baseline", "Optimized"],
        values,
        width=0.5
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.bar_label(bars, fmt="%.4g", padding=4)

    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.savefig(output_dir / filename, dpi=300)
    plt.close()


# 1. Energy consumption comparison, in mWh
comparison_chart(
    [baseline["energy"] * 1_000_000,
     optimized["energy"] * 1_000_000],
    ["Baseline", "Optimized"],
    "Energy Consumption per Execution",
    "Energy (mWh)",
    "01_energy_comparison.png"
)

# 2. Estimated carbon emissions comparison, in mg
comparison_chart(
    [baseline["emissions"] * 1_000_000,
     optimized["emissions"] * 1_000_000],
    ["Baseline", "Optimized"],
    "Estimated Carbon Emissions per Execution",
    "Emissions (mg CO2e)",
    "02_emissions_comparison.png"
)

# 3. Execution time comparison
comparison_chart(
    [baseline["execution_time"],
     optimized["execution_time"]],
    ["Baseline", "Optimized"],
    "Average Execution Time per Execution",
    "Time (seconds)",
    "03_execution_time.png"
)

# 4. Stage-wise execution time comparison
fig, ax = plt.subplots(figsize=(10, 6))

stage_names = [
    "Duplicate removal",
    "Filtering",
    "Revenue calculation",
    "Aggregation"
]

x = np.arange(len(stages))
width = 0.35

ax.bar(
    x - width / 2,
    stage_summary.loc["baseline"].values,
    width,
    label="Baseline"
)

ax.bar(
    x + width / 2,
    stage_summary.loc["optimized"].values,
    width,
    label="Optimized"
)

ax.set_title("Processing Time by Stage", fontsize=14, fontweight="bold")
ax.set_ylabel("Average time (seconds)")
ax.set_xticks(x)
ax.set_xticklabels(stage_names, rotation=10)
ax.legend()
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(output_dir / "04_stage_comparison.png", dpi=300)
plt.close()

# 5. Percentage reduction
fig, ax = plt.subplots(figsize=(9, 5))

names = list(reductions.keys())
values = list(reductions.values())

bars = ax.barh(names, values, height=0.5)

ax.set_title("Reduction Achieved Through Optimization",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Reduction (%)")
ax.bar_label(bars, fmt="%.2f%%", padding=5)
ax.invert_yaxis()
ax.grid(axis="x", alpha=0.25)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(output_dir / "05_percentage_reduction.png", dpi=300)
plt.close()

# Print final comparison
print("\nAVERAGE EXPERIMENT RESULTS")
print("=" * 45)

print(f"Baseline execution time:  {baseline['execution_time']:.6f} s")
print(f"Optimized execution time: {optimized['execution_time']:.6f} s")

print(f"\nBaseline energy:  {baseline['energy'] * 1_000_000:.6f} mWh")
print(f"Optimized energy: {optimized['energy'] * 1_000_000:.6f} mWh")

print(f"\nBaseline emissions:  {baseline['emissions'] * 1_000_000:.6f} mg CO2e")
print(f"Optimized emissions: {optimized['emissions'] * 1_000_000:.6f} mg CO2e")

print("\nPERCENTAGE REDUCTION")
for name, value in reductions.items():
    print(f"{name}: {value:.2f}%")

print("\nCharts saved in results/charts/")
print("Generated 5 comparison charts.")
