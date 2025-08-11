from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ValidationResult:
    ok: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def with_detail(self, key: str, value: Any) -> "ValidationResult":
        self.details[key] = value
        return self
