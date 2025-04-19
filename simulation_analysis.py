#!/usr/bin/env python3
"""
analyze_simulation.py

Load the simulation results, compute summary statistics, and generate plots comparing
policies under different bandwidth and arrival rate settings.
"""
import pandas as pd
import matplotlib.pyplot as plt


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    return df


def summarize(df: pd.DataFrame, output_csv: str = 'summary.csv') -> pd.DataFrame:
    """
    Group by policy, bandwidth, and arrival_rate; compute mean and std for key metrics.
    Save summary to CSV and return the summary DataFrame.
    """
    summary = (
        df
        .groupby(['policy', 'bandwidth', 'arrival_rate'])
        .agg(
            run_time_mean=('run_time', 'mean'),
            run_time_std=('run_time', 'std'),
            quality_mean=('quality', 'mean'),
            quality_std=('quality', 'std'),
            avg_uncertainty_mean=('avg_uncertainty', 'mean'),
            avg_uncertainty_std=('avg_uncertainty', 'std')
        )
        .reset_index()
    )
    summary.to_csv(output_csv, index=False)
    return summary


def plot_vs_bandwidth(summary: pd.DataFrame, metric: str, output_png: str):
    # plot mean vs bandwidth for each type
    for policy in summary['policy'].unique():
        data = summary[summary['policy'] == policy]
        plt.plot(
            data['bandwidth'],
            data[f'{metric}_mean'],
            marker='o',
            label=policy
        )
    plt.xlabel('Bandwidth (messages/sec)')
    plt.ylabel(metric.replace('_', ' ').title())
    plt.title(f'{metric.replace("_"," ").title()} vs Bandwidth')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_png)
    plt.clf()


def plot_vs_arrival_rate(summary: pd.DataFrame, metric: str, output_png: str):
    # plot metric mean vs arrival rate
    for policy in summary['policy'].unique():
        data = summary[summary['policy'] == policy]
        plt.plot(
            data['arrival_rate'],
            data[f'{metric}_mean'],
            marker='o',
            label=policy
        )
    plt.xlabel('Arrival Rate (queries/sec)')
    plt.ylabel(metric.replace('_', ' ').title())
    plt.title(f'{metric.replace("_"," ").title()} vs Arrival Rate')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_png)
    plt.clf()


def main():
    df = load_data('simulation_results.csv')

    summary = summarize(df, 'simulation_summary.csv')

    plot_vs_bandwidth(summary, 'run_time', 'run_time_vs_bandwidth.png')
    plot_vs_bandwidth(summary, 'avg_uncertainty', 'uncertainty_vs_bandwidth.png')
    plot_vs_arrival_rate(summary, 'quality', 'quality_vs_arrival_rate.png')

    print("Analysis complete. Summary: simulation_summary.csv; Plots: PNG files generated.")


if __name__ == '__main__':
    main()

