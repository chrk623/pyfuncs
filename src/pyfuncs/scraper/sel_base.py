import re
import time
import json
from selenium import webdriver as sw


class ChromeBase:
    def __init__(self, proxy=None, headless=False, disable_image=False):
        self.proxy = proxy
        self.headless = headless
        self.disable_image = disable_image
        self.options = sw.ChromeOptions()
        self._prepare_driver()
        self._set_headless()
        self._set_proxy()

    def prepare_driver(self):
        # custom options to add
        pass

    def _prepare_driver(self):
        # options
        if self.disable_image:
            prefs = {"profile.managed_default_content_settings.images": 2}
            self.options.add_experimental_option("prefs", prefs)

        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--window-size=%s" % "1920,1080")
        self.options.add_argument("--disable-dev-shm-usage")

    def _set_headless(self):
        if self.headless:
            self.options.add_argument("--headless")

    def _set_proxy(self):
        if self.proxy:
            proxy = self.proxy
            if isinstance(proxy, dict):
                proxy = re.sub("http://", "", proxy["http"])

            self.options.add_argument(f"--proxy-server={proxy}")

    def scroll_to_bottom(self, by_height=300, delay_between_scroll=1, actions_between_scroll=[]):
        h = 0
        H = self.execute_script('return document.body.scrollHeight;')

        while True:
            h += by_height
            if h >= H:
                break

            self.execute_script("window.scrollTo({}, {});".format(0, h))
            time.sleep(delay_between_scroll)

            out = []
            for action in actions_between_scroll:
                out.append(action())

        return out

    def fetch_network_log(self):
        out = []
        logs = self.get_log("performance")
        for entry in logs:
            log = json.loads(entry["message"])["message"]
            if (
                    "Network.response" in log["method"]
                    or "Network.request" in log["method"]
                    or "Network.webSocket" in log["method"]
            ):
                out.append(log)

        return out

    @staticmethod
    def filter_log_by_x(logs, expr):
        # TODO: can change to lambda expression here..
        """
            logs (list/dict): log
            expr (str): try anything in terms of x
                e.g., to find if log[0]["request"]["url"] exists
                then expr = "x["request"]["url"]"
                i.e, `filter_log_by_x(logs, "x["request"]["url"]")`

                Boolean expressions can also be use:
        """
        if isinstance(logs, dict):
            logs = [logs]

        out = []
        for x in logs:
            try:
                o = eval(expr)
                if isinstance(o, bool) and o:
                    out.append(x)
                else:
                    out.append(x)
            except:
                pass

        return out

    @staticmethod
    def filter_log_by_keys(logs, filters):
        # depreciated
        if isinstance(filters, str):
            filters = [filters]
        if isinstance(filters[0], str):
            filters = [filters]

        out = []
        used_log = []
        for log_i, log in enumerate(logs):
            for filter_i, filter in enumerate(filters):
                if log_i not in used_log:
                    key = re.sub(",[ ]", "][", json.dumps(filter))
                    try:
                        _ = eval("log" + key)
                        out.append(log)
                        used_log.append(log_i)
                    except KeyError:
                        pass

        return out
