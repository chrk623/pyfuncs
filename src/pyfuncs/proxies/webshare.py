import os
import random
import requests as rq
from retry import retry


class Webshare:
    def __init__(self, key=os.getenv("WEBSHARE_KEY"), userpass=False, ensure_ip_authorized=True):
        if key is None:
            raise Exception("No keys provided")
        self.userpass = userpass
        self.key = key
        self.headers = {"Authorization": key}
        self.public_ip = None

        if not userpass and ensure_ip_authorized:
            self._ensure_ip_authorized()

    def _ensure_ip_authorized(self):
        current_public_ip = self.fetch_public_ip()
        authorized_ips = self.fetch_authorized_ips()
        if current_public_ip not in authorized_ips:
            self.set_authorized_ips(current_public_ip)

    def fetch_authorized_ips(self):
        r = rq.get(
            "https://proxy.webshare.io/api/proxy/config/",
            headers=self.headers
        )
        p = r.json()["authorized_ips"]
        return p

    def set_authorized_ips(self, ips):
        auth_ips = self.fetch_authorized_ips()
        auth_ips.extend(ips)
        r = rq.post(
            "https://proxy.webshare.io/api/proxy/config/",
            json={"authorized_ips": auth_ips},
            headers=self.headers
        )
        return r.json()["authorized_ips"]

    def remove_authorized_ips(self, ips):
        authed_ips = self.fetch_authorized_ips()
        authed_ips = [x for x in authed_ips if x not in ips]
        r = rq.post(
            "https://proxy.webshare.io/api/proxy/config/",
            json={"authorized_ips": authed_ips},
            headers=self.headers
        )
        return r.status_code

    def fetch_proxies(self, region="US"):
        page = 1
        proxies = []
        next_page = True

        while next_page is not None:
            r = rq.get(
                f"https://proxy.webshare.io/api/proxy/list/?page={page}&countries={region}",
                headers=self.headers
            )
            j = r.json()
            proxies.extend(j["results"])
            next_page = j["next"]
            page += 1

        return proxies

    @retry(tries=5, delay=2)
    def fetch_public_ip(self):
        r = rq.get("https://api.ipify.org")
        if r.status_code == 200:
            self.public_ip = r.text.strip()
        else:
            r = rq.get("https://checkip.amazonaws.com'")
            if r.status_code == 200:
                self.public_ip = r.text.strip()

        return self.public_ip

    def fetch_proxies_dict(self):
        proxies = self.fetch_proxies()
        if self.userpass:
            proxies = [
                {
                    "http": f"http://{p['username']}:{p['password']}@{p['proxy_address']}:{p['ports']['http']}",
                    "https": f"http://{p['username']}:{p['password']}@{p['proxy_address']}:{p['ports']['http']}",

                } for p in proxies
            ]
        else:
            public_ip = self.fetch_public_ip()
            self.set_authorized_ips(public_ip)
            proxies = [
                {
                    "http": f"http://{p['proxy_address']}:{p['ports']['http']}",
                    "https": f"http://{p['proxy_address']}:{p['ports']['http']}",

                } for p in proxies
            ]

        random.shuffle(proxies)
        return proxies
