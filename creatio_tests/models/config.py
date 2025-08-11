from dataclasses import dataclass
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class CheckContext:
    driver: WebDriver
    wait_timeout_sec: int = 20
    debug: bool = False
    prefix: str = ""
