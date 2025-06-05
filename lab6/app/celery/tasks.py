from celery import current_task
from app.celery.celery_app import celery_app
from app.services.fuzzy_search import FuzzySearchService
from app.websocket.manager import websocket_manager
from app.schemas.search import WebSocketMessage, SearchResult
import asyncio
import json


@celery_app.task(bind=True)
def fuzzy_search_task(self, word: str, algorithm: str, corpus_text: str, user_id: int):
    """Задача для выполнения нечеткого поиска с отправкой уведомлений через WebSocket"""
    task_id = self.request.id
    
    # Отправляем уведомление о начале
    start_message = WebSocketMessage(
        status="STARTED",
        task_id=task_id,
        word=word,
        algorithm=algorithm
    )
    
    # Отправляем через WebSocket
    asyncio.run(websocket_manager.send_message_to_user(user_id, start_message.dict()))
    
    try:
        # Извлекаем слова для подсчета прогресса
        words = FuzzySearchService.extract_words(corpus_text)
        total_words = len(words)
        
        # Выполняем поиск с отправкой прогресса
        results = []
        query_word = word.lower()
        
        for i, corpus_word in enumerate(words):
            # Вычисляем расстояние
            if algorithm == "levenshtein":
                distance = FuzzySearchService.levenshtein_distance(query_word, corpus_word)
            elif algorithm == "damerau_levenshtein":
                distance = FuzzySearchService.damerau_levenshtein_distance(query_word, corpus_word)
            else:
                raise ValueError(f"Неподдерживаемый алгоритм: {algorithm}")
            
            if distance <= 3:  # Максимальное расстояние
                results.append(SearchResult(word=corpus_word, distance=distance))
            
            # Отправляем прогресс каждые 10% или каждые 100 слов
            if i % max(1, total_words // 10) == 0 or i % 100 == 0:
                progress = int((i + 1) / total_words * 100)
                progress_message = WebSocketMessage(
                    status="PROGRESS",
                    task_id=task_id,
                    progress=progress,
                    current_word=f"processing word {i + 1}/{total_words}"
                )
                asyncio.run(websocket_manager.send_message_to_user(user_id, progress_message.dict()))
        
        # Сортируем результаты
        results.sort(key=lambda x: x.distance)
        
        # Отправляем результат
        completion_message = WebSocketMessage(
            status="COMPLETED",
            task_id=task_id,
            execution_time=0.0,  # Будет вычислено на клиенте
            results=results
        )
        
        asyncio.run(websocket_manager.send_message_to_user(user_id, completion_message.dict()))
        
        return {
            "results": [result.dict() for result in results],
            "total_processed": total_words
        }
        
    except Exception as e:
        # Отправляем сообщение об ошибке
        error_message = WebSocketMessage(
            status="ERROR",
            task_id=task_id,
            word=word,
            algorithm=algorithm
        )
        asyncio.run(websocket_manager.send_message_to_user(user_id, error_message.dict()))
        raise e 