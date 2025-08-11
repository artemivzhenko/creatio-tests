from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseField


class BooleanField(BaseField):
    def _probe_control(self, container: WebElement):
        try:
            container.find_element(By.CSS_SELECTOR, "mat-checkbox input[type='checkbox']")
            return True, "checkbox control ok"
        except Exception as e:
            return False, f"checkbox control not found: {e}"

    def set_value(self, container: WebElement, value) -> tuple[bool, str]:
        try:
            inp = container.find_element(By.CSS_SELECTOR, "mat-checkbox input[type='checkbox']")
        except Exception as e:
            return False, f"checkbox not found: {e}"
        target = bool(value)
        try:
            current = inp.is_selected()
        except Exception:
            current = False
        if current == target:
            return True, "value unchanged"
        try:
            inp.click()
            return True, "value toggled"
        except Exception:
            try:
                container.parent.execute_script("arguments[0].click();", inp)
                return True, "value toggled via JS"
            except Exception as e:
                return False, f"cannot toggle: {e}"

    def clear_value(self, container: WebElement) -> tuple[bool, str]:
        return self.set_value(container, False)
