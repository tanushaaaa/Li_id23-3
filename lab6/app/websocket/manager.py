from typing import Dict, List
from fastapi import WebSocket
import json
import asyncio


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_message_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            disconnected_websockets = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception:
                    disconnected_websockets.append(websocket)
            
            # Удаляем отключенные соединения
            for websocket in disconnected_websockets:
                self.disconnect(websocket, user_id)

    async def send_message_to_all(self, message: dict):
        for user_id in list(self.active_connections.keys()):
            await self.send_message_to_user(user_id, message)


websocket_manager = WebSocketManager() 