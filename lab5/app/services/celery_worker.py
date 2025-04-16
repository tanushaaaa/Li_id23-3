from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0')
@app.task
def async_search_task(word, corpus_id):
    # Асинхронный поиск
    pass