# set webshare api key if not already in envoirnment
import os
os.environ["WEBSHARE_KEY"] = ""

from pyfuncs.scraper.rq import RqMulti


class Scraper(RqMulti):
    def __init__(self,  num_threads=1, headers=None, params=None, proxies=None):
        super().__init__(
            num_threads=num_threads,
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