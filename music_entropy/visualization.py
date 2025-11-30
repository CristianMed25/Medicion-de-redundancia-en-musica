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
