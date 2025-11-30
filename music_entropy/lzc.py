"""Complejidad de Lempel-Ziv para secuencias binarias."""

from __future__ import annotations

import math
from typing import Iterable, List


def _to_binary_string(sequence: Iterable[int | bool]) -> str:
    return "".join("1" if int(v) > 0 else "0" for v in sequence)


def lempel_ziv_complexity(binary_sequence: Iterable[int | bool]) -> int:
    """
    Lempel-Ziv complexity (LZ76) for a binary sequence using a simple substring parser.
    """
    s = _to_binary_string(binary_sequence)
    n = len(s)
    if n == 0:
        return 0
    if n == 1:
        return 1
    c = 1
    i = 0
    k = 1
    l = 1
    while True:
        if l + k > n:
            c += 1
            break
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
        else:
            i += 1
            if i == l:
                c += 1
                l += k
                if l >= n:
                    break
                i = 0
                k = 1
    return c


def normalized_lzc(binary_sequence: Iterable[int | bool]) -> float:
    """
    Normalized LZC: c(n) * log2(n) / n, capped at 1.0.
    """
    s = list(binary_sequence)
    n = len(s)
    if n == 0:
        return 0.0
    c = lempel_ziv_complexity(s)
    norm = (c * math.log2(n)) / n
    return min(1.0, norm)
