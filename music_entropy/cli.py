"""Command line interface for music entropy analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from . import visualization
from .analysis import AnalysisConfig, analyze_folder, analyze_piece, results_to_dataframe


def _config_from_args(args: argparse.Namespace) -> AnalysisConfig:
    return AnalysisConfig(
        markov_order=args.markov_order,
        window_size=args.window_size,
        window_step=args.window_step,
        time_unit=args.time_unit,
        compute_local=args.local,
    )


def _print_result(res) -> None:
    print(f"File: {res.path}")
    print(f"  H0: {res.h0:.4f}")
    print(f"  Hk (order): {res.hk:.4f}")
    print(f"  Hmax: {res.hmax:.4f}")
    print(f"  Redundancy: {res.redundancy:.4f}")
    print(f"  LZC: {res.lzc}")
    print(f"  LZC normalized: {res.lzc_normalized:.4f}")
    print(f"  Predictability (IP): {res.ip:.4f}")
    if res.local:
        print(f"  Local windows: {len(res.local)}")


def _save_local_csv(res, path: Path) -> None:
    if res.local is None:
        return
    records = [{**entry, "path": str(res.path)} for entry in res.local]
    import pandas as pd

    df = pd.DataFrame(records)
    df.to_csv(path, index=False)


def _maybe_plot_result(res, plot_dir: str | None) -> None:
    if not plot_dir:
        return
    base = Path(plot_dir)
    base.mkdir(parents=True, exist_ok=True)
    stem = Path(res.path).stem or "output"
    visualization.plot_global_metrics(res, base / f"{stem}_global.png")
    if res.local:
        visualization.plot_local_entropies(res, base / f"{stem}_local.png")


def handle_analyze(args: argparse.Namespace) -> int:
    cfg = _config_from_args(args)
    res = analyze_piece(args.input, input_type=args.input_type, config=cfg)
    _print_result(res)
    if args.output_csv:
        df = results_to_dataframe([res])
        df.to_csv(args.output_csv, index=False)
    if args.local_csv:
        _save_local_csv(res, Path(args.local_csv))
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(res.to_dict(), indent=2), encoding="utf-8")
    _maybe_plot_result(res, args.plot_dir)
    return 0


def handle_analyze_batch(args: argparse.Namespace) -> int:
    cfg = _config_from_args(args)
    results = analyze_folder(args.input, input_type=args.input_type, config=cfg, pattern=args.pattern)
    if not results:
        print("No files processed.", file=sys.stderr)
        return 1
    
    # Print results to console
    for res in results:
        _print_result(res)
    
    # Generate individual plots in song-specific folders
    if args.plot_dir:
        base = Path(args.plot_dir)
        for res in results:
            # Create individual folder for each song
            stem = Path(res.path).stem or "output"
            song_folder = base / stem
            song_folder.mkdir(parents=True, exist_ok=True)
            
            # Save plots in song folder
            visualization.plot_global_metrics(res, song_folder / f"{stem}_global.png")
            if res.local:
                visualization.plot_local_entropies(res, song_folder / f"{stem}_local.png")
    
    # Generate batch summary folder with compiled plots and CSV
    if args.plot_dir:
        base = Path(args.plot_dir)
        batch_folder = base / "batch"
        batch_folder.mkdir(parents=True, exist_ok=True)
        
        # Always generate CSV in batch folder
        csv_path = batch_folder / "batch_results.csv"
        df = results_to_dataframe(results)
        df.to_csv(csv_path, index=False)
        print(f"\nBatch results CSV saved: {csv_path}")
        
        # Generate batch comparison plots if requested
        if args.batch_plot:
            batch_plot_path = batch_folder / "batch_comparison.png"
            visualization.plot_batch_comparison(results, batch_plot_path)
            print(f"Batch comparison plot saved: {batch_plot_path}")
            
            # Generate local averages plot if local metrics are available
            if any(r.local for r in results):
                local_avg_path = batch_folder / "batch_local_averages.png"
                try:
                    visualization.plot_batch_local_averages(results, local_avg_path)
                    print(f"Batch local averages plot saved: {local_avg_path}")
                except ValueError as e:
                    print(f"Warning: Could not generate local averages plot: {e}", file=sys.stderr)
    
    # Handle legacy CSV options (for backward compatibility)
    if args.output_csv:
        df = results_to_dataframe(results)
        df.to_csv(args.output_csv, index=False)
    if args.local_csv:
        import pandas as pd

        local_records: List[dict] = []
        for res in results:
            if not res.local:
                continue
            for entry in res.local:
                rec = dict(entry)
                rec["path"] = str(res.path)
                local_records.append(rec)
        if local_records:
            pd.DataFrame(local_records).to_csv(args.local_csv, index=False)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Music entropy and redundancy toolkit.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a single file.")
    analyze.add_argument("--input", required=True, help="Path to input file.")
    analyze.add_argument(
        "--input-type", required=True, choices=["midi", "json", "csv"], help="Type of input file."
    )
    analyze.add_argument("--markov-order", type=int, default=1, help="Markov order k.")
    analyze.add_argument("--window-size", type=int, default=16, help="Window size for local metrics.")
    analyze.add_argument("--window-step", type=int, default=8, help="Stride for local metrics.")
    analyze.add_argument("--time-unit", type=float, default=0.25, help="Beat resolution for MIDI rhythm grid.")
    analyze.add_argument("--local", action="store_true", help="Compute local entropies.")
    analyze.add_argument("--output-csv", help="Path to save global metrics CSV.")
    analyze.add_argument("--local-csv", help="Path to save local metrics CSV.")
    analyze.add_argument("--output-json", help="Path to save JSON summary.")
    analyze.add_argument("--plot-dir", help="Directory to store generated PNG plots.")

    analyze_batch = subparsers.add_parser("analyze-batch", help="Analyze all files in a folder.")
    analyze_batch.add_argument("--input", required=True, help="Folder path.")
    analyze_batch.add_argument(
        "--input-type", required=True, choices=["midi", "json", "csv"], help="Input file type to scan."
    )
    analyze_batch.add_argument("--pattern", default="*", help="Glob pattern inside the folder.")
    analyze_batch.add_argument("--markov-order", type=int, default=1, help="Markov order k.")
    analyze_batch.add_argument("--window-size", type=int, default=16, help="Window size for local metrics.")
    analyze_batch.add_argument("--window-step", type=int, default=8, help="Stride for local metrics.")
    analyze_batch.add_argument("--time-unit", type=float, default=0.25, help="Beat resolution for MIDI rhythm grid.")
    analyze_batch.add_argument("--local", action="store_true", help="Compute local entropies.")
    analyze_batch.add_argument("--output-csv", help="Path to save global metrics CSV.")
    analyze_batch.add_argument("--local-csv", help="Path to save local metrics CSV.")
    analyze_batch.add_argument("--plot-dir", help="Directory to store generated PNG plots.")
    analyze_batch.add_argument("--batch-plot", action="store_true", help="Generate a comparison plot for all files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "analyze":
        return handle_analyze(args)
    if args.command == "analyze-batch":
        return handle_analyze_batch(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
