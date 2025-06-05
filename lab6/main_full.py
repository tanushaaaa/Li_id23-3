from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, corpus, search, websocket
from app.db.database import engine
from app.models import User, Corpus

# Создаем таблицы в базе данных
User.metadata.create_all(bind=engine)
Corpus.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fuzzy Search API",
    description="API для нечеткого поиска с WebSocket уведомлениями и Celery",
    version="2.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(corpus.router, prefix="/api", tags=["corpus"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])


@app.get("/")
def read_root():
    return {"message": "Fuzzy Search API (Full Version)", "version": "2.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 