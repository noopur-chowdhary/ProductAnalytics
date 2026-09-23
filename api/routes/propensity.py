from fastapi import APIRouter, Depends

from api.dependencies import result_store
from productpulse.services.results import ResultStore

router = APIRouter()


@router.get("/retailrocket")
def retailrocket_propensity(
    store: ResultStore = Depends(result_store)
):
    """
    Retailrocket propensity results from canonical outputs.
    """

    def optional_records(relative_path: str):
        path = store.path(relative_path)

        if not path.exists():
            return []

        return store.records(relative_path)

    return {
        "selection": optional_records(
            "retailrocket/model_selection.csv"
        ),
        "metrics": optional_records(
            "retailrocket/model_metrics.csv"
        ),
        "ranking": optional_records(
            "retailrocket/selected_ranking.csv"
        ),
        "policy": optional_records(
            "retailrocket/targeting_policy.csv"
        ),
        "result_source": "results/retailrocket",
    }


@router.get("/online-retail")
def online_retail_propensity(store: ResultStore = Depends(result_store)):
    return {
        "selection": store.records("08_behavior_and_customer_prediction/tables/online_retail_model_selection.csv"),
        "metrics": store.records("08_behavior_and_customer_prediction/tables/online_retail_model_metrics.csv"),
        "ranking": store.records("08_behavior_and_customer_prediction/tables/online_retail_selected_ranking.csv"),
        "policy": store.records("10_product_pulse_decision_engine/tables/online_retail_targeting_policy.csv"),
    }
