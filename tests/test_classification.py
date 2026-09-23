import numpy as np

from productpulse.evaluation.classification import lift_at_fraction, precision_at_fraction, recall_at_fraction


def test_top_fraction_metrics():
    y = np.array([1, 0, 1, 0])
    score = np.array([0.9, 0.8, 0.7, 0.1])
    assert precision_at_fraction(y, score, 0.5) == 0.5
    assert recall_at_fraction(y, score, 0.5) == 0.5
    assert lift_at_fraction(y, score, 0.5) == 1.0
