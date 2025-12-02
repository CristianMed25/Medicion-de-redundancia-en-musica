"""Visualizacion automatica de metricas de entropia."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

from .analysis import AnalysisResult


def _prepare_output(path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def plot_global_metrics(result: AnalysisResult, output_path: str | Path) -> Path:
    """Generate a bar chart with global entropy and rhythmic metrics."""
    path = _prepare_output(output_path)
    fig, axes = plt.subplots(2, 1, figsize=(6.5, 6), constrained_layout=True)
    axes[0].bar(["H0", "Hk", "Hmax"], [result.h0, result.hk, result.hmax], color=["#4c72b0", "#55a868", "#c44e52"])
    axes[0].set_ylabel("bits")
    axes[0].set_title(f"Entropy profile\n{result.path.name}")
    axes[0].grid(axis="y", alpha=0.3, linestyle="--", linewidth=0.5)

    axes[1].bar(
        ["Redundancy", "Predictability", "LZC", "LZC norm"],
        [result.redundancy, result.ip, result.lzc, result.lzc_normalized],
        color=["#8172b2", "#ccb974", "#64b5cd", "#dd8452"],
    )
    axes[1].set_ylabel("value")
    axes[1].set_ylim(bottom=0)
    axes[1].grid(axis="y", alpha=0.3, linestyle="--", linewidth=0.5)

    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_local_entropies(result: AnalysisResult, output_path: str | Path) -> Path:
    """Generate a line plot for local entropy windows."""
    if not result.local:
        raise ValueError("Result does not contain local metrics. Enable --local in the CLI.")
    path = _prepare_output(output_path)
    windows = [entry["window"] for entry in result.local]
    h0_vals = [entry["h0"] for entry in result.local]
    hk_vals = [entry["hk"] for entry in result.local]

    fig, ax = plt.subplots(figsize=(7.5, 4.5), constrained_layout=True)
    ax.plot(windows, h0_vals, label="H0", color="#4c72b0")
    ax.plot(windows, hk_vals, label="Hk", color="#55a868")
    ax.set_xlabel("Window index")
    ax.set_ylabel("bits")
    ax.set_title(f"Local entropy windows\n{result.path.name}")
    ax.grid(alpha=0.3, linestyle="--", linewidth=0.5)
    ax.legend()

    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def plot_batch_comparison(results: list[AnalysisResult], output_path: str | Path) -> Path:
    """Generate a chart showing average metrics from all analyzed files.
    
    Args:
        results: List of AnalysisResult objects from batch processing.
        output_path: Path where the comparison chart will be saved.
    
    Returns:
        Path to the saved chart.
    """
    if not results:
        raise ValueError("Cannot create batch comparison plot: no results provided.")
    
    path = _prepare_output(output_path)
    
    # Calculate averages
    n = len(results)
    avg_h0 = sum(r.h0 for r in results) / n
    avg_hk = sum(r.hk for r in results) / n
    avg_hmax = sum(r.hmax for r in results) / n
    avg_redundancy = sum(r.redundancy for r in results) / n
    avg_ip = sum(r.ip for r in results) / n
    avg_lzc_norm = sum(r.lzc_normalized for r in results) / n
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 1, figsize=(8, 7), constrained_layout=True)
    
    # Subplot 1: Average Entropy metrics
    axes[0].bar(['H0', 'Hk', 'Hmax'], [avg_h0, avg_hk, avg_hmax], 
                color=['#4c72b0', '#55a868', '#c44e52'])
    axes[0].set_ylabel('bits')
    axes[0].set_title(f'Promedios de Entropías ({n} archivos)')
    axes[0].grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Add value labels on bars
    for i, v in enumerate([avg_h0, avg_hk, avg_hmax]):
        axes[0].text(i, v + 0.1, f'{v:.2f}', ha='center', va='bottom', fontsize=10)
    
    # Subplot 2: Average Complexity metrics
    axes[1].bar(['Redundancia', 'Predictibilidad', 'LZC norm'],
                [avg_redundancy, avg_ip, avg_lzc_norm],
                color=['#8172b2', '#ccb974', '#64b5cd'])
    axes[1].set_ylabel('valor')
    axes[1].set_title('Promedios de Métricas de Complejidad')
    axes[1].grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    axes[1].set_ylim(bottom=0)
    
    # Add value labels on bars
    for i, v in enumerate([avg_redundancy, avg_ip, avg_lzc_norm]):
        axes[1].text(i, v + 0.05, f'{v:.2f}', ha='center', va='bottom', fontsize=10)
    
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return path


def plot_batch_local_averages(results: list[AnalysisResult], output_path: str | Path) -> Path:
    """Generate a chart showing average normalized local entropy metrics across all files.
    
    This function normalizes data for comparability:
    - Window index is converted to percentage of file length (0-100%)
    - Entropy values (H0, Hk) are normalized by Hmax for each file
    - Uncertainty bands show ±1 standard deviation
    
    Args:
        results: List of AnalysisResult objects with local metrics.
        output_path: Path where the chart will be saved.
    
    Returns:
        Path to the saved chart.
    """
    if not results:
        raise ValueError("Cannot create local averages plot: no results provided.")
    
    # Filter results that have local metrics
    results_with_local = [r for r in results if r.local]
    
    if not results_with_local:
        raise ValueError("No results contain local entropy metrics. Use --local flag when analyzing.")
    
    path = _prepare_output(output_path)
    
    # Normalize data for each file:
    # 1. Convert window index to percentage (0-100)
    # 2. Normalize entropy by Hmax
    
    # We'll use a common set of percentage bins (0-100%)
    num_bins = 100
    percentage_bins = list(range(num_bins + 1))
    
    # For each percentage bin, collect normalized entropy values from all files
    h0_normalized_by_bin = [[] for _ in range(num_bins + 1)]
    hk_normalized_by_bin = [[] for _ in range(num_bins + 1)]
    
    for result in results_with_local:
        num_windows = len(result.local)
        hmax = result.hmax
        
        # Skip files with invalid Hmax
        if hmax <= 0:
            continue
        
        for window_idx, window_data in enumerate(result.local):
            # Convert window index to percentage
            percentage = int((window_idx / (num_windows - 1)) * 100) if num_windows > 1 else 0
            percentage = min(percentage, 100)  # Clamp to 100
            
            # Normalize entropy values by Hmax
            h0_norm = window_data['h0'] / hmax
            hk_norm = window_data['hk'] / hmax
            
            h0_normalized_by_bin[percentage].append(h0_norm)
            hk_normalized_by_bin[percentage].append(hk_norm)
    
    # Calculate averages and standard deviations for each percentage bin
    avg_h0_normalized = []
    avg_hk_normalized = []
    std_h0_normalized = []
    std_hk_normalized = []
    valid_percentages = []
    
    import numpy as np
    
    for pct in percentage_bins:
        if h0_normalized_by_bin[pct]:
            avg_h0_normalized.append(np.mean(h0_normalized_by_bin[pct]))
            avg_hk_normalized.append(np.mean(hk_normalized_by_bin[pct]))
            std_h0_normalized.append(np.std(h0_normalized_by_bin[pct]))
            std_hk_normalized.append(np.std(hk_normalized_by_bin[pct]))
            valid_percentages.append(pct)
    
    # Convert to numpy arrays for easier computation
    valid_percentages = np.array(valid_percentages)
    avg_h0_normalized = np.array(avg_h0_normalized)
    avg_hk_normalized = np.array(avg_hk_normalized)
    std_h0_normalized = np.array(std_h0_normalized)
    std_hk_normalized = np.array(std_hk_normalized)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    
    # Plot H0 with uncertainty band
    ax.plot(valid_percentages, avg_h0_normalized, label='H0/Hmax promedio', 
            color='#4c72b0', linewidth=2, zorder=3)
    ax.fill_between(valid_percentages, 
                     avg_h0_normalized - std_h0_normalized,
                     avg_h0_normalized + std_h0_normalized,
                     color='#4c72b0', alpha=0.2, label='H0 ±1σ', zorder=1)
    
    # Plot Hk with uncertainty band
    ax.plot(valid_percentages, avg_hk_normalized, label='Hk/Hmax promedio', 
            color='#55a868', linewidth=2, zorder=3)
    ax.fill_between(valid_percentages,
                     avg_hk_normalized - std_hk_normalized,
                     avg_hk_normalized + std_hk_normalized,
                     color='#55a868', alpha=0.2, label='Hk ±1σ', zorder=1)
    
    ax.set_xlabel('Posición en el archivo (%)')
    ax.set_ylabel('Entropía normalizada (valor/Hmax)')
    ax.set_title(f'Promedios Normalizados de Entropías Locales con Incertidumbre ({len(results_with_local)} archivos)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.3, linestyle='--', linewidth=0.5, zorder=0)
    ax.legend(loc='best')
    
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return path
