from decimal import Decimal

from pa.api.oanda_api import MarketOrderRequest
from pa.event.event import SignalEvent, OrderEvent
from pa.signal.signal import SignalStrategy
from pa.sizing.sizing import SizingStrategy


class TestSignalStrategy(SignalStrategy):
    def __init__(self):
        super().__init__()
        self.ticks = 0

    def gen_signal(self, price):
        self.ticks += 1
        if self.ticks % 10 == 0:
            return SignalEvent(price.instrument, price.time, "BUY")
        elif self.ticks % 5 == 0:
            return SignalEvent(price.instrument, price.time, "SELL")
        else:
            return


class TestSizingStrategy(SizingStrategy):
    def __init__(self):
        super().__init__()
        self.ticks = 0

    def gen_order(self, signal: SignalEvent):
        self.ticks += 1
        if self.ticks % 5 == 0:
            inst = signal.instrument
            sign = 1 if signal.side == "BUY" else -1
            units = Decimal(100) * sign
            return OrderEvent(
                inst, signal.time, units, MarketOrderRequest(inst, float(units))
            )
        else:
            return
