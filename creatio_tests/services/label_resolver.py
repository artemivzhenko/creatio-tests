from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from .dom_queries import find_labels


def safe_text(el: WebElement) -> str:
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


def resolve_label(container: WebElement, driver: WebDriver) -> str:
    try:
        input_el = container.find_element(By.CSS_SELECTOR, "input, textarea, [role='combobox']")
    except Exception:
        input_el = None
    if input_el:
        a = (input_el.get_attribute("aria-label") or "").strip()
        if a:
            return a
        labelledby = (input_el.get_attribute("aria-labelledby") or "").strip()
        if labelledby:
            parts = []
            for rid in labelledby.split():
                try:
                    ref = driver.find_element(By.ID, rid)
                    txt = safe_text(ref)
                    if txt:
                        parts.append(txt)
                except Exception:
                    pass
            t = " ".join(parts).strip()
            if t:
                return t
    for le in find_labels(container):
        t = safe_text(le)
        if t:
            return t
    return ""
