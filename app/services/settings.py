"""Persist user-interface preferences (theme, font) as a small JSON file."""
import json
from app.utils.paths import get_local_appdata_dir

_DEFAULTS = {
    "theme": "dark",
    "font_family": "Consolas",
    "font_size": 14,
    "show_toolbar": True,
}


class UISettings:
    def __init__(self):
        self._path = get_local_appdata_dir() / "ui_settings.json"
        self.data = dict(_DEFAULTS)
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                self.data.update(
                    json.loads(self._path.read_text("utf-8"))
                )
            except Exception:
                pass

    def save(self):
        self._path.write_text(
            json.dumps(self.data, indent=2), encoding="utf-8"
        )

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()
