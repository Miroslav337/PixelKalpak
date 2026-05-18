import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULTS = {
    "language": "ru",
    "theme": "light",
    "accent": "blue",
    "loan_days": 30,
}

ACCENT_PRESETS = {
    "blue":   {"BLUE": "#A1B5D8", "BLUE_ACTIVE": "#7291C7", "ACCENT": "#A7ED85"},
    "green":  {"BLUE": "#A8D5B5", "BLUE_ACTIVE": "#6BAF85", "ACCENT": "#D4F5A0"},
    "purple": {"BLUE": "#C3B1E1", "BLUE_ACTIVE": "#9B7FCC", "ACCENT": "#F0C8FF"},
    "orange": {"BLUE": "#F5C6A0", "BLUE_ACTIVE": "#E89A60", "ACCENT": "#FFF0A0"},
    "red":    {"BLUE": "#F5A0A0", "BLUE_ACTIVE": "#D96060", "ACCENT": "#A0F5C0"},
}


class AppSettings:
    PATH = os.path.join(_HERE, "settings.json")

    def __init__(self):
        self._data = {**DEFAULTS}
        self.load()

    def load(self):
        if os.path.exists(self.PATH):
            with open(self.PATH, "r", encoding="utf-8") as f:
                self._data.update(json.load(f))

    def save(self):
        with open(self.PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    @property
    def language(self): return self._data["language"]

    @property
    def theme(self): return self._data["theme"]

    @property
    def accent(self): return self._data["accent"]

    @property
    def loan_days(self): return int(self._data.get("loan_days", 30))

    def set(self, key, value):
        self._data[key] = value
        self.save()
