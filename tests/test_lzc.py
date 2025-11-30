from music_entropy import lzc


def test_lzc_constant_low_complexity():
    seq = [0] * 32
    assert lzc.lempel_ziv_complexity(seq) <= 2
    assert lzc.normalized_lzc(seq) < 0.4


def test_lzc_random_higher_than_periodic():
    periodic = [0, 1] * 16
    randomish = [0, 1, 1, 0, 1, 0, 0, 1] * 4
    assert lzc.lempel_ziv_complexity(randomish) > lzc.lempel_ziv_complexity(periodic)
