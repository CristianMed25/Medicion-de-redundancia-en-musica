"""Funciones de alto nivel para análisis de piezas o carpetas."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import pandas as pd

from . import encoding, entropy, lzc, loader_midi, loader_text


@dataclass
class AnalysisConfig:
    markov_order: int = 1
    window_size: int = 16
    window_step: int = 8
    time_unit: float = 0.25
    compute_local: bool = False


@dataclass
class AnalysisResult:
    path: Path
    h0: float
    hk: float
    hmax: float
    redundancy: float
    lzc: float
    lzc_normalized: float
    ip: float
    local: Optional[List[Dict[str, float]]] = None

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["path"] = str(self.path)
        return data


def _load_sequences(path: Path, input_type: str, config: AnalysisConfig) -> tuple[list[object], list[int]]:
    input_type = input_type.lower()
    if input_type == "midi":
        midi_seq = loader_midi.load_midi(path, time_unit=config.time_unit)
        return encoding.standardize_melody(midi_seq.melody), encoding.standardize_rhythm(midi_seq.rhythm)
    if input_type in {"json", "csv", "text"}:
        text_seq = loader_text.load_text_sequence(path)
        return encoding.standardize_melody(text_seq.melody), encoding.standardize_rhythm(text_seq.rhythm)
    raise ValueError(f"Unsupported input_type: {input_type}")


def analyze_piece(path: str | Path, input_type: str, config: Optional[AnalysisConfig] = None) -> AnalysisResult:
    """Analyze a single piece and compute all metrics."""
    cfg = config or AnalysisConfig()
    piece_path = Path(path)
    melody, rhythm = _load_sequences(piece_path, input_type, cfg)

    h0 = entropy.shannon_entropy(melody)
    hk = entropy.markov_entropy(melody, cfg.markov_order)
    hmax = entropy.max_entropy(len(set(melody)))
    red = entropy.redundancy(hmax, hk)
    lzc_val = lzc.lempel_ziv_complexity(rhythm)
    lzc_norm = lzc.normalized_lzc(rhythm)
    ip = entropy.predictability_index(hk, hmax)

    local_metrics: Optional[List[Dict[str, float]]] = None
    if cfg.compute_local:
        windows = entropy.sliding_window_entropies(
            melody, window_size=cfg.window_size, step=cfg.window_step, order_k=cfg.markov_order
        )
        local_metrics = [{"window": idx, "h0": h0_w, "hk": hk_w} for idx, (h0_w, hk_w) in enumerate(windows)]

    return AnalysisResult(
        path=piece_path,
        h0=h0,
        hk=hk,
        hmax=hmax,
        redundancy=red,
        lzc=lzc_val,
        lzc_normalized=lzc_norm,
        ip=ip,
        local=local_metrics,
    )


def analyze_folder(
    folder: str | Path,
    input_type: str,
    config: Optional[AnalysisConfig] = None,
    pattern: str = "*",
) -> List[AnalysisResult]:
    """Analyze all compatible files in a folder."""
    cfg = config or AnalysisConfig()
    base = Path(folder)
    if not base.exists():
        raise FileNotFoundError(f"Folder not found: {base}")
    results: List[AnalysisResult] = []
    for path in sorted(base.glob(pattern)):
        if path.is_dir():
            continue
        if input_type == "midi" and path.suffix.lower() not in {".mid", ".midi"}:
            continue
        if input_type in {"json", "csv"} and path.suffix.lower() != f".{input_type}":
            continue
        res = analyze_piece(path, input_type=input_type, config=cfg)
        results.append(res)
    return results


def results_to_dataframe(results: Sequence[AnalysisResult]) -> pd.DataFrame:
    """Convert results list to pandas DataFrame."""
    data = [r.to_dict() for r in results]
    return pd.DataFrame(data)
