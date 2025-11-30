import json

import mido
import pandas as pd

from music_entropy import loader_midi, loader_text


def test_load_json(tmp_path):
    payload = {"melody": ["C4", "D4", "E4"], "rhythm": [1, 1, 0]}
    path = tmp_path / "toy.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    seq = loader_text.load_text_sequence(path)
    assert seq.melody == payload["melody"]
    assert seq.rhythm == payload["rhythm"]


def test_load_csv_columns(tmp_path):
    path = tmp_path / "toy.csv"
    df = pd.DataFrame({"melody": ["C4 D4 E4"], "rhythm": ["1 1 0"]})
    df.to_csv(path, index=False)
    seq = loader_text.load_text_sequence(path)
    assert seq.melody[:3] == ["C4", "D4", "E4"]
    assert seq.rhythm == [1, 1, 0]


def test_load_simple_midi(tmp_path):
    path = tmp_path / "toy.mid"
    mid = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.Message("note_on", note=60, velocity=90, time=0))
    track.append(mido.Message("note_off", note=60, velocity=0, time=480))
    mid.save(path)

    seq = loader_midi.load_midi(path, time_unit=0.25)
    assert seq.melody == [60]
    assert any(seq.rhythm)
