from typing import Optional, Tuple, Callable
import time
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
        required: Optional[bool] = None,
    ):
        self.code = code
        self.title = title
        self.readonly = readonly
        self.strict_title = strict_title
        self.required = required
        self.ctx = context
        self.log = Logger(enabled=self.ctx.debug, prefix=(self.ctx.prefix if getattr(self.ctx, "prefix", "") else f"[field:{self.code}]"))
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
        for sel in ["input, textarea", "[role='combobox']"]:
            try:
                return container.find_element(By.CSS_SELECTOR, sel)
            except Exception:
                pass
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
                self.ctx.driver.execute_script("arguments[0].click();", inp)
            except Exception as e:
                return False, f"cannot focus control: {e}"
        try:
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(Keys.DELETE)
            inp.send_keys(str(value))
        except Exception:
            try:
                self.ctx.driver.execute_script(
                    "arguments[0].value = arguments[1];"
                    "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                    inp, str(value)
                )
            except Exception as e:
                return False, f"cannot set value: {e}"
        try:
            self.ctx.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true})); arguments[0].blur();",
                inp
            )
        except Exception:
            pass
        return True, "value set"

    def clear_value(self, container: WebElement) -> Tuple[bool, str]:
        inp = self._find_editable(container)
        if not inp:
            return False, "editable control not found"
        try:
            inp.click()
        except Exception:
            try:
                self.ctx.driver.execute_script("arguments[0].click();", inp)
            except Exception as e:
                return False, f"cannot focus control: {e}"
        try:
            inp.send_keys(Keys.CONTROL, "a")
            inp.send_keys(Keys.DELETE)
        except Exception:
            try:
                self.ctx.driver.execute_script(
                    "arguments[0].value=''; arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                    inp
                )
            except Exception as e:
                return False, f"cannot clear value: {e}"
        try:
            self.ctx.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true})); arguments[0].blur();",
                inp
            )
        except Exception:
            pass
        return True, "value cleared"

    def get_value(self, container: WebElement) -> Tuple[bool, str, str]:
        inp = self._find_editable(container)
        if not inp:
            return False, "editable control not found", ""
        try:
            v = inp.get_attribute("value")
            if v is not None:
                return True, "value read", str(v)
        except Exception:
            pass
        try:
            v = self.ctx.driver.execute_script("return arguments[0].value;", inp)
            if v is not None:
                return True, "value read via JS", str(v)
        except Exception:
            pass
        return False, "cannot read value", ""

    def check_required_state(self, container: WebElement) -> Tuple[bool, str, bool]:
        inp = self._find_editable(container)
        is_req = False
        if inp:
            try:
                a = (inp.get_attribute("aria-required") or "").strip().lower()
                if a == "true":
                    is_req = True
            except Exception:
                pass
            try:
                if inp.get_attribute("required") is not None:
                    is_req = True
            except Exception:
                pass
        try:
            labels = container.find_elements(By.CSS_SELECTOR, ".crt-input-label, label, .crt-base-input-width-holder-label")
            for le in labels:
                cls = (le.get_attribute("class") or "")
                if "crt-input-required" in cls:
                    is_req = True
                    break
        except Exception:
            pass
        return True, "required state read", is_req

    def trigger_required_validation(self, container: WebElement, timeout_sec: int = 10) -> Tuple[bool, str]:
        ok, msg = self.clear_value(container)
        if not ok:
            return False, msg
        inp = self._find_editable(container)
        if inp:
            try:
                self.ctx.driver.execute_script("arguments[0].dispatchEvent(new Event('blur',{bubbles:true}));", inp)
            except Exception:
                pass
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            aria_invalid = ""
            try:
                aria_invalid = (inp.get_attribute("aria-invalid") or "").strip().lower() if inp else ""
            except Exception:
                aria_invalid = ""
            if aria_invalid == "true":
                return True, "invalid state detected"
            try:
                err = container.find_elements(By.CSS_SELECTOR, ".mat-form-field-subscript-wrapper .mat-error, .mat-form-field-subscript-wrapper [role='alert']")
                if any((e.text or e.get_attribute("textContent") or "").strip() for e in err):
                    return True, "error message detected"
            except Exception:
                pass
            time.sleep(0.15)
        return False, "no required validation detected"

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
        if self.required is not None:
            ok, _, is_req = self.check_required_state(container)
            if self.required and not is_req:
                return ValidationResult(False, "field is not marked as required", {"code": self.code})
            if not self.required and is_req:
                return ValidationResult(False, "field is marked as required", {"code": self.code})
        return ValidationResult(True, "field is valid", {"code": self.code})

    def await_for_check(
        self,
        resolve_element: Callable[[], Optional[WebElement]],
        timeout_sec: int = 30,
        poll_interval_sec: float = 0.25,
    ) -> ValidationResult:
        deadline = time.time() + timeout_sec
        last_fail: Optional[ValidationResult] = None
        while time.time() < deadline:
            el = None
            try:
                el = resolve_element()
            except Exception:
                el = None
            if el is not None:
                res = self.check(el)
                if res.ok:
                    return res
                last_fail = res
            time.sleep(poll_interval_sec)
        if last_fail is not None:
            return last_fail
        return ValidationResult(False, "field not found for check", {"code": self.code})
