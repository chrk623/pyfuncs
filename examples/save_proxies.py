import json
from pyfuncs.proxies.webshare import Webshare


ws = Webshare(key="")

# save dict {"http": ..., "https": ...} as json
# proxies = ws.fetch_proxies_dict()

# save list "ip:port" as json
# proxies = ws.fetch_proxies()
# proxies = [p["proxy_address"] + ":" + str(p["ports"]["http"]) for p in proxies]

json.dump(proxies, open("proxies.json", "w"), indent=2)
