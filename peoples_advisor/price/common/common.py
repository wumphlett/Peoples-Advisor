from abc import ABC, abstractmethod
from datetime import datetime


class BasePricingGen(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def gen(self):
        pass


def standard_filename(from_time: datetime, to_time: datetime):
    filename = from_time.strftime("%Y.%m.%dT%H.%M.%S") + "-" + to_time.strftime("%Y.%m.%dT%H.%M.%S")
    filename = "LIVE-[" + filename + "]"
    return filename
