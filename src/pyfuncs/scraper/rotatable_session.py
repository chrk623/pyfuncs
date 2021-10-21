import math
from time import sleep
from requests import Session
from ..utils import minimal_headers
from ..proxies.webshare import Webshare
from ..fua.fakeuseragent import FakeUserAgent


class RSession(Session):
    sleep_secs = 30
    last_error = None
    log_base_text = ""
    unaccepted_codes = []
    unaccepted_code_start = [4]
    webshare_options = {"userpass": False, "ensure_ip_authorized": False}

    def __init__(self, proxy_list=None, base_headers=None, patience=3, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patience = patience
        self.patience_wait_n = math.ceil(patience * 0.5)
        self.logger = logger
        self.fua = FakeUserAgent()
        self._init_headers(base_headers)
        self._init_proxies(proxy_list)

    def log_print(self, x):
        self.logger.info(x)

    def is_code_accepted(self, code):
        if code in self.unaccepted_codes:
            return False
        for s in self.unaccepted_code_start:
            if str(code)[0] == str(s):
                return False

        return True

    def _init_headers(self, headers):
        if headers is None:
            new_headers = minimal_headers
        else:
            new_headers = {}
            for k, v in headers.items():
                new_headers[k.lower()] = v
            new_headers["user-agent"] = self.fua.random

        self.headers = new_headers

    def _init_proxies(self, proxies):
        if type(proxies) not in [dict, list, str, type(None)]:
            raise Exception("check proxies input")

        self.proxy_cnt = 0
        if proxies is not None:
            if proxies == "webshare":
                ws = Webshare(**self.webshare_options)
                proxies = ws.fetch_proxies_dict()
            elif isinstance(proxies, dict):
                proxies = [proxies]
        else:
            proxies = [{}]

        self.proxy_list = proxies
        self.num_proxies = len(self.proxy_list)
        self.proxies = self.proxy_list[self.proxy_cnt]
        self.proxy_cnt += 1

    def _req(self, method, *args, **kwargs):
        for p in range(self.patience):
            try:
                r = self.request(method=method, *args, **kwargs)
                if not self.is_code_accepted(r.status_code):
                    self.rotate_ua_and_proxy()
                    self.logger.warning(f"status_code='{r.status_code}, rotating proxy'")
                    continue
                return r
            except Exception as e:
                if p == self.patience_wait_n:
                    self.logger.warning(f"request failed {self.patience_wait_n} times, sleeping for {self.sleep_secs} seconds")
                    sleep(self.sleep_secs)
                self.last_error = e
                self.rotate_ua_and_proxy()

        return None

    def get(self, *args, **kwargs):
        return self._req(method="GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._req(method="POST", *args, **kwargs)

    def rotate_ua(self):
        self.headers["user-agent"] = self.fua.random

    def rotate_proxy(self):
        old_count = self.proxy_cnt
        if self.proxy_cnt >= self.num_proxies:
            self.proxy_cnt = 0
        self.proxies = self.proxy_list[self.proxy_cnt]
        self.proxy_cnt += 1

        if self.logger is not None:
            self.logger.debug(self.log_base_text + f", switching proxy [{old_count}] -> [{self.proxy_cnt}]")

    def rotate_ua_and_proxy(self):
        self.rotate_ua()
        self.rotate_proxy()

    def get_loc(self):
        r = self.get(url="http://ip-api.com/json")
        r = r.json()

        if r["status"] == "success":
            return {
                "ip": r["query"],
                "country": r["country"],
                "region": r["regionName"],
                "city": r["city"],
            }

        return None
