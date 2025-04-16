from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from app.services.fuzzy import fuzzy_search
import time

router = APIRouter()

# Простая заглушка корпуса
FAKE_CORPUSES = {
    1: ["example", "sample", "temple", "apple", "examine", "expletive"]
}

class SearchRequest(BaseModel):
    word: str
    algorithm: Literal["levenshtein", "damerau"]
    corpus_id: int

class SearchResult(BaseModel):
    word: str
    distance: int

class SearchResponse(BaseModel):
    execution_time: float
    results: List[SearchResult]

@router.post("/search_algorithm", response_model=SearchResponse)
def search_fuzzy(req: SearchRequest):
    corpus = FAKE_CORPUSES.get(req.corpus_id)
    if not corpus:
        raise HTTPException(status_code=404, detail="Corpus not found")

    start = time.time()
    results = fuzzy_search(req.word, corpus, req.algorithm)
    end = time.time()

    return {
        "execution_time": round(end - start, 4),
        "results": results
    }
