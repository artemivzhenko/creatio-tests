import time
from typing import Callable, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By


def wait_for_js_ready(driver: WebDriver, timeout: int):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if (driver.execute_script("return document.readyState") or "") == "complete":
                return True
        except Exception:
            pass
        time.sleep(0.05)
    return False


def wait_for_css(driver: WebDriver, selector: str, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        except Exception:
            pass
        time.sleep(0.05)
    return False


def poll_until(fn: Callable[[], bool], timeout: int, interval: float = 0.1) -> bool:
    deadline = time.time() + timeout
    last = False
    while time.time() < deadline:
        try:
            last = bool(fn())
            if last:
                return True
        except Exception:
            last = False
        time.sleep(interval)
    return False
