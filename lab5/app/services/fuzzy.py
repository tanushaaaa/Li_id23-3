def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    previous_row = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        current_row = [i + 1]
        for j, cb in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (ca != cb)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def damerau_levenshtein(a: str, b: str) -> int:
    d = {}
    lenstr1 = len(a)
    lenstr2 = len(b)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            cost = 0 if a[i] == b[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,      # удаление
                d[(i, j - 1)] + 1,      # вставка
                d[(i - 1, j - 1)] + cost  # замена
            )
            if i > 0 and j > 0 and a[i] == b[j - 1] and a[i - 1] == b[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + cost)  # транспозиция
    return d[(lenstr1 - 1, lenstr2 - 1)]

def fuzzy_search(word: str, corpus: list[str], algorithm: str = "levenshtein") -> list[dict]:
    results = []

    func = levenshtein if algorithm == "levenshtein" else damerau_levenshtein

    for w in corpus:
        dist = func(word, w)
        results.append({"word": w, "distance": dist})

    return sorted(results, key=lambda x: x["distance"])
