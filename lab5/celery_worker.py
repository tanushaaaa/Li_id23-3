from app.services.tasks import celery

celery.autodiscover_tasks(["app.services"])
