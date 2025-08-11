from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseField


class NumberField(BaseField):
    def _probe_control(self, container: WebElement):
        try:
            container.find_element(By.CSS_SELECTOR, "input[crtnumbercontrol], input[type='number'], input.mat-input-element")
            return True, "number control ok"
        except Exception as e:
            return False, f"number control not found: {e}"
