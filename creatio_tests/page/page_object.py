from typing import Dict, Tuple, Optional
from ..models.config import CheckContext
from ..models.result import ValidationResult
from ..field_types import FieldType
from ..fields.factory import FieldFactory
from .auth_page import CreatioAuthPage


class PageObject:
    def __init__(self, name: str, client: CreatioAuthPage, default_wait_timeout_sec: int = 30, debug: bool = False):
        self.name = name
        self.client = client
        self.default_wait_timeout_sec = default_wait_timeout_sec
        self.debug = debug
        self.fields: Dict[str, object] = {}

    def _log(self, field_code: str, msg: str):
        if self.debug:
            print(f"[{self.name}][{field_code}] {msg}", flush=True)

    def add_field(
        self,
        field_type: FieldType,
        code: str,
        title: Optional[str],
        readonly: Optional[bool],
        strict_title: bool,
        required: Optional[bool] = None,
        lookup_values: Optional[list] = None,
        wait_timeout_sec: Optional[int] = None,
    ):
        ctx = CheckContext(
            driver=self.client.driver,
            wait_timeout_sec=wait_timeout_sec or self.default_wait_timeout_sec,
            debug=self.debug,
            prefix=f"[{self.name}][{code}]"
        )
        f = FieldFactory.create(
            field_type=field_type,
            code=code,
            title=title,
            readonly=readonly,
            strict_title=strict_title,
            context=ctx,
            lookup_values=lookup_values,
            required=required,
        )
        self.fields[code] = f
        self._log(code, "field registered")

    def check_all(self) -> Tuple[bool, Dict[str, ValidationResult]]:
        results: Dict[str, ValidationResult] = {}
        all_ok = True
        for code, f in self.fields.items():
            el = self.client.get_field_fresh(code)
            if el is None:
                r = ValidationResult(False, "field not found", {"code": code})
            else:
                r = f.check(el)
            results[code] = r
            self._log(code, r.message)
            if not r.ok:
                all_ok = False
        return all_ok, results

    def await_check_all(self, timeout_per_field_sec: int = 30) -> Tuple[bool, Dict[str, ValidationResult]]:
        results: Dict[str, ValidationResult] = {}
        all_ok = True
        for code, f in self.fields.items():
            r = f.await_for_check(
                resolve_element=lambda c=code: self.client.get_field_fresh(c),
                timeout_sec=timeout_per_field_sec
            )
            results[code] = r
            self._log(code, r.message)
            if not r.ok:
                all_ok = False
        return all_ok, results
