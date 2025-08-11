from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def scroll_into_view(driver: WebDriver, el: WebElement):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center',inline:'center'});", el)
    except Exception:
        pass


def find_labels(container: WebElement) -> List[WebElement]:
    sels = [
        ".crt-input-label",
        "label",
        ".crt-checkbox-label",
        ".crt-base-input-width-holder-label",
        ".mat-form-field-label",
    ]
    out: List[WebElement] = []
    for s in sels:
        try:
            out.extend(container.find_elements(By.CSS_SELECTOR, s))
        except Exception:
            pass
    return out


def outer_html(driver: WebDriver, el: WebElement, max_len: int = 1200) -> str:
    try:
        html = driver.execute_script("return arguments[0].outerHTML;", el) or ""
    except Exception:
        html = ""
    html = html.strip().replace("\n", "")
    return html[:max_len] + ("..." if len(html) > max_len else "")


def find_trigger(container: WebElement) -> WebElement:
    try:
        return container.find_element(By.CSS_SELECTOR, "[role='combobox']")
    except Exception:
        pass
    try:
        return container.find_element(By.CSS_SELECTOR, ".crt-combobox-container, .crt-autocomplete-input-control, input")
    except Exception as e:
        raise e
