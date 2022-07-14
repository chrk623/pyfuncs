import os
os.environ["WEBSHARE_KEY"] = ""

import pandas as pd
from pyfuncs.apis.binance import Binance
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
        b = Binance(proxy=session.proxies)
        p = b.spot_price(
            symbol=param["symbol"],
            limit=param["limit"],
            interval=param["interval"]
        )
        return p

    def extract_once(self, from_scrape, progress_text=""):
        return from_scrape

symbols = [
    "ETH",
    "UNI",
    "MANA",
    "LINK",
    "ENJ",
    "GALA"
]
symbols = [s + "BUSD" for s in symbols]
symbols = pd.DataFrame({"symbol": symbols})
symbols.loc[:, "limit"] = 1500
symbols.loc[:, "interval"] = "1d"
symbols = symbols.to_dict("records")
s = Scraper(num_threads=20, proxies="webshare", params=symbols)
df = s.run()
