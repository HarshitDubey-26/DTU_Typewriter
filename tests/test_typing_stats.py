"""Tests for the TypingStatsService and the new application workflow.

Uses a separate temporary database — never touches the real user database.
"""
import pytest
from app.services.typing_stats import TypingStatsService


# ── TypingStatsService ──────────────────────────────────────────

class TestTypingStatsService:
    def setup_method(self):
        self.svc = TypingStatsService()

    # Net WPM
    def test_net_wpm_basic(self):
        # 50 correct chars in 60 seconds  →  (50/5)/1 = 10 WPM
        assert self.svc.calculate_net_wpm(50, 60) == 10.0

    def test_net_wpm_zero_elapsed(self):
        assert self.svc.calculate_net_wpm(100, 0) == 0.0

    def test_net_wpm_negative_elapsed(self):
        assert self.svc.calculate_net_wpm(100, -5) == 0.0

    def test_net_wpm_short_duration(self):
        # 25 correct chars in 10 seconds → (25/5)/(10/60) = 5/0.1667 ≈ 30
        wpm = self.svc.calculate_net_wpm(25, 10)
        assert wpm == 30.0

    # Accuracy
    def test_accuracy_perfect(self):
        assert self.svc.calculate_accuracy(100, 100) == 100.0

    def test_accuracy_half(self):
        assert self.svc.calculate_accuracy(50, 100) == 50.0

    def test_accuracy_no_keystrokes(self):
        assert self.svc.calculate_accuracy(0, 0) == 100.0

    def test_accuracy_with_errors(self):
        # 80 correct out of 100 total = 80%
        assert self.svc.calculate_accuracy(80, 100) == 80.0

    # KDPH (Key Depressions Per Hour)
    def test_kdph_basic(self):
        # 1500 keystrokes in 600 seconds (10 min) -> (1500 / 600) * 3600 = 9000 KDPH
        assert self.svc.calculate_kdph(1500, 600) == 9000.0

    def test_kdph_zero_elapsed(self):
        assert self.svc.calculate_kdph(100, 0) == 0.0

    def test_kdph_one_minute(self):
        # 300 keystrokes in 60 seconds -> (300 / 60) * 3600 = 18000 KDPH
        assert self.svc.calculate_kdph(300, 60) == 18000.0

    # compare_texts
    def test_compare_texts_perfect(self):
        correct, total, errors = self.svc.compare_texts("hello", "hello")
        assert correct == 5
        assert total == 5
        assert errors == 0

    def test_compare_texts_with_errors(self):
        correct, total, errors = self.svc.compare_texts("hello", "hxllo")
        assert correct == 4
        assert errors == 1

    def test_compare_texts_partial(self):
        correct, total, errors = self.svc.compare_texts("hello world", "hel")
        assert correct == 3
        assert total == 3
        assert errors == 0

    def test_compare_texts_empty_typed(self):
        correct, total, errors = self.svc.compare_texts("hello", "")
        assert correct == 0
        assert total == 0
        assert errors == 0
