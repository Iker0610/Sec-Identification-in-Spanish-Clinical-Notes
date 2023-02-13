"""
Boundary Similarity (B) package.

.. moduleauthor:: Chris Fournier <chris.m.fournier@gmail.com>
"""
from __future__ import absolute_import, division
from segeval.similarity import __boundary_statistics__, SIMILARITY_METRIC_DEFAULTS
from segeval.util import __fnc_metric__
from decimal import Decimal


def __boundary_similarity__(*args, **kwargs):
    metric_kwargs = dict(kwargs)
    del metric_kwargs['return_parts']
    del metric_kwargs['one_minus']
    # Arguments
    return_parts = kwargs['return_parts']
    one_minus = kwargs['one_minus']
    # Compute
    statistics = __boundary_statistics__(*args, **metric_kwargs)
    additions = statistics['additions']
    substitutions = statistics['substitutions']
    transpositions = statistics['transpositions']
    count_unweighted = len(additions) + len(substitutions) + len(transpositions)
    # Fraction
    denominator = count_unweighted + len(statistics['matches'])
    numerator = denominator - statistics['count_edits']
    if return_parts:
        return numerator, denominator, additions, substitutions, transpositions
    else:
        value = numerator / denominator if denominator > 0 else 1
        if one_minus:
            return Decimal('1') - value
        else:
            return value


def __boundary_similarity_2__(*args, **kwargs):
    metric_kwargs = dict(kwargs)
    del metric_kwargs['return_parts']
    del metric_kwargs['one_minus']

    # Arguments
    return_parts = kwargs['return_parts']
    one_minus = kwargs['one_minus']
    return_statistics = kwargs.get('return_statistics', False)
    if 'return_statistics' in metric_kwargs:
        del metric_kwargs['return_statistics']

    # Compute
    statistics = __boundary_statistics__(*args, **metric_kwargs)
    additions = statistics['additions']
    substitutions = statistics['substitutions']
    transpositions = statistics['transpositions']
    count_unweighted = len(additions) + len(substitutions) + len(transpositions)
    # Fraction
    denominator = count_unweighted + len(statistics['matches']) + (len(transpositions) - statistics['weighted_transpositions'])
    numerator = denominator - statistics['count_edits']
    if numerator < 0: numerator = 0

    if return_parts:
        return numerator, int(denominator), additions, substitutions, transpositions
    else:
        value = numerator / denominator if denominator > 0 else 1

        value = Decimal('1') - value if one_minus else value
        if return_statistics:
            return value, statistics
        else:
            return value


def boundary_similarity(*args, **kwargs):
    """
    Boundary Similarity (B).
    """

    return __fnc_metric__(__boundary_similarity__, args, kwargs,
                          SIMILARITY_METRIC_DEFAULTS)


def boundary_similarity_2(*args, **kwargs):
    """
    Boundary Similarity (B2).
    """

    return __fnc_metric__(__boundary_similarity_2__, args, kwargs,
                          SIMILARITY_METRIC_DEFAULTS)
