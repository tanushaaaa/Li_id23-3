from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, websocket, search_tasks, search
from fastapi.responses import FileResponse
import os

app = FastAPI()

app.include_router(search.router, tags=["fuzzy_search"])
app.include_router(search_tasks.router, prefix="/search", tags=["search"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(websocket.router)  # WebSocket не требует prefix

@app.get("/")
def read_root():
    return {"message": "Welcome to my API!"}
@app.get("/favicon.ico")
def favicon():
    return FileResponse(os.path.join("static", "favicon.ico"))

# CORS для клиентской части
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
