from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from datetime import datetime

from peoples_advisor.api.oanda.oanda_api import OrderRequest


class BaseEvent(ABC):
    def __init__(self, priority: int, event_type: str):
        self.priority = priority
        self.type = event_type

    def __lt__(self, other):
        return self.priority <= other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @staticmethod
    @abstractmethod
    def from_repr(representation):
        pass


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

    def __repr__(self):
        return f"PRICE,{self.instrument},{int(self.time.timestamp())},{self.bid},{self.ask}"

    @staticmethod
    def from_repr(representation):
        args = representation.split(",")
        return PriceEvent(
            args[1],
            datetime.fromtimestamp(int(args[2])),
            Decimal(args[3]),
            Decimal(args[4]),
        )


class QuoteEvent(BaseEvent):
    def __init__(self, instrument: str, time: datetime, bid: Decimal, ask: Decimal):
        """
        Identical to PriceEvents, but not consumed by SignalStrategy, just used to convert currency

        Args:
            instrument (str): Name of the instrument
            time (datetime): Datetime object representing the time of the price signal
            bid (Decimal): Decimal object representing the bid price in appropriate units
            ask (Decimal): Decimal object representing the ask price in appropriate units
        """
        super().__init__(4, "QUOTE")
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return f'QUOTE  : Inst: {self.instrument} Time: {self.time.isoformat("T")} Bid: {self.bid} Ask: {self.ask}'

    def __repr__(self):
        return f"QUOTE,{self.instrument},{int(self.time.timestamp())},{self.bid},{self.ask}"

    @staticmethod
    def from_repr(representation):
        args = representation.split(",")
        return QuoteEvent(
            args[1],
            datetime.fromtimestamp(int(args[2])),
            Decimal(args[3]),
            Decimal(args[4]),
        )


class SignalEvent(BaseEvent):
    def __init__(
        self, instrument: str, time: datetime, side: str, info: Optional[dict] = None
    ):
        """
        Creates a signal event to be passed along to the order generator.

        Args:
            instrument (str): Name of the instrument
            time (datetime): Datetime object representing the time of the price signal
            side (str) ['BUY', 'SELL']: What type of signal it is, choose either 'BUY', 'SELL'
            info (dict, optional): Whatever info you want to pass on
        """
        super().__init__(3, "SIGNAL")
        self.instrument = instrument
        self.time = time
        self.side = side
        self.info = info

    def __str__(self):
        return f'SIGNAL: Inst: {self.instrument} Time: {self.time.isoformat("T")} Side: {self.side}'

    def __repr__(self):
        return f"SIGNAL,{self.instrument},{int(self.time.timestamp())},{self.side},{self.info}"

    @staticmethod
    def from_repr(representation):
        args = representation.split(",")
        return SignalEvent(
            args[1], datetime.fromtimestamp(int(args[2])), args[3], eval(args[4])
        )


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

    def __repr__(self):
        pass

    @staticmethod
    def from_repr(representation):
        pass


class StartEvent(BaseEvent):
    def __init__(self):
        super().__init__(1, "START")

    def __str__(self):
        return "START :"

    def __repr__(self):
        return "START"

    @staticmethod
    def from_repr(representation):
        return StartEvent()


class StopEvent(BaseEvent):
    def __init__(self):
        super().__init__(5, "STOP")

    def __str__(self):
        return "STOP  :"

    def __repr__(self):
        return "STOP"

    @staticmethod
    def from_repr(representation):
        return StopEvent()


class ExitEvent(BaseEvent):
    def __init__(self):
        super().__init__(0, "EXIT")

    def __str__(self):
        return "EXIT  :"

    def __repr__(self):
        return "EXIT"

    @staticmethod
    def from_repr(representation):
        return ExitEvent()


def event_from_repr(repr_string):
    repr_string = repr_string.replace("\n", "")
    event_type = repr_string.split(",")[0].title() + "Event"
    return eval(f"{event_type}.from_repr('{repr_string}')")
