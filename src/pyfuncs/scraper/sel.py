import os
from ..utils import chrome_main_version
from .sel_base import ChromeBase
import undetected_chromedriver.v2 as uc
from seleniumwire.webdriver import Chrome as SWW
from selenium.webdriver.chrome.webdriver import WebDriver as SW

_HOME = os.path.expanduser("~")


class ChromeUDSession(uc.Chrome, ChromeBase):
    def __init__(
            self,
            version_main=None,
            proxy=None,
            headless=False,
            disable_image=False,
            extensions=[],
            tz="America/Los_Angeles",  # set timezone to PST, earliest in US
            *args,
            **kwargs
    ):
        ChromeBase.__init__(
            self=self,
            proxy=proxy,
            headless=False,
            disable_image=False,
            extensions=extensions
        )

        if version_main is None:
            version_main = chrome_main_version()

        options = uc.ChromeOptions()
        old_options_dict = self.options.__dict__
        options.__dict__["_arguments"].extend(old_options_dict["_arguments"])

        if disable_image:
            options.add_argument('--blink-settings=imagesEnabled=false')

        # disable welcome message
        options.add_argument("--no-first-run")
        options.add_argument("--no-service-autorun")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--password-store=basic")

        super().__init__(
            version_main=version_main,
            options=options,
            headless=headless,
            desired_capabilities={'browserName': 'chrome', 'goog:loggingPrefs': {'performance': 'ALL'}},
            *args,
            **kwargs
        )
        self.execute_cdp_cmd(
            "Emulation.setTimezoneOverride",
            {"timezoneId": tz}
        )


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

