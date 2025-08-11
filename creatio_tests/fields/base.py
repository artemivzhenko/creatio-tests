from typing import Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from ..models.result import ValidationResult
from ..models.config import CheckContext
from ..services.logger import Logger
from ..services.label_resolver import resolve_label
from ..services.readonly_detector import ReadonlyDetector


class BaseField:
    def __init__(
        self,
        code: str,
        title: Optional[str],
        readonly: Optional[bool],
        strict_title: bool,
        context: CheckContext,
    ):
        self.code = code
        self.title = title
        self.readonly = readonly
        self.strict_title = strict_title
        self.ctx = context
        self.log = Logger(enabled=self.ctx.debug, prefix=f"[field:{self.code}]")
        self._readonly = ReadonlyDetector()

    def _safe_text(self, el: WebElement) -> str:
        try:
            t = (el.text or "").strip()
            if t:
                return t
        except Exception:
            pass
        try:
            t = (el.get_attribute("textContent") or "").strip()
            if t:
                return t
        except Exception:
            pass
        return ""

    def _probe_control(self, container: WebElement) -> Tuple[bool, str]:
        return True, "control ok"

    def _check_title(self, container: WebElement) -> Tuple[bool, str, str]:
        if self.title is None:
            return True, "title check skipped", ""
        txt = resolve_label(container, self.ctx.driver)
        if not txt:
            return False, "label text is empty", ""
        if self.strict_title and txt != self.title:
            return False, f"label mismatch: expected '{self.title}', got '{txt}'", txt
        if not self.strict_title and self.title not in txt:
            return False, f"label does not contain expected substring: '{self.title}', got '{txt}'", txt
        return True, "title ok", txt

    def _check_readonly(self, container: WebElement) -> Tuple[bool, str, str]:
        if self.readonly is None:
            return True, "readonly check skipped", ""
        ro, reason = self._readonly.check(container)
        if self.readonly and not ro:
            return False, f"field is not readonly: {reason}", reason
        if not self.readonly and ro:
            return False, f"field is readonly: {reason}", reason
        return True, f"readonly ok: {reason}", reason

    def _find_editable(self, container: WebElement) -> Optional[WebElement]:
        try:
            return container.find_element(By.CSS_SELECTOR, "input, textarea")
        except Exception:
            return None

    def set_value(self, container: WebElement, value: str) -> Tuple[bool, str]:
        if value is None:
            return False, "value is None"
        inp = self._find_editable(container)
        if not inp:
            return False, "editable control not found"
        try:
            inp.click()
        except Exception:
            try:
                container.parent.execute_script("arguments[0].click();", inp)
            except Exception as e:
                return False, f"cannot focus control: {e}"
        try:
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(Keys.DELETE)
            inp.send_keys(str(value))
            return True, "value set"
        except Exception:
            try:
                container.parent.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", inp, str(value))
                return True, "value set via JS"
            except Exception as e:
                return False, f"cannot set value: {e}"

    def clear_value(self, container: WebElement) -> Tuple[bool, str]:
        inp = self._find_editable(container)
        if not inp:
            return False, "editable control not found"
        try:
            inp.click()
        except Exception:
            try:
                container.parent.execute_script("arguments[0].click();", inp)
            except Exception as e:
                return False, f"cannot focus control: {e}"
        try:
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(Keys.DELETE)
            return True, "value cleared"
        except Exception:
            try:
                container.parent.execute_script("arguments[0].value = ''; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", inp)
                return True, "value cleared via JS"
            except Exception as e:
                return False, f"cannot clear value: {e}"

    def check(self, container: WebElement) -> ValidationResult:
        ok, msg = self._probe_control(container)
        if not ok:
            return ValidationResult(False, msg, {"code": self.code})
        ok, tmsg, found = self._check_title(container)
        if not ok:
            return ValidationResult(False, tmsg, {"code": self.code, "label_found": found})
        ok, rmsg, reason = self._check_readonly(container)
        if not ok:
            return ValidationResult(False, rmsg, {"code": self.code, "readonly_reason": reason})
        return ValidationResult(True, "field is valid", {"code": self.code})
