"""Homologación de secuencias simbólicas."""

from __future__ import annotations

import re
from typing import Iterable, List, Tuple


NOTE_BASE = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}


def note_name_to_midi(note: str) -> int | None:
    """Convert note name like C#4 or Db3 to MIDI number. Returns None if invalid."""
    match = re.match(r"^([A-Ga-g])([#b]?)(-?\d+)$", note.strip())
    if not match:
        return None
    base = NOTE_BASE[match.group(1).upper()]
    accidental = match.group(2)
    if accidental == "#":
        base += 1
    elif accidental == "b":
        base -= 1
    octave = int(match.group(3))
    return (octave + 1) * 12 + base


def standardize_melody(melody: Iterable[str | int]) -> List[str | int]:
    """Map note names to MIDI integers when possible."""
    standardized: List[str | int] = []
    for item in melody:
        if isinstance(item, int):
            standardized.append(item)
            continue
        try:
            num = int(str(item))
            standardized.append(num)
            continue
        except ValueError:
            pass
        midi_val = note_name_to_midi(str(item))
        standardized.append(midi_val if midi_val is not None else str(item))
    return standardized


def standardize_rhythm(rhythm: Iterable[int | float | str]) -> List[int]:
    """Force rhythm to binary sequence."""
    clean: List[int] = []
    for item in rhythm:
        try:
            val = int(float(item))
        except (ValueError, TypeError):
            val = 0
        clean.append(1 if val > 0 else 0)
    return clean


def encode_sequences(melody: Iterable[str | int], rhythm: Iterable[int | float | str]) -> Tuple[List[str | int], List[int]]:
    """Return standardized melody and rhythm sequences."""
    return standardize_melody(melody), standardize_rhythm(rhythm)
