from sqlalchemy.orm import Session
from app.models.corpus import Corpus
from app.schemas.corpus import CorpusCreate
from typing import List


def create_corpus(db: Session, corpus: CorpusCreate, user_id: int) -> Corpus:
    db_corpus = Corpus(
        name=corpus.corpus_name,
        text=corpus.text,
        user_id=user_id
    )
    db.add(db_corpus)
    db.commit()
    db.refresh(db_corpus)
    return db_corpus


def get_corpuses_by_user(db: Session, user_id: int) -> List[Corpus]:
    return db.query(Corpus).filter(Corpus.user_id == user_id).all()


def get_corpus_by_id(db: Session, corpus_id: int, user_id: int) -> Corpus:
    return db.query(Corpus).filter(
        Corpus.id == corpus_id, 
        Corpus.user_id == user_id
    ).first() 