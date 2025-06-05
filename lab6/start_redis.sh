#!/bin/bash

# Проверяем, установлен ли Docker
if ! command -v docker &> /dev/null; then
    echo "Docker не установлен. Устанавливаем Redis локально..."
    
    # Для macOS с Homebrew
    if command -v brew &> /dev/null; then
        echo "Устанавливаем Redis через Homebrew..."
        brew install redis
        echo "Запускаем Redis..."
        brew services start redis
    else
        echo "Пожалуйста, установите Redis вручную или Docker"
        exit 1
    fi
else
    echo "Запускаем Redis в Docker..."
    docker run -d --name redis-fuzzy-search -p 6379:6379 redis:7-alpine
    echo "Redis запущен в контейнере redis-fuzzy-search"
fi

echo "Redis доступен на localhost:6379" 