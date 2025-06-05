from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from app.websocket.manager import websocket_manager
from app.core.security import verify_token
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.cruds.user import get_user_by_id

router = APIRouter()


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """WebSocket эндпоинт для получения уведомлений"""
    try:
        # Проверяем токен
        user_id = verify_token(token)
        user = get_user_by_id(db, user_id)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Подключаем пользователя
        await websocket_manager.connect(websocket, user_id)
        
        try:
            while True:
                # Ожидаем сообщения от клиента (для поддержания соединения)
                data = await websocket.receive_text()
                # Можно обрабатывать входящие сообщения здесь
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, user_id)
            
    except Exception as e:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR) 