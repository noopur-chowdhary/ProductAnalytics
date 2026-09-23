from productpulse.experimentation.ab_testing import choose_experiment_action


def test_significant_negative_effect_keeps_control():
    assert choose_experiment_action(-0.008, 0.0016) == "keep_control"


def test_non_significant_effect_has_no_clear_winner():
    assert choose_experiment_action(0.003, 0.20) == "no_clear_winner"
