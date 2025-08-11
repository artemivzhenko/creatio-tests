from typing import Dict, Optional, Iterable
from selenium.webdriver.remote.webelement import WebElement


class FieldIndex:
    def __init__(self):
        self._items: Dict[str, WebElement] = {}

    def add(self, code: str, element: WebElement):
        if not code:
            return
        if code not in self._items:
            self._items[code] = element

    def get(self, code: str) -> Optional[WebElement]:
        return self._items.get(code)

    def keys(self) -> Iterable[str]:
        return self._items.keys()

    def values(self) -> Iterable[WebElement]:
        return self._items.values()

    def items(self) -> Iterable:
        return self._items.items()

    def __len__(self) -> int:
        return len(self._items)
