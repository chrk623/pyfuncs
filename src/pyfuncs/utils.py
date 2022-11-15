import re
import os
import time
import json
import logging
import numpy as np
import pandas as pd
import requests as rq
import multiprocessing
from datetime import datetime

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


def send_webhook(wehbook_url, msg="hi"):
    r = rq.post(wehbook_url, data={"content": msg})
    return r


def keep_webhook(webhook_url, msg_fn=lambda: "test", sec_to_sleep=60):
    """
    msg_fn returns a string to be sent to webhook

    example (track csv files):
        from glob import glob
        from pyfuncs.utils import keep_webhook
        def msg_fn():
            return str(len(glob(./test/*.csv)))
        keep_webhook(msg_fn=msg_fn, sec_to_sleep=120)
    """
    while True:
        send_webhook(
            webhook_url=webhook_url,
            msg=msg_fn()
        )
        time.sleep(sec_to_sleep)


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


def camel_to_underscore(df):
    original_cols = list(df.columns)
    new_cols = [re.sub("([A-Z])", "_\\1", x).lower() for x in original_cols]
    rename_dict = {old: new for old, new in zip(original_cols, new_cols)}
    df = df.rename(columns=rename_dict)

    return df


def split_list(x, n):
    x = np.array(x)
    x = np.array_split(x, n)
    x = [_.tolist() for _ in x]
    return x


def extract_dl(dl, return_df=False):
    out = []
    for d in dl:
        out.append(d)

    out_dict = {k: v for k, v in out[0].items()}
    for i, d in enumerate(out[1:]):
        for k, v in d.items():
            if len(v.shape) == 1:
                out_dict[k] = torch.cat([out_dict[k], v])
            else:
                out_dict[k] = torch.vstack([out_dict[k], v])

    out_dict = {k: v.numpy() for k, v in out_dict.items()}

    if return_df:
        return pd.DataFrame({k: v.tolist() for k, v in out_dict.items()})

    return out_dict


def check_chrome():
    chrome_version = os.popen("google-chrome --product-version").read()
    print(
        f"chrome version: {chrome_version}"
        f"https://chromedriver.chromium.org/downloads"
    )


def chrome_main_version():
    chrome_version = os.popen("google-chrome --product-version").read()
    return int(chrome_version.split(".")[0])


def date_range_days(start, end, by_day=0):
    # by_days = 0 means
    if by_day is None:
        return [(start, end)]
    out = []
    by = timedelta(days=by_day)

    while (start + by) < end:
        out.append((start, start + by))
        start = start + by + timedelta(days=1)

    if len(out) == 0:
        return [(start, end)]
    elif out[-1][1] != end:
        out.append((start, end))

    return out


def date_range_days(start, end, by_months=1, force_start_at_day1=False, force_end_at_eom=False):
    """
    :param start: start datetime
    :param end: end datetime
    :param by_months: months apart between each interval
    :param force_start_at_day1: force first start date to start at day 1
        True: start = "2021-12-05" then first start day will be "2021-12-01"
        False: opposite to above start = "2021-12-05" then first start day will the same
    :param force_end_at_eom:
        True: output range will be the end of the month for end's date
            i.e. end = "2021-12-05" then last end will be "2021-12-31"
        False: opposite to above
            i.e. end = "2021-12-05" then last end will be "the same
    :return:
    """
    if force_start_at_day1:
        start = datetime(
            year=start.year,
            month=start.month,
            day=1
        )

    out_starts = [start]
    out_ends = []
    # compute out_start
    while True:
        # next date's starting month
        next_month = out_starts[-1].month + 1
        # if + 1 = 13 then its next jan
        next_month = 1 if next_month > 12 else next_month
        # next date's starting year
        next_year = out_starts[-1].year
        # if next month = 1 then its next year
        next_year = next_year + 1 if next_month == 1 else next_year
        next_start = datetime(
            year=next_year,
            month=next_month,
            day=1
        )
        out_starts.append(next_start)
        if next_month == end.month and next_year == end.year:
            break

    # compute out_end
    for out_start in out_starts:
        # next month of the current date
        next_month = out_start.month + 1
        next_month = 1 if next_month > 12 else next_month
        # ending date is current 1st of next month - 1 day
        end_date = datetime(
            year=out_start.year,
            month=next_month,
            day=1
        ) - timedelta(days=1)
        out_ends.append(end_date)

    if not force_end_at_eom:
        out_ends[-1] = end

    out = []
    for i in range(0, len(out_starts), by_months):
        out.append((out_starts[i], out_ends[i]))

    return out


def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s


def clean_html(html):
    """
    Remove HTML markup from the given string.
    :param html: the HTML string to be cleaned
    :param remove_ref: try to remove the reference, remove
        all text after the last occurance of the word [R|r]eference
    :type html: str
    :rtype: str
    """
    cleaned = html.strip()
    cleaned = re.sub(" <sub> ", "", cleaned)
    cleaned = re.sub(" </sub> ", " ", cleaned)
    cleaned = re.sub(" <sup> ", "", cleaned)
    cleaned = re.sub(" </sup> ", " ", cleaned)
    cleaned = re.sub(" <em> ", "", cleaned)
    cleaned = re.sub(" </em> ", " ", cleaned)

    # First we remove inline JavaScript/CSS:
    # cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", cleaned)
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    # tidy up remove extra spaces
    cleaned = " ".join(cleaned.split())

    return cleaned


def timestamp2date(timestamp, text=False):
    timestamp_with_ms = timestamp
    dt = datetime.fromtimestamp(timestamp_with_ms / 1000)
    if text:
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return formatted_time

    return dt

def flatten_list(x):
	return list(itertools.chain(*x))

def split_df(df, num_chunks=None, chunk_size=None):
    # num_chunks: number of chunks to return
    # chunk_size: number of rows in each chunk
    if num_chunks is not None and chunk_size is not None:
        raise Exception("only provide ONE of num_chunk or chunk_size")

    if chunk_size is not None:
        num_chunks = np.ceil(df.shape[0] / chunk_size)

    return np.array_split(df, num_chunks)
