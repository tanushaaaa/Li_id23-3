from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.fuzzy import fuzzy_search

# Заглушка корпуса — в будущем заменим на БД
FAKE_CORPUSES = {
    1: ["example", "sample", "temple", "apple", "examine"]
}

router = APIRouter()

@router.websocket("/ws/search")
async def websocket_search(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            word = data.get("word")
            algorithm = data.get("algorithm", "levenshtein")
            corpus_id = data.get("corpus_id", 1)

            corpus = FAKE_CORPUSES.get(corpus_id, [])
            results = fuzzy_search(word, corpus, algorithm)

            await websocket.send_json({
                "word": word,
                "results": results
            })

    except WebSocketDisconnect:
        print("Client disconnected")
