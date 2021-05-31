from abc import ABC
from decimal import Decimal
from typing import Optional
from datetime import datetime

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

    def __repr__(self):
        return f"PRICE,{self.instrument},{self.time.timestamp()},{self.bid},{self.ask}"


class InfoEvent(BaseEvent):
    def __init__(self, instrument: str, time: datetime, bid: Decimal, ask: Decimal):
        """
        Creates a price event to be passed along to the signal generator.

        Args:
            instrument (str): Name of the instrument
            time (datetime): Datetime object representing the time of the price signal
            bid (Decimal): Decimal object representing the bid price in appropriate units
            ask (Decimal): Decimal object representing the ask price in appropriate units
        """
        super().__init__(4, "INFO")
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return f'INFO  : Inst: {self.instrument} Time: {self.time.isoformat("T")} Bid: {self.bid} Ask: {self.ask}'

    def __repr__(self):
        return f"INFO,{self.instrument},{self.time.timestamp()},{self.bid},{self.ask}"


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
        return (
            f"SIGNAL,{self.instrument},{self.time.timestamp()},{self.side},{self.info}"
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


class StartEvent(BaseEvent):
    def __init__(self):
        super().__init__(1, "START")


class StopEvent(BaseEvent):
    def __init__(self):
        super().__init__(5, "STOP")


class ExitEvent(BaseEvent):
    def __init__(self):
        super().__init__(0, "EXIT")
