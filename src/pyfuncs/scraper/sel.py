import os
import re
from selenium import webdriver as sw
from seleniumwire import webdriver as sww
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


HOME = os.path.expanduser("~")


def chrome_session(
        proxy=None,
        headless=False,
        wire=False,
        tz="America/Los_Angeles", # set timezone to PST, earliest in US
        exec_path=os.path.join(HOME, "gdrive/tools/chromedriver_92_linux")
):
    # options = {
    #     'proxy': {
    #         'http': 'http://username:password@host:port',
    #         'https': 'https://username:password@host:port',
    #         'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
    #     }
    # }
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # init options
    chrome_options = sw.ChromeOptions()

    # set regular settings
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--window-size=%s" % "1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")


    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # chromedriver 75+

    # headless mode
    if headless:
        chrome_options.add_argument("--headless")

    options=None
    # set proxy
    if proxy is not None:
        if isinstance(proxy, dict):
            proxy_http = proxy["http"]
            proxy = re.sub("http://", "", proxy["http"])
        elif isinstance(proxy, str):
            proxy_http = "http://" + proxy

        if wire:
            options = {
                "proxy": {
                    "http": proxy_http,
                    "https": proxy_http,
                    "no_proxy": "localhost,127.0.0.1"
                }
            }
        else:
            chrome_options.add_argument(f"--proxy-server={proxy}")

    if wire:
        w = sww.Chrome(
            os.path.join(dir_path, exec_path),
            options=chrome_options,
            desired_capabilities=capabilities,
            seleniumwire_options=options
        )
    else:
        w = sw.Chrome(
            os.path.join(dir_path, exec_path),
            options=chrome_options,
            desired_capabilities=capabilities
        )

    w.execute_cdp_cmd(
        "Emulation.setTimezoneOverride",
        {"timezoneId": tz}
    )

    return w
