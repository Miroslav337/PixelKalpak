import json
import os


class I18n:
    def __init__(self, lang: str = "ru"):
        self._cache = {}
        self.lang = lang
        self._load(lang)

    def _load(self, lang: str):
        if lang not in self._cache:
            path = os.path.join(os.path.dirname(__file__), "locales", f"{lang}.json")
            with open(path, encoding="utf-8") as f:
                self._cache[lang] = json.load(f)

    def set_lang(self, lang: str):
        self._load(lang)
        self.lang = lang

    def t(self, key: str) -> str:
        return self._cache.get(self.lang, {}).get(key, key)
