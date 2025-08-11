import time
from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .dom_queries import scroll_into_view, find_trigger


class OverlayService:
    def __init__(self, driver: WebDriver, timeout_sec: int = 20, logger=None):
        self.driver = driver
        self.timeout_sec = timeout_sec
        self.logger = logger

    def _log(self, msg: str):
        if self.logger:
            self.logger.info(msg)

    def open(self, container: WebElement) -> Tuple[bool, str]:
        scroll_into_view(self.driver, container)
        try:
            caret = container.find_element(By.CSS_SELECTOR, "mat-icon[svgicon='caret-arrow']")
            try:
                caret.click()
                self._log("caret clicked")
            except Exception:
                self.driver.execute_script("arguments[0].click();", caret)
                self._log("caret clicked via JS")
        except Exception:
            trg = find_trigger(container)
            try:
                trg.click()
                self._log("trigger clicked")
            except Exception:
                self.driver.execute_script("arguments[0].click();", trg)
                self._log("trigger clicked via JS")
        try:
            WebDriverWait(self.driver, self.timeout_sec).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cdk-overlay-pane .mat-autocomplete-panel.mat-autocomplete-visible .mat-option"))
            )
            self._log("overlay visible")
            return True, "overlay visible"
        except Exception as e:
            return False, f"overlay not visible: {e}"

    def _scroll_to_end(self):
        self.driver.execute_script(
            """
const panels = Array.from(document.querySelectorAll('.cdk-overlay-pane .mat-autocomplete-panel.mat-autocomplete-visible'));
for (const p of panels) { p.scrollTop = p.scrollHeight; }
"""
        )

    def collect_options(self) -> List[str]:
        items = self.driver.execute_script(
            """
const panels = Array.from(document.querySelectorAll('.cdk-overlay-pane .mat-autocomplete-panel.mat-autocomplete-visible'));
const set = new Set();
for (const p of panels) {
  const nodes = p.querySelectorAll('.mat-option .chip-text, .mat-option .mat-option-text, .mat-option [crttextoverflowtitle]');
  nodes.forEach(n => {
    const t = (n.innerText || n.textContent || '').trim();
    if (t) set.add(t);
  });
}
return Array.from(set);
"""
        ) or []
        return [str(x) for x in items]

    def read_until_stable(self) -> Tuple[bool, List[str], str]:
        deadline = time.time() + self.timeout_sec
        last_len = -1
        stable_ticks = 0
        texts: List[str] = []
        while time.time() < deadline:
            texts = self.collect_options()
            self._log(f"options: {texts}")
            if len(texts) == last_len and last_len >= 1:
                stable_ticks += 1
            else:
                stable_ticks = 0
            if stable_ticks >= 2:
                break
            last_len = len(texts)
            self._scroll_to_end()
            try:
                panel = self.driver.find_element(By.CSS_SELECTOR, ".cdk-overlay-pane .mat-autocomplete-panel.mat-autocomplete-visible")
                panel.send_keys(Keys.PAGE_DOWN)
            except Exception:
                pass
            time.sleep(0.15)
        if not texts:
            try:
                html = self.driver.execute_script(
                    "var p=document.querySelector('.cdk-overlay-pane .mat-autocomplete-panel.mat-autocomplete-visible');"
                    "return p? p.outerHTML : '';"
                ) or ""
            except Exception:
                html = ""
            return False, [], f"no options; overlay html: {html[:800]}"
        return True, texts, "options collected"

    def close(self):
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            self._log("overlay closed via ESC")
        except Exception:
            pass
