"""Typing statistics calculation service.

Calculates Net WPM, accuracy percentage, and error count using
character-level analysis.  This module is intentionally kept free of any
UI / Tkinter dependencies so it can be unit-tested independently.
"""


class TypingStatsService:
    """Stateless helper that computes typing-test metrics."""

    @staticmethod
    def calculate_net_wpm(correct_chars: int, elapsed_seconds: float) -> float:
        """Net WPM = (correct_chars / 5) / elapsed_minutes.

        Handles division-by-zero and very short durations gracefully.
        """
        if elapsed_seconds <= 0:
            return 0.0
        elapsed_minutes = elapsed_seconds / 60.0
        if elapsed_minutes <= 0:
            return 0.0
        return round((correct_chars / 5.0) / elapsed_minutes, 2)

    @staticmethod
    def calculate_accuracy(correct_keystrokes: int, total_keystrokes: int) -> float:
        """Accuracy = (correct / total) * 100.

        Returns 100.0 when there are no keystrokes (edge-case guard).
        """
        if total_keystrokes <= 0:
            return 100.0
        return round((correct_keystrokes / total_keystrokes) * 100.0, 2)

    @staticmethod
    def compare_texts(reference: str, typed: str):
        """Character-level comparison of typed text against the reference.

        Returns
        -------
        correct_chars : int
            Number of characters that match the reference at the same
            position.
        total_compared : int
            ``min(len(reference), len(typed))`` — i.e. how far the student
            actually typed.
        errors : int
            Character-position mismatches (only up to the length of the
            shorter string).
        """
        length = min(len(reference), len(typed))
        correct = sum(1 for i in range(length) if reference[i] == typed[i])
        errors = length - correct
        return correct, length, errors
