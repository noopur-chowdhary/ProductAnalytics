from functools import lru_cache

from productpulse.services.results import ResultStore


@lru_cache
def result_store() -> ResultStore:
    return ResultStore()
