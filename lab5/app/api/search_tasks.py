from fastapi import APIRouter
from app.services.tasks import run_fuzzy_search

router = APIRouter()

# Заглушка корпуса
FAKE_CORPUSES = {
    1: ["example", "sample", "temple", "apple", "examine"]
}

@router.post("/start_search")
def start_search(word: str, algorithm: str = "levenshtein", corpus_id: int = 1):
    corpus = FAKE_CORPUSES.get(corpus_id, [])
    task = run_fuzzy_search.delay(word, corpus, algorithm)
    return {"task_id": task.id}

@router.get("/task_result/{task_id}")
def get_result(task_id: str):
    from app.services.tasks import celery
    task = celery.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "pending"}
    elif task.state == "SUCCESS":
        return {"status": "done", "result": task.result}
    else:
        return {"status": task.state}
