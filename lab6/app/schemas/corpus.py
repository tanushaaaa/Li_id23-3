from pydantic import BaseModel
from typing import List
from datetime import datetime


class CorpusBase(BaseModel):
    corpus_name: str
    text: str


class CorpusCreate(CorpusBase):
    pass


class CorpusResponse(BaseModel):
    corpus_id: int
    message: str


class CorpusInfo(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True


class CorpusList(BaseModel):
    corpuses: List[CorpusInfo] 