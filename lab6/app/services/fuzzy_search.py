import re
import time
from typing import List, Tuple, Dict
from app.schemas.search import SearchResult


class FuzzySearchService:
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Вычисляет расстояние Левенштейна между двумя строками"""
        if len(s1) < len(s2):
            return FuzzySearchService.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    @staticmethod
    def damerau_levenshtein_distance(s1: str, s2: str) -> int:
        """Вычисляет расстояние Дамерау-Левенштейна между двумя строками"""
        len1, len2 = len(s1), len(s2)
        
        # Создаем матрицу
        H = {}
        maxdist = len1 + len2
        H[-1, -1] = maxdist
        
        # Инициализация первой строки и столбца
        for i in range(0, len1 + 1):
            H[i, -1] = maxdist
            H[i, 0] = i
        for j in range(0, len2 + 1):
            H[-1, j] = maxdist
            H[0, j] = j
            
        # Словарь для отслеживания последнего вхождения символов
        last_row = {}
        for c in s1 + s2:
            last_row[c] = 0
            
        for i in range(1, len1 + 1):
            last_match_col = 0
            for j in range(1, len2 + 1):
                i1 = last_row[s2[j-1]]
                j1 = last_match_col
                cost = 1
                if s1[i-1] == s2[j-1]:
                    cost = 0
                    last_match_col = j
                    
                H[i, j] = min(
                    H[i-1, j] + 1,     # insertion
                    H[i, j-1] + 1,     # deletion
                    H[i-1, j-1] + cost, # substitution
                    H[i1-1, j1-1] + (i-i1-1) + 1 + (j-j1-1) # transposition
                )
                
            last_row[s1[i-1]] = i
            
        return H[len1, len2]

    @staticmethod
    def extract_words(text: str) -> List[str]:
        """Извлекает слова из текста"""
        words = re.findall(r'\b\w+\b', text.lower())
        return list(set(words))  # Убираем дубликаты

    @staticmethod
    def search_with_algorithm(
        query_word: str, 
        corpus_text: str, 
        algorithm: str,
        max_distance: int = 3
    ) -> Tuple[List[SearchResult], float]:
        """Выполняет поиск с указанным алгоритмом"""
        start_time = time.time()
        
        words = FuzzySearchService.extract_words(corpus_text)
        results = []
        
        query_word = query_word.lower()
        
        for word in words:
            if algorithm == "levenshtein":
                distance = FuzzySearchService.levenshtein_distance(query_word, word)
            elif algorithm == "damerau_levenshtein":
                distance = FuzzySearchService.damerau_levenshtein_distance(query_word, word)
            else:
                raise ValueError(f"Неподдерживаемый алгоритм: {algorithm}")
            
            if distance <= max_distance:
                results.append(SearchResult(word=word, distance=distance))
        
        # Сортируем по расстоянию
        results.sort(key=lambda x: x.distance)
        
        execution_time = time.time() - start_time
        return results, execution_time

    @staticmethod
    def get_available_algorithms() -> List[str]:
        """Возвращает список доступных алгоритмов"""
        return ["levenshtein", "damerau_levenshtein"] 