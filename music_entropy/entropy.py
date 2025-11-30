"""Funciones de entropía y redundancia."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Iterable, List, Sequence, Tuple


def shannon_entropy(sequence: Sequence[object]) -> float:
    """Order-0 Shannon entropy in bits."""
    if not sequence:
        return 0.0
    counts = Counter(sequence)
    total = len(sequence)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def markov_entropy(sequence: Sequence[object], order_k: int) -> float:
    """Conditional entropy estimate using Markov model of order k."""
    if order_k <= 0:
        return shannon_entropy(sequence)
    n = len(sequence)
    if n <= order_k:
        return 0.0
    transitions = defaultdict(list)
    for idx in range(n - order_k):
        context = tuple(sequence[idx : idx + order_k])
        next_symbol = sequence[idx + order_k]
        transitions[context].append(next_symbol)
    total = n - order_k
    entropy = 0.0
    for next_symbols in transitions.values():
        weight = len(next_symbols) / total
        entropy += weight * shannon_entropy(next_symbols)
    return entropy


def max_entropy(alphabet_size: int) -> float:
    """Maximum entropy for a uniform distribution on alphabet_size symbols."""
    if alphabet_size <= 0:
        return 0.0
    return math.log2(alphabet_size)


def redundancy(h_max: float, h_star: float) -> float:
    """Redundancy R = Hmax - H* (no negativa)."""
    return max(0.0, h_max - h_star)


def predictability_index(h_star_eff: float, h_max: float) -> float:
    """IP = 1 - (H* / Hmax) en rango [0,1]."""
    if h_max <= 0:
        return 0.0
    ip = 1.0 - (h_star_eff / h_max)
    return min(1.0, max(0.0, ip))


def sliding_window_entropies(
    sequence: Sequence[object],
    window_size: int,
    step: int,
    order_k: int = 1,
) -> List[Tuple[float, float]]:
    """Compute H0 and Hk for ventanas deslizantes."""
    if window_size <= 0 or step <= 0:
        raise ValueError("window_size and step must be positive integers.")
    results: List[Tuple[float, float]] = []
    n = len(sequence)
    for start in range(0, n, step):
        window = sequence[start : start + window_size]
        if not window:
            continue
        h0 = shannon_entropy(window)
        hk = markov_entropy(window, order_k)
        results.append((h0, hk))
    return results
