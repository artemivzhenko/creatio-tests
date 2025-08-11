import sys
from typing import Optional


class Logger:
    def __init__(self, enabled: bool = False, prefix: str = ""):
        self.enabled = enabled
        self.prefix = prefix

    def _fmt(self, level: str, msg: str) -> str:
        p = f"{self.prefix} " if self.prefix else ""
        return f"{p}[{level}] {msg}"

    def log(self, msg: str):
        if self.enabled:
            print(self._fmt("log", msg), file=sys.stderr, flush=True)

    def info(self, msg: str):
        if self.enabled:
            print(self._fmt("info", msg), file=sys.stderr, flush=True)

    def warn(self, msg: str):
        if self.enabled:
            print(self._fmt("warn", msg), file=sys.stderr, flush=True)

    def error(self, msg: str):
        if self.enabled:
            print(self._fmt("error", msg), file=sys.stderr, flush=True)
