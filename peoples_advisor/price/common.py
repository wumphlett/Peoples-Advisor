from abc import ABC, abstractmethod


class BasePricingGen(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def gen(self):
        pass
