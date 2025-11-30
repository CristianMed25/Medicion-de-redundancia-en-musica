"""MIDI loader to extract melody and rhythmic grid."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import mido


@dataclass
class MidiSequence:
    melody: List[int]
    rhythm: List[int]


def _select_melody_track(mid: mido.MidiFile) -> int:
    """Choose the track with the largest number of note_on events."""
    best_index = 0
    best_count = -1
    for idx, track in enumerate(mid.tracks):
        count = sum(1 for msg in track if msg.type == "note_on" and msg.velocity > 0)
        if count > best_count:
            best_index = idx
            best_count = count
    return best_index


def _collect_intervals(track: mido.MidiTrack, ticks_per_beat: int) -> Tuple[List[int], List[Tuple[float, float]]]:
    """Return melody note list and (start, end) intervals in beats."""
    melody: List[int] = []
    intervals: List[Tuple[float, float]] = []
    time_acc = 0
    active: Dict[int, float] = {}

    for msg in track:
        time_acc += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            start = time_acc / ticks_per_beat
            melody.append(msg.note)
            active[msg.note] = start
        elif msg.type in {"note_off", "note_on"} and (msg.type == "note_off" or msg.velocity == 0):
            if msg.note in active:
                start = active.pop(msg.note)
                end = time_acc / ticks_per_beat
                intervals.append((start, end))
    # Close any hanging notes at track end
    end_time = time_acc / ticks_per_beat
    for start in active.values():
        intervals.append((start, end_time))
    return melody, intervals


def _intervals_to_rhythm(intervals: List[Tuple[float, float]], total_beats: float, time_unit: float) -> List[int]:
    """Convert note intervals to a binary activation grid."""
    if time_unit <= 0:
        raise ValueError("time_unit must be positive.")
    n_steps = max(1, int((total_beats / time_unit) + 1))
    rhythm = [0 for _ in range(n_steps)]
    for start, end in intervals:
        start_idx = max(0, int(start / time_unit))
        end_idx = max(start_idx + 1, int((end / time_unit) + 0.9999))
        for idx in range(start_idx, min(end_idx, n_steps)):
            rhythm[idx] = 1
    return rhythm


def load_midi(path: str | Path, time_unit: float = 0.25, track_index: Optional[int] = None) -> MidiSequence:
    """
    Load a MIDI file and return discrete melody and rhythm sequences.

    Args:
        path: Path to the MIDI file.
        time_unit: Temporal resolution in beats (e.g., 0.25 for sixteenth notes).
        track_index: Optional track to extract. If None, chooses the most active track.

    Returns:
        MidiSequence with melody pitches and binary rhythm.
    """
    midi_path = Path(path)
    if not midi_path.exists():
        raise FileNotFoundError(f"MIDI file not found: {midi_path}")

    mid = mido.MidiFile(midi_path)
    idx = _select_melody_track(mid) if track_index is None else track_index
    if idx < 0 or idx >= len(mid.tracks):
        raise ValueError(f"track_index {idx} out of bounds for MIDI with {len(mid.tracks)} tracks.")

    melody, intervals = _collect_intervals(mid.tracks[idx], mid.ticks_per_beat)
    total_beats = max((end for _, end in intervals), default=0.0)
    rhythm = _intervals_to_rhythm(intervals, total_beats, time_unit)
    return MidiSequence(melody=melody, rhythm=rhythm)
