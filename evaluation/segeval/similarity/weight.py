"""
Weighting functions for edit operations produced by boundary edit distance.

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
"""
import math
from decimal import Decimal


def weight_a(additions):
    """
    Default unweighted weighting function for addition edit operations.
    """
    return len(additions)


def weight_s(substitutions, max_s, min_s=1):
    """
    Unweighted weighting function for substitution edit operations.
    """

    return len(substitutions)


def weight_s_scale(substitutions, max_s, min_s=1):
    """
    Default weighting function for substitution edit operations by the distance between ordinal boundary types.
    """

    return weight_t_scale(substitutions, max_s - min_s + 1)


def weight_t(transpositions, max_n):
    """
    Unweighted weighting function for transposition edit operations.
    """

    return len(transpositions)


def weight_t_scale(transpositions, max_n):
    """
    Default weighting function for transposition edit operations by the distance that transpositions span.
    """
    numerator = 0
    for transposition in transpositions:
        numerator += abs(transposition[0] - transposition[1])
    return Decimal(numerator) / max_n


# ----------------------------------------------------------------

def custom_weight_a(additions):
    additions = len(additions)

    def weight(x):
        return 0.75 + (math.tanh((x - 1.5) - 2) / 4)

    return additions * weight(additions) if additions else 0


def custom_weight_s(*args, **kwargs):
    return 1.3 * weight_s(*args, **kwargs)


def custom_weight_t(transpositions, max_n):
    def weight(x):
        return 0.35 + (math.tanh(x / 10) / 3)

    numerator = 0
    for transposition in transpositions:
        num_tokens_moved = abs(transposition[0] - transposition[1])
        numerator += 0 if num_tokens_moved <= 2 else weight(num_tokens_moved - 15)
    return numerator


custom_weights = (custom_weight_a, custom_weight_s, custom_weight_t)
B2_parameters = {
    'weight': custom_weights,
    'n_t': 40
}
