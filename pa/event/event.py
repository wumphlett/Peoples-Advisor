from abc import ABC
from datetime import datetime
from decimal import Decimal

from pa.api.oanda_api import OrderRequest


class BaseEvent(ABC):
    def __init__(self, priority: int, event_type: str):
        self.priority = priority
        self.type = event_type

    def __lt__(self, other):
        return self.priority <= other.priority

    def __eq__(self, other):
        return self.priority == other.priority


class PriceEvent(BaseEvent):
    def __init__(self, instrument: str, time: datetime, bid: Decimal, ask: Decimal):
        """
        Creates a price event to be passed along to the signal generator.

        Args:
            instrument (str): Name of the instrument
            time (datetime): Datetime object representing the time of the price signal
            bid (Decimal): Decimal object representing the bid price in appropriate units
            ask (Decimal): Decimal object representing the ask price in appropriate units
        """
        super().__init__(4, "PRICE")
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return f'PRICE : Inst: {self.instrument} Time: {self.time.isoformat("T")} Bid: {self.bid} Ask: {self.ask}'


class SignalEvent(BaseEvent):
    def __init__(self, instrument: str, time: datetime, side: str):
        """
        Creates a signal event to be passed along to the order generator.

        Args:
            instrument (str): Name of the instrument
            time (datetime): Datetime object representing the time of the price signal
            side (str) ['BUY', 'SELL']: What type of signal it is, choose either 'BUY', 'SELL'
        """
        super().__init__(3, "SIGNAL")
        self.instrument = instrument
        self.time = time
        self.side = side

    def __str__(self):
        return f'SIGNAL: Inst: {self.instrument} Time: {self.time.isoformat("T")} Side: {self.side}'


class OrderEvent(BaseEvent):
    def __init__(
        self, instrument: str, time: datetime, units: Decimal, order: OrderRequest
    ):  # TODO Abstracted OrderRequest?
        super().__init__(2, "ORDER")
        self.instrument = instrument
        self.time = time
        self.units = units
        self.order = order

    def __str__(self):
        return f'ORDER : Inst: {self.instrument} Time: {self.time.isoformat("T")} Units: {self.units} Type: {self.order.type}'


class StartEvent(BaseEvent):
    def __init__(self):
        super().__init__(1, "START")


class StopEvent(BaseEvent):
    def __init__(self):
        super().__init__(5, "STOP")


class ExitEvent(BaseEvent):
    def __init__(self):
        super().__init__(0, "EXIT")


class EOFEvent(BaseEvent):  # TODO Needed?
    def __init__(self):
        super().__init__(5, "EOF")


# TODO Transaction/Size Event?

# TODO Control Event? Stop start and "live"/backtest and paper/live?
