from typing import List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseField
from ..services.overlay_service import OverlayService


class LookupField(BaseField):
    def __init__(
        self,
        code: str,
        title: Optional[str],
        readonly: Optional[bool],
        strict_title: bool,
        context,
        expected_options: Optional[List[str]] = None,
    ):
        super().__init__(code, title, readonly, strict_title, context)
        self.expected_options = expected_options or []
        self.overlay = OverlayService(self.ctx.driver, self.ctx.wait_timeout_sec, logger=self.log)

    def _probe_control(self, container: WebElement):
        try:
            container.find_element(By.CSS_SELECTOR, ".crt-combobox-container, .crt-autocomplete-input-control, [role='combobox']")
            return True, "lookup control ok"
        except Exception as e:
            return False, f"lookup control not found: {e}"

    def _check_options(self, container: WebElement) -> Tuple[bool, str, List[str]]:
        if not self.expected_options:
            return True, "lookup dictionary check skipped", []
        ok, msg = self.overlay.open(container)
        if not ok:
            return False, msg, []
        ok2, options, msg2 = self.overlay.read_until_stable()
        if not ok2:
            return False, msg2, []
        missing = [v for v in self.expected_options if v not in options]
        if missing:
            return False, f"lookup dictionary missing values: {missing}; actual: {options}", options
        try:
            self.overlay.close()
        except Exception:
            pass
        return True, "lookup dictionary ok", options

    def set_value(self, container: WebElement, value: str) -> Tuple[bool, str]:
        if value is None or value == "":
            return False, "value is empty"
        ok, msg = self.overlay.open(container)
        if not ok:
            return False, msg
        try:
            option = self.ctx.driver.find_element(By.XPATH, f"//div[contains(@class,'mat-autocomplete-panel') and contains(@class,'mat-autocomplete-visible')]//mat-option[.//text()[normalize-space()='{value}'] or .//*[normalize-space(text())='{value}']]")
        except Exception:
            try:
                option = self.ctx.driver.find_element(By.XPATH, f"//div[contains(@class,'mat-autocomplete-panel') and contains(@class,'mat-autocomplete-visible')]//mat-option//*[contains(@class,'chip-text') or contains(@class,'mat-option-text')][normalize-space(text())='{value}']/ancestor::mat-option")
            except Exception as e:
                return False, f"option not found: {e}"
        try:
            option.click()
        except Exception:
            try:
                self.ctx.driver.execute_script("arguments[0].click();", option)
            except Exception as e:
                return False, f"cannot click option: {e}"
        try:
            self.overlay.close()
        except Exception:
            pass
        return True, "value set"

    def clear_value(self, container: WebElement) -> Tuple[bool, str]:
        try:
            clear_btn = container.find_element(By.CSS_SELECTOR, ".combobox-expander.clear, mat-icon[svgicon='small-close']")
        except Exception:
            clear_btn = None
        if clear_btn:
            try:
                clear_btn.click()
                return True, "value cleared via clear icon"
            except Exception:
                try:
                    self.ctx.driver.execute_script("arguments[0].click();", clear_btn)
                    return True, "value cleared via clear icon JS"
                except Exception:
                    pass
        try:
            host = container.find_element(By.CSS_SELECTOR, "[role='combobox']")
            host.clear()
            return True, "value cleared"
        except Exception:
            try:
                self.ctx.driver.execute_script("var e=arguments[0]; if(e){e.value=''; e.dispatchEvent(new Event('input',{bubbles:true}));}", host)
                return True, "value cleared via JS"
            except Exception as e:
                return False, f"cannot clear value: {e}"

    def check(self, container: WebElement):
        res = super().check(container)
        if not res.ok:
            return res
        ok, msg, options = self._check_options(container)
        if not ok:
            return type(res)(False, msg, {"code": self.code, "options": options})
        return type(res)(True, "field is valid", {"code": self.code, "options": options if options else None})
