import numpy as np

from productpulse.evaluation.uplift import targeting_table


def test_targeting_table_has_full_population_row():
    y = np.array([1, 0, 1, 0, 1, 0])
    t = np.array([1, 0, 1, 0, 1, 0])
    score = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4])
    table = targeting_table(y, t, score)
    assert float(table.iloc[-1]["target_fraction"]) == 1.0
    assert int(table.iloc[-1]["rows"]) == len(y)
