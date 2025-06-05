from celery import Celery
import os

# Используем простой Redis URL для разработки
# В продакшене можно заменить на настоящий Redis
redis_url = "redis://localhost:6379/0"

celery_app = Celery(
    "fuzzy_search_app",
    broker=redis_url,
    backend=redis_url,
    include=["app.celery.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.celery.tasks.fuzzy_search_task": {"queue": "search_queue"},
    },
) 