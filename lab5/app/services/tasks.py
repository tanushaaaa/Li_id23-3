from celery import Celery
from app.services.fuzzy import fuzzy_search
from app.core.config import REDIS_URL

celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery.task
def run_fuzzy_search(word: str, corpus: list[str], algorithm: str = "levenshtein"):
    return fuzzy_search(word, corpus, algorithm)
