import os
from .sel_base import ChromeBase
from seleniumwire.webdriver import Chrome as SWW
from selenium.webdriver.chrome.webdriver import WebDriver as SW

_HOME = os.path.expanduser("~")


class ChromeSession(SW, ChromeBase):
    def __init__(
            self,
            executable_path=os.path.join(_HOME, "gdrive/tools/chromedriver_92_linux"),
            proxy=None,
            headless=False,
            disable_image=False,
            tz="America/Los_Angeles",  # set timezone to PST, earliest in US
            *args,
            **kwargs
    ):
        ChromeBase.__init__(
            self=self,
            proxy=proxy,
            headless=headless,
            disable_image=disable_image,
        )
        super().__init__(
            executable_path=executable_path,
            options=self.options,
            desired_capabilities={'browserName': 'chrome', 'goog:loggingPrefs': {'performance': 'ALL'}},
            *args,
            **kwargs
        )
        self.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": tz}
        )


class ChromeWireSession(SWW, ChromeBase):
    proxy = None
    wire_options = {}

    def __init__(
            self,
            executable_path=os.path.join(_HOME, "gdrive/tools/chromedriver_92_linux"),
            proxy=None,
            headless=False,
            disable_image=False,
            tz="America/Los_Angeles",  # set timezone to PST, earliest in US
            *args,
            **kwargs
    ):
        ChromeBase.__init__(
            self=self,
            proxy=proxy,
            headless=headless,
            disable_image=disable_image,
        )
        super().__init__(
            executable_path=executable_path,
            options=self.options,
            desired_capabilities={'browserName': 'chrome', 'goog:loggingPrefs': {'performance': 'ALL'}},
            *args,
            **kwargs
        )
        self.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": tz}
        )

    def _set_proxy(self):
        if self.proxy:
            proxy = self.proxy
            if isinstance(proxy, dict):
                proxy = proxy["http"]

            self.wire_options = {
                "proxy": {
                    "http": proxy,
                    "https": proxy,
                    "no_proxy": "localhost,127.0.0.1"
                }
            }
