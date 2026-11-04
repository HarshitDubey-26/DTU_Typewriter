"""Debounce-based autosave that triggers after a configurable idle interval."""
import logging

logger = logging.getLogger("dtu_typewriter.autosave")


class AutosaveService:
    def __init__(self, root, controller, interval_ms: int = 3000):
        self.root = root
        self.controller = controller
        self.interval_ms = interval_ms
        self._timer_id = None
        self._dirty = False

    def mark_dirty(self):
        self._dirty = True
        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
        self._timer_id = self.root.after(
            self.interval_ms, self._do_save
        )

    def _do_save(self):
        self._timer_id = None
        if self._dirty:
            logger.debug("Autosave triggered")
            self.controller.autosave_now()
            self._dirty = False

    def stop(self):
        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
