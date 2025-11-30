from music_entropy import encoding


def test_note_name_to_midi_basic():
    assert encoding.note_name_to_midi("C4") == 60
    assert encoding.note_name_to_midi("A4") == 69
    assert encoding.note_name_to_midi("F#3") == 54
    assert encoding.note_name_to_midi("Db5") == 73


def test_standardize_sequences_convert_and_keep():
    melody = ["C4", "61", "X1"]
    rhythm = [1, 0, "1", "0", 2]
    mel_clean, r_clean = encoding.encode_sequences(melody, rhythm)
    assert mel_clean[0] == 60
    assert mel_clean[1] == 61
    assert mel_clean[2] == "X1"
    assert r_clean == [1, 0, 1, 0, 1]
