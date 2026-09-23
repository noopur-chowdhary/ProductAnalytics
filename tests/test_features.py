import pandas as pd

from productpulse.features.retailrocket import build_retailrocket_snapshot


def test_retailrocket_snapshot_does_not_use_future_events_as_features():
    cutoff = pd.Timestamp("2026-01-22", tz="UTC")
    rows = [
        {"visitorid": 1, "itemid": 10, "event": "view", "event_time": cutoff - pd.Timedelta(days=1)},
        {"visitorid": 1, "itemid": 10, "event": "transaction", "event_time": cutoff + pd.Timedelta(days=1)},
    ]
    df = pd.DataFrame(rows)
    out = build_retailrocket_snapshot(df, cutoff, "test")
    row = out.iloc[0]
    assert row["events_21d"] == 1
    assert row["transactions_21d"] == 0
    assert row["target_future_transaction"] == 1
