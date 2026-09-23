import json

from fastapi import APIRouter, Depends

from api.dependencies import result_store
from productpulse.services.results import ResultStore


router = APIRouter()


def optional_records(store: ResultStore, relative_path: str):
    path = store.path(relative_path)

    if not path.exists():
        return []

    return store.records(relative_path)


@router.get("/criteo")
def criteo_uplift(store: ResultStore = Depends(result_store)):
    """
    Dashboard-facing Criteo uplift results.

    Primary results come from the canonical CLI output:
        results/criteo/

    Older notebook outputs are temporarily retained only for
    supplemental model/policy tables.
    """

    summary_path = store.path("criteo/summary.json")
    targeting_path = store.path("criteo/targeting_table.csv")

    summary = {}

    if summary_path.exists():
        summary = json.loads(summary_path.read_text())

    targeting = []

    if targeting_path.exists():
        targeting = store.records("criteo/targeting_table.csv")

    return {
        "summary": summary,
        "targeting": targeting,

        # Transitional supplemental outputs.
        # We will move these to canonical folders next.
        "model_selection": optional_records(
            store,
            "09_criteo_uplift_modeling/tables/model_selection.csv",
        ),
        "metrics": optional_records(
            store,
            "09_criteo_uplift_modeling/tables/model_metrics.csv",
        ),
        "deciles": optional_records(
            store,
            "09_criteo_uplift_modeling/tables/uplift_deciles.csv",
        ),
        "policy": optional_records(
            store,
            "10_product_pulse_decision_engine/tables/criteo_causal_targeting_policy.csv",
        ),

        "result_source": "results/criteo",
    }
