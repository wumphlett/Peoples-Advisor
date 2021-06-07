from abc import ABC, abstractmethod


class BaseOrder(ABC):
    def __init__(self, conditional: bool):
        self.conditional = conditional


class MarketOrder(BaseOrder):
    def __init__(self):
        super().__init__(False)


class LimitOrder(BaseOrder):
    def __init__(self):
        super().__init__(True)


class StopOrder(BaseOrder):
    def __init__(self):
        super().__init__(True)


class TakeProfitOrder(BaseOrder):
    def __init__(self):
        super().__init__(True)


class StopLossOrder(BaseOrder):
    def __init__(self):
        super().__init__(True)


class MarketIfTouchedOrder(BaseOrder):
    def __init__(self):
        super().__init__(True)


class TrailingStopOrder(BaseOrder):
    def __init__(self):
        super().__init__(True)
