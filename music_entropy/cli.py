"""Command line interface for music entropy analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

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
    return 0


def handle_analyze_batch(args: argparse.Namespace) -> int:
    cfg = _config_from_args(args)
    results = analyze_folder(args.input, input_type=args.input_type, config=cfg, pattern=args.pattern)
    if not results:
        print("No files processed.", file=sys.stderr)
        return 1
    for res in results:
        _print_result(res)
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
