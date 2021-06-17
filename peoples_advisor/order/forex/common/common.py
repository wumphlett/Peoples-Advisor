from abc import ABC, abstractmethod
from decimal import Decimal


class BaseOrder(ABC):
    def __init__(self, order_type: str, instrument: str, units: int):
        self.type = order_type
        self.instrument = instrument
        self.units = units


class MarketOrder(BaseOrder):
    def __init__(self, instrument: str, units: int):
        super().__init__("MARKET", instrument, units)


class ConditionalOrder(BaseOrder):
    def __init__(self, order_type: str, instrument: str, units: int, trigger_price: Decimal):
        super().__init__(order_type, instrument, units)
        self.trigger_price = trigger_price

    @abstractmethod
    def trigger(self, price: Decimal) -> bool:
        pass


class LimitOrder(ConditionalOrder):
    def __init__(self, instrument: str, units: int, trigger_price: Decimal):
        super().__init__("LIMIT", instrument, units, trigger_price)

    def trigger(self, price: Decimal) -> bool:
        if self.units > 0:
            return price <= self.trigger_price
        elif self.units < 0:
            return price >= self.trigger_price


class StopOrder(ConditionalOrder):
    def __init__(self, instrument: str, units: int, trigger_price: Decimal):
        super().__init__("STOP", instrument, units, trigger_price)

    def trigger(self, price: Decimal) -> bool:
        if self.units > 0:
            return price >= self.trigger_price
        elif self.units < 0:
            return price <= self.trigger_price


class TakeProfitOrder(ConditionalOrder):
    def __init__(self, instrument: str, units: int, trigger_price: Decimal):
        super().__init__("TAKE_PROFIT", instrument, units, trigger_price)

    def trigger(self, price: Decimal) -> bool:
        if self.units > 0:
            return price <= self.trigger_price
        elif self.units < 0:
            return price >= self.trigger_price


class StopLossOrder(ConditionalOrder):
    def __init__(self, instrument: str, units: int, trigger_price: Decimal):
        super().__init__("STOP_LOSS", instrument, units, trigger_price)

    def trigger(self, price: Decimal) -> bool:
        if self.units > 0:
            return price >= self.trigger_price
        elif self.units < 0:
            return price <= self.trigger_price


class MarketIfTouchedOrder(ConditionalOrder):
    def __init__(self, instrument: str, units: int, trigger_price: Decimal):
        super().__init__("MARKET_IF_TOUCHED", instrument, units, trigger_price)

    def trigger(self, price: Decimal) -> bool:
        if self.units > 0:
            return price <= self.trigger_price
        elif self.units < 0:
            return price >= self.trigger_price


class TrailingStopOrder(ConditionalOrder):
    def __init__(self, instrument: str, units: int, trigger_price: Decimal):
        super().__init__("TRAILING_STOP", instrument, units, trigger_price)

    def trigger(self, price: Decimal) -> bool:
        if self.units > 0:
            return price >= self.trigger_price
        elif self.units < 0:
            return price <= self.trigger_price
