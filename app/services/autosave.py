"""Hybrid autosave service: periodic timer + keystroke threshold + debounce idle.

Ensures that even during continuous typing without pauses, or in case of a
sudden crash / power cut, progress is persisted to SQLite regularly.
"""
import logging

logger = logging.getLogger("dtu_typewriter.autosave")


class AutosaveService:
    def __init__(self, root, controller, interval_ms: int = 1500, periodic_ms: int = 2000):
        self.root = root
        self.controller = controller
        self.interval_ms = interval_ms
        self.periodic_ms = periodic_ms
        self._timer_id = None
        self._periodic_timer_id = None
        self._dirty = False
        self._keystroke_count = 0
        self._periodic_running = False

    def start_periodic(self):
        """Start a periodic ticker that saves dirty drafts every periodic_ms."""
        self.stop_periodic()
        self._periodic_running = True
        self._schedule_periodic()

    def _schedule_periodic(self):
        if not self._periodic_running:
            return
        self._periodic_timer_id = self.root.after(
            self.periodic_ms, self._periodic_tick
        )

    def _periodic_tick(self):
        self._periodic_timer_id = None
        if self._dirty:
            self._do_save()
        if self._periodic_running:
            self._schedule_periodic()

    def stop_periodic(self):
        self._periodic_running = False
        if self._periodic_timer_id is not None:
            try:
                self.root.after_cancel(self._periodic_timer_id)
            except Exception:
                pass
            self._periodic_timer_id = None

    def mark_dirty(self, keystroke: bool = True):
        """Mark typing state dirty.
        
        Triggers an immediate save every 10 keystrokes or schedules a debounced save.
        """
        self._dirty = True
        if keystroke:
            self._keystroke_count += 1
            if self._keystroke_count >= 10:
                self._keystroke_count = 0
                self._do_save()
                return

        # Debounced idle save
        if self._timer_id is not None:
            try:
                self.root.after_cancel(self._timer_id)
            except Exception:
                pass
        self._timer_id = self.root.after(
            self.interval_ms, self._do_save
        )

    def _do_save(self):
        if self._timer_id is not None:
            try:
                self.root.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        if self._dirty:
            logger.debug("Autosave triggered")
            try:
                self.controller.autosave_now()
            except Exception as exc:
                logger.error("Error in autosave_now: %s", exc)
            self._dirty = False

    def stop(self):
        """Stop all autosave timers and flush any pending dirty state."""
        self.stop_periodic()
        if self._timer_id is not None:
            try:
                self.root.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        if self._dirty:
            try:
                self.controller.autosave_now()
            except Exception:
                pass
            self._dirty = False
