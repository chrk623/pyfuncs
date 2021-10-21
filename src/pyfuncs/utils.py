import os
import json
import logging
import numpy as np
import pandas as pd
import requests as rq
import multiprocessing


HOME = os.path.expanduser("~")
_RETURN_NONE = (lambda: None).__code__.co_code


minimal_headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en;q=0.9",
}


def create_logger():
    """
    create logger for your instance
    """
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s| %(name)s| %(levelname)s| %(processName)s] %(message)s"
    )
    handler = logging.FileHandler("output.log")
    handler.setFormatter(formatter)

    # log to console as well
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)

    # this bit will make sure you won't have
    # duplicated messages in the output
    if not len(logger.handlers):
        logger.addHandler(handler)
        logger.addHandler(consoleHandler)

    return logger


def send_webook(wehbook_url, msg="hi"):
    r = rq.post(wehbook_url, data={"content": msg})
    return r


def proxy_location(proxy):
    r = rq.get(url="http://ip-api.com/json", proxies=proxy)
    r = r.json()

    if r["status"] == "success":
        return {
            "ip": r["query"],
            "country": r["country"],
            "region": r["regionName"],
            "city": r["city"],
        }

    return None


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def dh(txt, path=os.path.join(HOME, "Desktop/test.html")):
    with open(path, "w") as f:
        f.write(txt)


def dj(j, path=os.path.join(HOME, "Desktop/test.json")):
    json.dump(j, open(path, "w"), indent=2)


def ifelse(cond, true, false):
    return true if cond else false


def is_pass(f):
    return f.__code__.co_code == _RETURN_NONE


def is_na(obj):
    """general na, "", None detection
    Args:
        obj ([type]): input object, can be off anything in theory
    """
    if pd.isna(obj):
        return True
    elif obj == "":
        return True
    elif obj == None:
        return True
    else:
        return False


def to_str(x):
    return None if x is None else str(x)


def to_float(x):
    return None if x is None else float(x)


def to_int(x):
    return None if x is None else int(x)


def split_list(x, n):
    x = np.array(x)
    x = np.array_split(x, n)
    x = [_.tolist() for _ in x]
    return x


def check_chrome():
    chrome_version = os.popen("google-chrome --product-version").read()
    print(
        f"chrome version: {chrome_version}"
        f"https://chromedriver.chromium.org/downloads"
    )
