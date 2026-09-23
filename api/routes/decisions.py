from fastapi import APIRouter, Depends

from api.dependencies import result_store
from productpulse.services.results import ResultStore

router = APIRouter()


@router.get("/decisions")
def decisions(store: ResultStore = Depends(result_store)):
    return {
        "cards": store.decision_cards(),
        "registry": store.decision_registry(),
        "guardrails": store.records("10_product_pulse_decision_engine/tables/production_guardrails.csv"),
    }
