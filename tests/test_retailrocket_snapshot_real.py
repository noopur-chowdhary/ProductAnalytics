import numpy as np
import pandas as pd
import pytest

from productpulse.data.cleaning import clean_retailrocket_events
from productpulse.features.retailrocket import build_retailrocket_snapshot


RAW_PATH = "data/raw/retailrocket/events.csv"

CUTOFF = pd.Timestamp("2015-08-08", tz="UTC")
HISTORY_START = CUTOFF - pd.Timedelta(days=21)
RECENT_START = CUTOFF - pd.Timedelta(days=7)
LABEL_END = CUTOFF + pd.Timedelta(days=7)


@pytest.fixture(scope="module")
def events():
    start_ms = int(HISTORY_START.timestamp() * 1000)
    end_ms = int(LABEL_END.timestamp() * 1000)

    parts = []

    for chunk in pd.read_csv(
        RAW_PATH,
        chunksize=250_000,
    ):
        keep = chunk[
            (chunk["timestamp"] >= start_ms)
            & (chunk["timestamp"] < end_ms)
        ]

        if not keep.empty:
            parts.append(keep)

    raw = pd.concat(parts, ignore_index=True)

    return clean_retailrocket_events(raw)


@pytest.fixture(scope="module")
def snapshot(events):
    return build_retailrocket_snapshot(
        events,
        cutoff=CUTOFF,
        split_name="integration_test",
    )


def test_snapshot_time_boundaries(snapshot):
    assert len(snapshot) > 0

    assert snapshot["prediction_cutoff"].eq(CUTOFF).all()
    assert snapshot["label_end"].eq(LABEL_END).all()

    assert (
        snapshot["first_event_21d"] >= HISTORY_START
    ).all()

    assert (
        snapshot["last_event_21d"] < CUTOFF
    ).all()


def test_snapshot_counts_against_raw_events(events, snapshot):
    visitor_ids = (
        snapshot
        .nlargest(10, "events_21d")["visitorid"]
        .tolist()
    )

    for visitor_id in visitor_ids:
        row = snapshot.loc[
            snapshot["visitorid"] == visitor_id
        ].iloc[0]

        visitor_events = events.loc[
            events["visitorid"] == visitor_id
        ]

        history = visitor_events.loc[
            (visitor_events["event_time"] >= HISTORY_START)
            & (visitor_events["event_time"] < CUTOFF)
        ]

        recent = history.loc[
            history["event_time"] >= RECENT_START
        ]

        future = visitor_events.loc[
            (visitor_events["event_time"] >= CUTOFF)
            & (visitor_events["event_time"] < LABEL_END)
        ]

        assert row["events_21d"] == len(history)
        assert row["unique_items_21d"] == history["itemid"].nunique()

        assert row["views_21d"] == (history["event"] == "view").sum()
        assert row["carts_21d"] == (history["event"] == "addtocart").sum()
        assert row["transactions_21d"] == (history["event"] == "transaction").sum()

        assert row["views_7d"] == (recent["event"] == "view").sum()
        assert row["carts_7d"] == (recent["event"] == "addtocart").sum()
        assert row["transactions_7d"] == (recent["event"] == "transaction").sum()

        future_transactions = (
            future["event"] == "transaction"
        ).sum()

        assert row["future_transactions_7d"] == future_transactions
        assert row["target_future_transaction"] == int(future_transactions > 0)


def test_future_event_does_not_change_features(events, snapshot):
    negative_row = snapshot.loc[
        snapshot["target_future_transaction"] == 0
    ].iloc[0]

    visitor_id = int(negative_row["visitorid"])

    fake_future_event = pd.DataFrame(
        {
            "timestamp": [
                int(CUTOFF.timestamp() * 1000)
            ],
            "visitorid": [visitor_id],
            "event": ["transaction"],
            "itemid": [999999999],
            "transactionid": [999999999],
            "event_time": [CUTOFF],
        }
    )

    modified_events = pd.concat(
        [events, fake_future_event],
        ignore_index=True,
    )

    modified_snapshot = build_retailrocket_snapshot(
        modified_events,
        cutoff=CUTOFF,
        split_name="integration_test",
    )

    before = snapshot.loc[
        snapshot["visitorid"] == visitor_id
    ].iloc[0]

    after = modified_snapshot.loc[
        modified_snapshot["visitorid"] == visitor_id
    ].iloc[0]

    feature_columns = [
        "events_21d",
        "unique_items_21d",
        "views_21d",
        "carts_21d",
        "transactions_21d",
        "views_7d",
        "carts_7d",
        "transactions_7d",
        "recency_hours",
        "active_span_days_21d",
        "cart_per_view_21d",
        "transaction_per_view_21d",
    ]

    for column in feature_columns:
        before_value = before[column]
        after_value = after[column]

        if pd.isna(before_value):
            assert pd.isna(after_value)
        else:
            assert np.isclose(
                before_value,
                after_value,
            )

    assert before["target_future_transaction"] == 0
    assert after["target_future_transaction"] == 1

    assert (
        after["future_transactions_7d"]
        == before["future_transactions_7d"] + 1
    )
