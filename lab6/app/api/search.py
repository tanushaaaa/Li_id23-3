from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.cruds.corpus import get_corpus_by_id
from app.core.security import get_current_user
from app.models.user import User
from app.services.fuzzy_search import FuzzySearchService
from app.celery.tasks import fuzzy_search_task

router = APIRouter()


@router.post("/search_algorithm", response_model=SearchResponse)
def search_algorithm(
    search_request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Выполняет поиск с указанным алгоритмом (синхронная версия)"""
    # Проверяем существование корпуса
    corpus = get_corpus_by_id(db, search_request.corpus_id, current_user.id)
    if not corpus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corpus not found"
        )
    
    # Проверяем поддерживаемые алгоритмы
    available_algorithms = FuzzySearchService.get_available_algorithms()
    if search_request.algorithm not in available_algorithms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported algorithm. Available: {available_algorithms}"
        )
    
    # Выполняем поиск
    results, execution_time = FuzzySearchService.search_with_algorithm(
        search_request.word,
        corpus.text,
        search_request.algorithm
    )
    
    return SearchResponse(
        execution_time=execution_time,
        results=results
    )


@router.post("/search_algorithm_async")
def search_algorithm_async(
    search_request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Запускает асинхронный поиск с уведомлениями через WebSocket"""
    # Проверяем существование корпуса
    corpus = get_corpus_by_id(db, search_request.corpus_id, current_user.id)
    if not corpus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Corpus not found"
        )
    
    # Проверяем поддерживаемые алгоритмы
    available_algorithms = FuzzySearchService.get_available_algorithms()
    if search_request.algorithm not in available_algorithms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported algorithm. Available: {available_algorithms}"
        )
    
    # Запускаем задачу Celery
    task = fuzzy_search_task.delay(
        search_request.word,
        search_request.algorithm,
        corpus.text,
        current_user.id
    )
    
    return {
        "message": "Search task started",
        "task_id": task.id,
        "status": "PENDING"
    } 