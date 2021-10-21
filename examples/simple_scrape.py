# set webshare api key if not already in envoirnment
import os
os.environ["WEBSHARE_KEY"] = ""

from pyfuncs.scraper.rq import RqSingle


class Scraper(RqSingle):
    def __init__(self,  headers=None, params=None, proxies=None):
        super().__init__(
            headers=headers,
            params=params,
            proxies=proxies
        )

    def scrape_once(self, session, param, progress_text=""):
        # print(progress_text)
        r = session.get(url="http://ip-api.com/json")
        return r

    def extract_once(self, from_scrape, progress_text=""):
        return from_scrape.json()


s = Scraper(proxies="webshare")
s.run()