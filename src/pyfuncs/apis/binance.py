import pandas as pd
import requests as rq
from datetime import datetime


class Binance:
    def __init__(self, api_key="", proxy={}):
        self.api_key = api_key
        self.s = rq.session()
        self.s.proxies = proxy

    def _convert_timestampe(self, ts):
        return datetime.fromtimestamp(ts / 1000)

    def _get_spot_price(self, *args, **kwargs):
        params = {**kwargs}
        # remove any Nones
        params = {k: v for k, v in params.items() if v is not None}
        r = self.s.get("https://api.binance.com/api/v3/klines", params=params)
        if r.status_code != 200:
            return None
        return r.json()

    def _process_spot_price(self, symbol, prices):
        names = [
            "open_time", # Open time
            "open_price", # Open
            "high_price", # High
            "low_price",  # Low
            "close_price", # Close
            "volume", # Volume
            "close_time", # Close time
            "quote_asset_volume", # Quote asset volume
            "num_trades", # Number of trades
            "taker_buy_base_asset_volume", # Taker buy base asset volume
            "taker_buy_quote_asset_volume", # Taker buy quote asset volume
            "ignore" # Ignore
        ]
        out = []
        for i, p in enumerate(prices):
            out.append({
                "symbol": symbol,
                **{k: v for k, v in zip(names, p)}
            })
        df = pd.DataFrame(out)
        df.loc[:, "open_time"] = df.open_time.apply(lambda x: self._convert_timestampe(x))
        df.loc[:, "close_time"] = df.close_time.apply(lambda x: self._convert_timestampe(x))

        return df

    def spot_price(self, symbol, limit=10, interval=None, start_time=None, endTime=None):
        # limit max 1500, default 500
        # m -> minutes; h -> hours; d -> days; w -> weeks; M -> months
            # e.g., 1m, 3m, 15m, 1h, 12h, 1M
        prices = self._get_spot_price(
            symbol=symbol,
            limit=limit,
            interval=interval,
            start_time=start_time,
            endTime=endTime
        )
        if prices is None:
            return None

        prices = self._process_spot_price(symbol=symbol, prices=prices)

        return prices
