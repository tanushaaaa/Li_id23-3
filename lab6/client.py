#!/usr/bin/env python3
"""
Консольный клиент для API нечеткого поиска
"""

import asyncio
import json
import sys
import argparse
from typing import Optional, Dict, Any
import websockets
import requests
from urllib.parse import urljoin


class FuzzySearchClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = urljoin(base_url, "/api")
        self.ws_url = base_url.replace("http", "ws") + "/api"
        self.token: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, auth: bool = True) -> Dict:
        """Выполняет HTTP запрос к API"""
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        url = f"{self.api_url}/{endpoint}"
        
        headers = {"Content-Type": "application/json"}
        
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"Детали ошибки: {error_detail}")
                except:
                    print(f"Ответ сервера: {e.response.text}")
            return {}
    
    def register(self, email: str, password: str) -> bool:
        """Регистрация нового пользователя"""
        data = {"email": email, "password": password}
        result = self._make_request("POST", "sign-up/", data, auth=False)
        
        if result and "token" in result:
            self.token = result["token"]
            self.user_info = result
            print(f"Успешная регистрация! Пользователь ID: {result['id']}")
            return True
        else:
            print("Ошибка регистрации")
            return False
    
    def login(self, email: str, password: str) -> bool:
        """Вход в систему"""
        data = {"email": email, "password": password}
        result = self._make_request("POST", "login/", data, auth=False)
        
        if result and "token" in result:
            self.token = result["token"]
            self.user_info = result
            print(f"Успешный вход! Пользователь ID: {result['id']}")
            return True
        else:
            print("Ошибка входа")
            return False
    
    def get_user_info(self) -> Optional[Dict]:
        """Получение информации о текущем пользователе"""
        if not self.token:
            print("Необходимо войти в систему")
            return None
        
        result = self._make_request("GET", "users/me/")
        if result:
            print(f"Информация о пользователе: {result}")
            return result
        return None
    
    def upload_corpus(self, name: str, text: str) -> Optional[int]:
        """Загрузка корпуса текста"""
        if not self.token:
            print("Необходимо войти в систему")
            return None
        
        data = {"corpus_name": name, "text": text}
        result = self._make_request("POST", "upload_corpus", data)
        
        if result and "corpus_id" in result:
            corpus_id = result["corpus_id"]
            print(f"Корпус успешно загружен! ID: {corpus_id}")
            return corpus_id
        else:
            print("Ошибка загрузки корпуса")
            return None
    
    def get_corpuses(self) -> Optional[list]:
        """Получение списка корпусов"""
        if not self.token:
            print("Необходимо войти в систему")
            return None
        
        result = self._make_request("GET", "corpuses")
        if result and "corpuses" in result:
            corpuses = result["corpuses"]
            print("Доступные корпусы:")
            for corpus in corpuses:
                print(f"  ID: {corpus['id']}, Название: {corpus['name']}")
            return corpuses
        else:
            print("Ошибка получения списка корпусов")
            return None
    
    def search_sync(self, word: str, algorithm: str, corpus_id: int) -> Optional[Dict]:
        """Синхронный поиск"""
        if not self.token:
            print("Необходимо войти в систему")
            return None
        
        data = {"word": word, "algorithm": algorithm, "corpus_id": corpus_id}
        result = self._make_request("POST", "search_algorithm", data)
        
        if result:
            print(f"Результаты поиска (время выполнения: {result.get('execution_time', 0):.4f}с):")
            for res in result.get("results", []):
                print(f"  Слово: {res['word']}, Расстояние: {res['distance']}")
            return result
        else:
            print("Ошибка поиска")
            return None
    
    def search_async(self, word: str, algorithm: str, corpus_id: int) -> Optional[str]:
        """Асинхронный поиск"""
        if not self.token:
            print("Необходимо войти в систему")
            return None
        
        data = {"word": word, "algorithm": algorithm, "corpus_id": corpus_id}
        result = self._make_request("POST", "search_algorithm_async", data)
        
        if result and "task_id" in result:
            task_id = result["task_id"]
            print(f"Асинхронный поиск запущен! Task ID: {task_id}")
            return task_id
        else:
            print("Ошибка запуска асинхронного поиска")
            return None
    
    async def listen_websocket(self):
        """Прослушивание WebSocket уведомлений"""
        if not self.token:
            print("Необходимо войти в систему")
            return
        
        ws_url = f"{self.ws_url}/ws/{self.token}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print("WebSocket соединение установлено. Ожидание уведомлений...")
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._handle_websocket_message(data)
                    except json.JSONDecodeError:
                        print(f"Получено некорректное сообщение: {message}")
                        
        except Exception as e:
            print(f"Ошибка WebSocket соединения: {e}")
    
    async def _handle_websocket_message(self, data: Dict):
        """Обработка WebSocket сообщений"""
        status = data.get("status")
        task_id = data.get("task_id")
        
        if status == "STARTED":
            print(f"\n[{task_id}] Поиск начат: '{data.get('word')}' алгоритмом '{data.get('algorithm')}'")
        
        elif status == "PROGRESS":
            progress = data.get("progress", 0)
            current_word = data.get("current_word", "")
            print(f"[{task_id}] Прогресс: {progress}% ({current_word})")
        
        elif status == "COMPLETED":
            execution_time = data.get("execution_time", 0)
            results = data.get("results", [])
            print(f"\n[{task_id}] Поиск завершен! Время выполнения: {execution_time:.4f}с")
            print("Результаты:")
            for res in results:
                print(f"  Слово: {res['word']}, Расстояние: {res['distance']}")
        
        elif status == "ERROR":
            print(f"\n[{task_id}] Ошибка при выполнении поиска")
    
    def interactive_mode(self):
        """Интерактивный режим"""
        print("=== Клиент API нечеткого поиска ===")
        print("Доступные команды:")
        print("  register <email> <password> - Регистрация")
        print("  login <email> <password> - Вход")
        print("  me - Информация о пользователе")
        print("  upload <name> <text> - Загрузка корпуса")
        print("  corpuses - Список корпусов")
        print("  search <word> <algorithm> <corpus_id> - Синхронный поиск")
        print("  search_async <word> <algorithm> <corpus_id> - Асинхронный поиск")
        print("  listen - Прослушивание WebSocket уведомлений")
        print("  quit - Выход")
        print()
        
        while True:
            try:
                command = input(">>> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "quit":
                    break
                elif cmd == "register" and len(command) == 3:
                    self.register(command[1], command[2])
                elif cmd == "login" and len(command) == 3:
                    self.login(command[1], command[2])
                elif cmd == "me":
                    self.get_user_info()
                elif cmd == "upload" and len(command) >= 3:
                    name = command[1]
                    text = " ".join(command[2:])
                    self.upload_corpus(name, text)
                elif cmd == "corpuses":
                    self.get_corpuses()
                elif cmd == "search" and len(command) == 4:
                    word, algorithm, corpus_id = command[1], command[2], int(command[3])
                    self.search_sync(word, algorithm, corpus_id)
                elif cmd == "search_async" and len(command) == 4:
                    word, algorithm, corpus_id = command[1], command[2], int(command[3])
                    self.search_async(word, algorithm, corpus_id)
                elif cmd == "listen":
                    asyncio.run(self.listen_websocket())
                else:
                    print("Неизвестная команда или неверные параметры")
                    
            except KeyboardInterrupt:
                print("\nВыход...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")


def main():
    parser = argparse.ArgumentParser(description="Клиент API нечеткого поиска")
    parser.add_argument("--url", default="http://localhost:8000", help="URL сервера")
    parser.add_argument("--script", help="Файл со скриптом команд")
    
    args = parser.parse_args()
    
    client = FuzzySearchClient(args.url)
    
    if args.script:
        # Выполнение скрипта из файла
        try:
            with open(args.script, 'r', encoding='utf-8') as f:
                commands = f.readlines()
            
            for line in commands:
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"Выполняется: {line}")
                    # Здесь можно добавить логику выполнения команд из файла
                    
        except FileNotFoundError:
            print(f"Файл скрипта не найден: {args.script}")
            sys.exit(1)
    else:
        # Интерактивный режим
        client.interactive_mode()


if __name__ == "__main__":
    main() 