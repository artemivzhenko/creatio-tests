from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseField


class DateTimeField(BaseField):
    def _probe_control(self, container: WebElement):
        try:
            container.find_element(By.CSS_SELECTOR, "input[aria-haspopup='dialog'], .crt-picker-input-control, .mat-datepicker-toggle, .mat-date-range-input")
            return True, "datetime control ok"
        except Exception as e:
            return False, f"datetime control not found: {e}"
