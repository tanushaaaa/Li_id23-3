from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.corpus import CorpusCreate, CorpusResponse, CorpusList, CorpusInfo
from app.cruds.corpus import create_corpus, get_corpuses_by_user
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/upload_corpus", response_model=CorpusResponse)
def upload_corpus(
    corpus: CorpusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Загружает корпус текста для индексации и поиска"""
    db_corpus = create_corpus(db=db, corpus=corpus, user_id=current_user.id)
    
    return CorpusResponse(
        corpus_id=db_corpus.id,
        message="Corpus uploaded successfully"
    )


@router.get("/corpuses", response_model=CorpusList)
def get_corpuses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Возвращает список корпусов с идентификаторами"""
    corpuses = get_corpuses_by_user(db=db, user_id=current_user.id)
    
    corpus_list = [
        CorpusInfo(id=corpus.id, name=corpus.name)
        for corpus in corpuses
    ]
    
    return CorpusList(corpuses=corpus_list) 