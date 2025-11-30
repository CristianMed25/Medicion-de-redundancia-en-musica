"""Load melody and rhythm sequences from JSON or CSV files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

import pandas as pd


@dataclass
class TextSequence:
    melody: List[str | int]
    rhythm: List[int]


def _parse_tokens(value: object) -> List[str]:
    """Split a cell value into tokens using commas or whitespace."""
    if isinstance(value, list):
        return [str(v).strip() for v in value]
    text = str(value)
    return [tok for tok in re.split(r"[,\s]+", text) if tok]


def _maybe_int(token: str) -> str | int:
    try:
        return int(token)
    except ValueError:
        return token


def _parse_sequence_cell(value: object) -> List[str | int]:
    tokens = _parse_tokens(value)
    return [_maybe_int(tok) for tok in tokens]


def _load_json(path: Path) -> Tuple[List[str | int], List[int]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "melody" not in data or "rhythm" not in data:
        raise ValueError("JSON must contain 'melody' and 'rhythm' keys.")
    melody = list(data["melody"])
    rhythm = [int(v) for v in data["rhythm"]]
    return melody, rhythm


def _load_csv(path: Path) -> Tuple[List[str | int], List[int]]:
    df = pd.read_csv(path)
    melody: List[str | int] = []
    rhythm: List[int] = []
    # Flexible layout: either columns melody/rhythm or type/sequence
    if {"melody", "rhythm"}.issubset(df.columns):
        for val in df["melody"].dropna().tolist():
            melody.extend(_parse_sequence_cell(val))
        for val in df["rhythm"].dropna().tolist():
            rhythm.extend(int(tok) for tok in _parse_tokens(val))
        return melody, rhythm
    if {"type", "sequence"}.issubset(df.columns):
        for _, row in df.iterrows():
            seq_type = str(row["type"]).strip().lower()
            tokens = _parse_sequence_cell(row["sequence"])
            if seq_type == "melody":
                melody.extend(tokens)
            elif seq_type == "rhythm":
                rhythm.extend(int(tok) for tok in _parse_tokens(row["sequence"]))
        if not melody or not rhythm:
            raise ValueError("CSV with type/sequence must include both melody and rhythm rows.")
        return melody, rhythm
    # Fallback: treat first column as melody and second as rhythm
    if df.shape[1] >= 2:
        melody = _parse_sequence_cell(df.iloc[:, 0].tolist())
        rhythm = [int(tok) for tok in _parse_tokens(df.iloc[:, 1].tolist())]
        return melody, rhythm
    raise ValueError("Unsupported CSV format. Include columns melody/rhythm or type/sequence.")


def load_text_sequence(path: str | Path) -> TextSequence:
    """
    Load symbolic sequences from a JSON or CSV file.

    JSON format example:
        {"melody": ["C4", "D4", "E4"], "rhythm": [1, 1, 0]}

    CSV options:
        melody,rhythm
        C4 D4 E4,"1 1 0"
    or:
        type,sequence
        melody,"C4,D4,E4"
        rhythm,"1,1,0"
    """
    text_path = Path(path)
    if not text_path.exists():
        raise FileNotFoundError(f"Text file not found: {text_path}")

    suffix = text_path.suffix.lower()
    if suffix == ".json":
        melody, rhythm = _load_json(text_path)
    elif suffix == ".csv":
        melody, rhythm = _load_csv(text_path)
    else:
        raise ValueError("Unsupported text format. Use .json or .csv.")

    return TextSequence(melody=melody, rhythm=rhythm)
