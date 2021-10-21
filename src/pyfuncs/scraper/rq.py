import threading
from ..utils import split_list
from .rq_base import RqBase


class RqSingle(RqBase):
    run_type = "base"

    def __init__(self, headers=None, params=None, proxies=None):
        super().__init__(headers=headers, run_type=self.run_type)
        self._init_output_list()
        self.params = self._generate_params(params)
        self.proxies = self._fetch_proxies(proxies)

    def _init_output_list(self):
        self.out = []

    def scrape_once(self, session, param, progress_text=""):
        self.logger.info(f"{progress_text}")
        r = session.get(
            url=param["url"],
            params=param["params"],
        )
        return r

    def extract_once(self, from_scrape, progress_text=""):
        return from_scrape

    def run(self):
        self._init_output_list()
        self._run(thread_num=None)
        return self._finialize_output(self.out)


class RqMulti(RqBase):
    run_type = "multi"

    def __init__(self, num_threads=1, headers=None, params=None, proxies=None):
        super().__init__(headers=headers, run_type=self.run_type)
        self.num_threads = num_threads
        self._init_output_list(self.num_threads)
        self._check_and_split_params(params, self.num_threads)
        self._check_and_split_proxies(proxies, self.num_threads)

    def _init_output_list(self, n):
        self.out = [[] for _ in range(n)]

    def _check_and_split_params(self, params, n):
        params_dict = self._generate_params(params=params)
        params_dict = split_list(params_dict, n)
        self.params = params_dict

    def _check_and_split_proxies(self, proxies, n):
        proxies = self._fetch_proxies(proxies=proxies, n=n)
        proxies = split_list(proxies, n)
        self.proxies = proxies

    def scrape_once(self, session, param, progress_text=""):
        self.logger.info(f"{progress_text}")
        r = session.get(
            url=param["url"],
            params=param["params"],
        )
        return r

    def extract_once(self, from_scrape, progress_text=""):
        return from_scrape

    def run(self):
        threads = []
        self._init_output_list(self.num_threads)
        for i in range(self.num_threads):
            self.logger.info(f"Starting thread {i}")
            t = threading.Thread(target=self._run, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return self._finialize_output(self.out)
