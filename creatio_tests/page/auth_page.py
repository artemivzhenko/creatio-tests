import json
import sys
import time
from typing import Optional

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .field_index import FieldIndex

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException



class CreatioAuthPage:
    def __init__(self, base_url: str, username: str, password: str, test_url: str, headless: bool = True, wait_timeout_sec: int = 30, debug: bool = False):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.test_url = test_url
        self.wait_timeout_sec = wait_timeout_sec
        self.debug = debug
        self._http = requests.Session()
        chrome_opts = Options()
        if headless:
            chrome_opts.add_argument("--headless=new")
        chrome_opts.add_argument("--disable-gpu")
        chrome_opts.add_argument("--window-size=1920,1080")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_opts)
        self.page_html: Optional[str] = None
        self.fields = FieldIndex()

    def _log(self, msg: str):
        if self.debug:
            print(f"[creatio-auth-page] {msg}", file=sys.stderr, flush=True)

    def _login_and_get_cookies(self) -> requests.cookies.RequestsCookieJar:
        login_url = f"{self.base_url}/ServiceModel/AuthService.svc/Login"
        payload = {"UserName": self.username, "UserPassword": self.password}
        self._log(f"POST {login_url}")
        resp = self._http.post(login_url, json=payload, timeout=30)
        self._log(f"Login HTTP {resp.status_code}")
        if resp.status_code != 200:
            raise RuntimeError(f"Login failed: HTTP {resp.status_code}, body={resp.text[:2000]}")
        try:
            data = resp.json()
        except json.JSONDecodeError:
            data = {}
        self._log(f"Login JSON: {data}")
        if isinstance(data, dict) and data.get("Code") not in (None, 0):
            raise RuntimeError(f"Login returned error code: {data}")
        if not self._http.cookies:
            raise RuntimeError("No cookies returned after login.")
        self._log("Cookies: " + ", ".join([c.name for c in self._http.cookies]))
        return self._http.cookies

    def login(self):
        cookies = self._login_and_get_cookies()
        self.driver.get(self.base_url)
        time.sleep(0.5)
        for c in cookies:
            cookie_dict = {"name": c.name, "value": c.value, "path": c.path or "/"}
            if c.domain:
                cookie_dict["domain"] = c.domain.lstrip(".")
            if getattr(c, "secure", None) is not None:
                cookie_dict["secure"] = bool(c.secure)
            try:
                self.driver.add_cookie(cookie_dict)
                self._log(f"Cookie set: {c.name}")
            except Exception as e:
                self._log(f"Cookie add failed: {c.name}: {e}")

    def _resolve_test_url(self) -> str:
        if self.test_url.startswith("http://") or self.test_url.startswith("https://"):
            return self.test_url
        return f"{self.base_url}{self.test_url if self.test_url.startswith('/') else '/' + self.test_url}"

    def load_page(self):
        url = self._resolve_test_url()
        self._log(f"GET {url}")
        self.driver.get(url)
        deadline = time.time() + self.wait_timeout_sec
        while time.time() < deadline:
            try:
                state = self.driver.execute_script("return document.readyState") or ""
                if state == "complete":
                    break
            except Exception:
                pass
            time.sleep(0.05)
        self._log("document.readyState == complete")
        root_deadline = time.time() + self.wait_timeout_sec
        root_detected = False
        while time.time() < root_deadline:
            try:
                if self.driver.find_elements(By.CSS_SELECTOR, "[class*='crt-'], [data-component*='crt']"):
                    root_detected = True
                    break
            except Exception:
                pass
            time.sleep(0.05)
        if root_detected:
            self._log("CRT root detected")
        else:
            self._log("CRT root not detected")
        try:
            el_deadline = time.time() + self.wait_timeout_sec
            while time.time() < el_deadline:
                if self.driver.find_elements(By.CSS_SELECTOR, "[element-name]"):
                    self._log("at least one [element-name] detected")
                    break
                time.sleep(0.05)
        except Exception:
            self._log("no [element-name] detected within timeout")
        self.page_html = self.driver.page_source

    def build_fields_index(self):
        deadline = time.time() + self.wait_timeout_sec
        last_count = -1
        stable_ticks = 0
        poll_interval = 0.25
        selectors = [
            "crt-input[element-name]",
            "crt-checkbox[element-name]",
            "crt-combobox[element-name]",
            "crt-number-input[element-name]",
            "crt-date-input[element-name]",
            "crt-time-input[element-name]",
            "crt-date-time-input[element-name]",
            "crt-datetimepicker[element-name]",
        ]
        while time.time() < deadline:
            added_this_tick = 0
            all_candidates = []
            for sel in selectors:
                try:
                    all_candidates.extend(self.driver.find_elements(By.CSS_SELECTOR, sel))
                except Exception:
                    pass
            for el in all_candidates:
                try:
                    code = (el.get_attribute("element-name") or "").strip()
                except Exception:
                    code = ""
                if code:
                    if self.fields.get(code) is None:
                        self.fields.add(code, el)
                        added_this_tick += 1
            cur_count = len(self.fields)
            self._log(f"indexing: total={cur_count}, added={added_this_tick}")
            if cur_count == last_count:
                stable_ticks += 1
            else:
                stable_ticks = 0
            last_count = cur_count
            if cur_count > 0 and stable_ticks >= 4:
                break
            time.sleep(poll_interval)
        self._log(f"Indexed fields: {len(self.fields)}")

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass

    def get_field_fresh(self, code: str):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, f"[element-name='{code}']")
        except NoSuchElementException:
            return None

    def await_field_present(self, code: str, timeout_sec: int = 30, poll_interval_sec: float = 0.25):
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            el = self.get_field_fresh(code)
            if el is not None:
                return el
            time.sleep(poll_interval_sec)
        return None
