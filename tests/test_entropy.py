import math

from music_entropy import entropy


def test_shannon_constant_zero_entropy():
    seq = [1] * 20
    assert entropy.shannon_entropy(seq) == 0.0


def test_shannon_uniform_matches_log2():
    seq = [0, 1, 2, 3] * 5
    h0 = entropy.shannon_entropy(seq)
    assert math.isclose(h0, math.log2(4), rel_tol=0.05)


def test_markov_entropy_reduces_on_deterministic_pattern():
    seq = [0, 1] * 20  # alternancia determinista
    h0 = entropy.shannon_entropy(seq)
    hk = entropy.markov_entropy(seq, order_k=1)
    assert h0 > hk
    assert hk == 0.0
