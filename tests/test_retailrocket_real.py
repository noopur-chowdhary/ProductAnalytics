import pandas as pd

from productpulse.data.cleaning import clean_retailrocket_events


RAW_PATH = "data/raw/retailrocket/events.csv"


def test_retailrocket_real_cleaning():
    # Use a real 50k-row slice so the test stays fast
    raw = pd.read_csv(RAW_PATH, nrows=50_000)

    clean = clean_retailrocket_events(raw)

    # ---------------------------------------------------------
    # Basic output checks
    # ---------------------------------------------------------
    assert isinstance(clean, pd.DataFrame)
    assert len(clean) > 0
    assert len(clean) <= len(raw)

    # ---------------------------------------------------------
    # Required columns
    # ---------------------------------------------------------
    required = {
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid",
        "event_time",
    }

    assert required.issubset(clean.columns)

    # ---------------------------------------------------------
    # Required fields should not be missing
    # ---------------------------------------------------------
    assert clean["timestamp"].notna().all()
    assert clean["visitorid"].notna().all()
    assert clean["event"].notna().all()
    assert clean["itemid"].notna().all()
    assert clean["event_time"].notna().all()

    # transactionid is allowed to be null for views/add-to-cart
    assert str(clean["transactionid"].dtype) == "Int64"

    # ---------------------------------------------------------
    # Event types
    # ---------------------------------------------------------
    valid_events = {
        "view",
        "addtocart",
        "transaction",
    }

    assert set(clean["event"].unique()).issubset(valid_events)

    # ---------------------------------------------------------
    # Timestamp conversion
    # ---------------------------------------------------------
    assert isinstance(
        clean["event_time"].dtype,
        pd.DatetimeTZDtype,
    )

    assert str(clean["event_time"].dt.tz) == "UTC"

    # Verify timestamp -> datetime conversion
    expected_time = pd.to_datetime(
        clean["timestamp"],
        unit="ms",
        utc=True,
    )

    assert clean["event_time"].equals(expected_time)

    # ---------------------------------------------------------
    # Duplicates
    # ---------------------------------------------------------
    assert clean.duplicated().sum() == 0

    # ---------------------------------------------------------
    # Sanity checks
    # ---------------------------------------------------------
    assert (clean["visitorid"] >= 0).all()
    assert (clean["itemid"] >= 0).all()


def test_retailrocket_transaction_ids():
    raw = pd.read_csv(RAW_PATH, nrows=50_000)

    clean = clean_retailrocket_events(raw)

    transactions = clean[
        clean["event"] == "transaction"
    ]

    # Actual transaction events should have transaction IDs
    assert len(transactions) > 0
    assert transactions["transactionid"].notna().all()
