from fastapi import APIRouter, Depends

from api.dependencies import result_store
from productpulse.services.results import ResultStore

router = APIRouter()


@router.get("/overview")
def overview(store: ResultStore = Depends(result_store)):
    return {
        "decision_cards": store.decision_cards(),
        "decision_registry": store.decision_registry(),
    }
