from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base import BaseField


class TextField(BaseField):
    def _probe_control(self, container: WebElement):
        try:
            container.find_element(By.CSS_SELECTOR, "input.mat-input-element, input[type='text'], input[matinput]")
            return True, "text control ok"
        except Exception as e:
            return False, f"text control not found: {e}"
