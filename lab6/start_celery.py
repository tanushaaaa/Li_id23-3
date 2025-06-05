#!/usr/bin/env python3
"""
Скрипт для запуска Celery worker
"""

import os
import sys
from app.celery.celery_app import celery_app

if __name__ == "__main__":
    # Запускаем Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=1',
        '--pool=solo'  # Для Windows совместимости
    ]) 