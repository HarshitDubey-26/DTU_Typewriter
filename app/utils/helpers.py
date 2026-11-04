"""Small, reusable utility functions."""


def count_words(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def count_chars(text: str) -> int:
    return len(text)


def count_lines(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + 1


def calculate_wpm(typed_text: str, elapsed_seconds: int) -> float:
    if elapsed_seconds <= 0:
        return 0.0
    words = len(typed_text.split())
    return round((words / elapsed_seconds) * 60.0, 2)


def calculate_accuracy(original: str, typed: str) -> tuple:
    errors = 0
    total = max(len(original), 1)
    for i in range(max(len(original), len(typed))):
        oc = original[i] if i < len(original) else ""
        tc = typed[i] if i < len(typed) else ""
        if oc != tc:
            errors += 1
    accuracy = round(max(0.0, (1 - errors / total)) * 100.0, 2)
    return accuracy, errors
