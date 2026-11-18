
import time
from pathlib import Path

import pandas as pd
from codecarbon import EmissionsTracker

from baseline import run_baseline
from optimized import run_optimized


# EXPERIMENT CONFIGURATION

DATASET_PATH = "data/transactions.csv"

RESULTS_DIR = Path("results")
EMISSIONS_DIR = Path("emissions")

REPETITIONS = 5
MIN_TRACKING_SECONDS = 10
SAMPLING_INTERVAL = 1

CARBON_INTENSITY = 675

IMPLEMENTATIONS = {
    "baseline": run_baseline,
    "optimized": run_optimized
}


def run_measurement(name, function, df, batch_number):

    print(f"\nMeasuring {name.upper()}, batch {batch_number}")

    output_file = (
        f"{name}_batch_{batch_number}.csv"
    )

    tracker = EmissionsTracker(
        project_name=f"{name}_batch_{batch_number}",
        measure_power_secs=SAMPLING_INTERVAL,
        output_dir=str(EMISSIONS_DIR),
        output_file=output_file,
        save_to_api=False,
        save_to_file=True,
        force_carbon_intensity_g_co2e_kwh=CARBON_INTENSITY,
        allow_multiple_runs=True,
        log_level="error"
    )

    execution_times = []
    stage_totals = {
        "duplicate_removal": 0.0,
        "filtering": 0.0,
        "revenue_calculation": 0.0,
        "aggregation": 0.0
    }

    completed_output = None

    tracker.start()

    try:
        measurement_start = time.perf_counter()

        while (
            time.perf_counter() - measurement_start
            < MIN_TRACKING_SECONDS
        ):

            execution_start = time.perf_counter()

            output, timings = function(df)

            execution_time = (
                time.perf_counter() - execution_start
            )

            execution_times.append(execution_time)

            for stage, duration in timings.items():
                stage_totals[stage] += duration

            completed_output = output

        measurement_duration = (
            time.perf_counter() - measurement_start
        )

    finally:
        emissions = tracker.stop()

    # Read total energy recorded by CodeCarbon

    emissions_file = EMISSIONS_DIR / output_file

    carbon_data = pd.read_csv(emissions_file)

    total_energy = float(
        carbon_data.iloc[-1]["energy_consumed"]
    )

    execution_count = len(execution_times)

    average_execution_time = (
        sum(execution_times) / execution_count
    )

    average_stage_times = {
        stage: duration / execution_count
        for stage, duration in stage_totals.items()
    }

    energy_per_execution = (
        total_energy / execution_count
    )

    emissions_per_execution = (
        emissions / execution_count
    )

    result = {
        "implementation": name,
        "batch": batch_number,
        "executions": execution_count,
        "measurement_duration_seconds": measurement_duration,
        "average_execution_time_seconds": average_execution_time,
        "duplicate_removal_seconds":
            average_stage_times["duplicate_removal"],
        "filtering_seconds":
            average_stage_times["filtering"],
        "revenue_calculation_seconds":
            average_stage_times["revenue_calculation"],
        "aggregation_seconds":
            average_stage_times["aggregation"],
        "total_energy_kwh": total_energy,
        "energy_per_execution_kwh": energy_per_execution,
        "total_emissions_kg": emissions,
        "emissions_per_execution_kg":
            emissions_per_execution,
        "carbon_intensity_g_per_kwh": CARBON_INTENSITY
    }

    print(f"Executions completed: {execution_count}")
    print(
        f"Average execution time: "
        f"{average_execution_time:.6f} seconds"
    )
    print(
        f"Energy per execution: "
        f"{energy_per_execution:.12f} kWh"
    )
    print(
        f"Emissions per execution: "
        f"{emissions_per_execution:.12f} kg CO2e"
    )

    return result, completed_output


def main():

    RESULTS_DIR.mkdir(exist_ok=True)
    EMISSIONS_DIR.mkdir(exist_ok=True)

    print("=" * 55)
    print("GREEN SOFTWARE ENGINEERING EXPERIMENT")
    print("=" * 55)

    # Load dataset once, outside the measurement sessions

    print("\nLoading dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset records: {len(df):,}")

    # Warm-up executions

    print("\nPerforming warm-up executions...")

    baseline_warmup, _ = run_baseline(df)
    optimized_warmup, _ = run_optimized(df)

    pd.testing.assert_frame_equal(
        baseline_warmup,
        optimized_warmup,
        check_dtype=False,
        check_exact=False,
        atol=0.01,
        rtol=0
    )

    print("Warm-up completed. Outputs match.")

    del baseline_warmup
    del optimized_warmup

    all_results = []
    final_outputs = {}

    # Alternate execution order to reduce order-related bias

    for batch in range(1, REPETITIONS + 1):

        if batch % 2 == 1:
            order = ["baseline", "optimized"]
        else:
            order = ["optimized", "baseline"]

        for name in order:

            result, output = run_measurement(
                name,
                IMPLEMENTATIONS[name],
                df,
                batch
            )

            all_results.append(result)
            final_outputs[name] = output

    # Validate final outputs

    print("\nValidating final outputs...")

    pd.testing.assert_frame_equal(
        final_outputs["baseline"],
        final_outputs["optimized"],
        check_dtype=False,
        check_exact=False,
        atol=0.01,
        rtol=0
    )

    print("Final outputs match.")

    # Save final outputs

    final_outputs["baseline"].to_csv(
        RESULTS_DIR / "baseline_output.csv",
        index=False
    )

    final_outputs["optimized"].to_csv(
        RESULTS_DIR / "optimized_output.csv",
        index=False
    )

    # Save all measurement batches

    results_df = pd.DataFrame(all_results)

    results_df.to_csv(
        RESULTS_DIR / "experiment_results.csv",
        index=False
    )

    # Display experiment summary

    print("\n" + "=" * 55)
    print("EXPERIMENT COMPLETED")
    print("=" * 55)

    summary = (
        results_df
        .groupby("implementation")
        .agg(
            average_execution_time=(
                "average_execution_time_seconds", "mean"
            ),
            average_energy=(
                "energy_per_execution_kwh", "mean"
            ),
            average_emissions=(
                "emissions_per_execution_kg", "mean"
            )
        )
    )

    print("\nAVERAGE RESULTS")
    print(summary.to_string())

    print("\nFiles saved:")
    print("- results/experiment_results.csv")
    print("- results/baseline_output.csv")
    print("- results/optimized_output.csv")
    print("- emissions/")

    print("\nAll experiment batches completed successfully.")


if __name__ == "__main__":
    main()
