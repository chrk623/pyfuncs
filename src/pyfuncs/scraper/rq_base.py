import logging
import itertools
import pandas as pd
from .rotatable_session import RSession
from ..proxies.webshare import Webshare


class RqBase:
    patience = 3
    testing = False
    overall_progress = {"current": 0, "total": 0}
    overall_ticks = [] # ticks for [20%, 40%, 60%, 80%, 100%]
    webshare_options = {"userpass": False, "ensure_ip_authorized": False}

    def __init__(self, headers=None, run_type="base"):
        self.headers = headers
        self._init_logger(run_type)

    def _init_logger(self, run_type):
        if run_type not in ["base", "multi"]:
            raise Exception("run_type not in 'base' or 'multi'")
        if run_type == "multi":
            logging.basicConfig(level=logging.INFO, format="[%(asctime)s| %(levelname)s| %(threadName)s] %(message)s")
        else:
            logging.basicConfig(level=logging.INFO, format="[%(asctime)s| %(levelname)s] %(message)s")
        self.logger = logging

        # if run_type not in ["base", "multi"]:
        #     raise Exception("run_type not in 'base' or 'multi'")
        #
        # logger = logging.getLogger()
        # logger.setLevel(logging.INFO)
        # logger_handler = logging.StreamHandler()
        # logger.addHandler(logger_handler)
        # logFormatter = logging.Formatter(
        #     f"[%(asctime)s" \
        #     f" |%(levelname)s" \
        #     f"{' |%(threadName)s' if run_type == 'multi' else ''}] " \
        #     f"%(message)s"
        # )
        # logger_handler.setFormatter(logFormatter)
        # self.logger = logger

    def _generate_params(self, params):
        if params is None:
            return [None]
        
        if isinstance(params, list):
            return params
        
        for k, v in params.items():
            if not isinstance(params[k], list):
                params[k] = [params[k]]

        base_dict = {"url": params["url"]}
        url_len = len(base_dict["url"])
        _ = params.pop("url")

        combn_params = []
        combn_names = list(params.keys())
        for k, v in params.items():
            combn_params.append(params[k])
        combn_params = list(itertools.product(*combn_params))

        params_dict = []
        for combn in combn_params:
            for i, col in enumerate(combn):
                base_dict[combn_names[i]] = [col] * url_len
            params_dict.append(pd.DataFrame(base_dict))

        params_dict = pd.concat(params_dict).to_dict("records")
        self.overall_progress["total"] = len(params_dict)
        self.overall_ticks = [round(len(params_dict) * x) for x in [0.2, 0.4, 0.6, 0.8, 1]]

        return params_dict

    def _fetch_proxies(self, proxies, n=1):
        if type(proxies) not in [dict, list, str, type(None)]:
            raise Exception("check proxies input")

        if proxies is not None:
            if proxies == "webshare":
                ws = Webshare(**self.webshare_options)
                proxies = ws.fetch_proxies_dict()
            elif isinstance(proxies, dict):
                proxies = [proxies]
        else:
            proxies = [{}] * n

        return proxies

    def _scrape_once(self, session, param, progress_text):
        self.logger.info(f"scrape: {progress_text}, proxy[{session.proxy_cnt}]")
        r = self.scrape_once(session=session, param=param, progress_text=progress_text)
        return r

    def _extract_once(self, from_scrape, progress_text):
        self.logger.info(f"extract: {progress_text}")
        if from_scrape is None:
            out = None
        elif isinstance(from_scrape, list):
            out = []
            for r in from_scrape:
                if r is None or (isinstance(r, list) and len(r) == 0):
                    out.append(None)
                else:
                    try:
                        extracted = self.extract_once(from_scrape=r, progress_text=progress_text)
                    except:
                        self.logger.info(f"extract: failed, appending `None`")
                        extracted = None
                    out.append(extracted)
        else:
            out = self.extract_once(from_scrape=from_scrape, progress_text=progress_text)

        return out

    def scrape_once(self, session, param, progress_text):
        self.logger.info(f"{progress_text}")
        r = session.get(
            url=param["url"],
            params=param["params"]
        )
        return r

    def extract_once(self, from_scrape, progress_text):
        return from_scrape

    def fetch_session_and_params(self, thread_num=None):
        if self.run_type == "multi" and thread_num is None:
            self.logger.warning("thread_num=None not supported for multithreading, using thread=0")
            thread_num = 0

        params = self.params if thread_num is None else self.params[thread_num]
        session = RSession(
            proxy_list=self.proxies if thread_num is None else self.proxies[thread_num],
            base_headers=self.headers,
            patience=self.patience,
            logger=self.logger
        )
        return session, params

    def _run(self, thread_num=None):
        session, params = self.fetch_session_and_params(thread_num=thread_num)
        out = []
        for p_i, param in enumerate(params):
            progress_text = f"{p_i + 1}/{len(params)}"
            session.log_base_text = progress_text
            from_scrape = self._scrape_once(
                session=session,
                param=param,
                progress_text=progress_text,
            )
            session.rotate_ua_and_proxy()
            r = self._extract_once(
                from_scrape=from_scrape,
                progress_text=progress_text,
            )
            out.append(r)

            self.overall_progress["current"] += 1
            self._overall_log()

        if thread_num is None:
            self.out = out
        else:
            self.out[thread_num] = out

        self.logger.info("Scraping complete")

    def set_log_level(self, level):
        level = level.lower()
        if level in ["critical", "error", "warning", "info", "debug"]:
            if level == "debug":
                self.logger.setLevel(logging.DEBUG)
            elif level == "info":
                self.logger.setLevel(logging.INFO)
            elif level == "warning":
                self.logger.setLevel(logging.WARNING)
            elif level == "error":
                self.logger.setLevel(logging.ERROR)
            else:
                self.logger.setLevel(logging.CRITICAL)
        else:
            raise Exception(f"'{level}' is not a logging level")

    def _overall_log(self):
        if len(self.overall_ticks) > 0:
            if self.overall_progress["current"] >= self.overall_ticks[0]:
                self.logger.info(
                    f"Overall progress: "
                    f"{self.overall_progress['current']}/{self.overall_progress['total']}"
                )
                self.overall_ticks = self.overall_ticks[1:]

    @staticmethod
    def _finialize_output(x):
        if isinstance(x, list):
            if len(x[0]) == 0:
                x[0] = [None]
            while isinstance(x[0], list):
                x = list(itertools.chain.from_iterable(x))
        return x
