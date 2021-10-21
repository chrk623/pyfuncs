import random
from .browser_uas import USER_AGENTS


class FakeUserAgent:
    def __init__(self, browser="all"):
        uas = USER_AGENTS

        if browser == "all":
            uas = [uas[k] for k, d in uas.items()]
            self.uas = [ua for browsers in uas for ua in browsers]
        else:
            self.uas = uas[browser]

    def __getattr__(self, attr):
        if attr == "random":
            return random.choice(self.uas)
