from pydantic import BaseModel
from typing import List, Optional


class SearchRequest(BaseModel):
    word: str
    algorithm: str
    corpus_id: int


class SearchResult(BaseModel):
    word: str
    distance: int


class SearchResponse(BaseModel):
    execution_time: float
    results: List[SearchResult]


class WebSocketMessage(BaseModel):
    status: str
    task_id: str
    word: Optional[str] = None
    algorithm: Optional[str] = None
    progress: Optional[int] = None
    current_word: Optional[str] = None
    execution_time: Optional[float] = None
    results: Optional[List[SearchResult]] = None 