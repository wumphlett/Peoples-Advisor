from decimal import Decimal

from peoples_advisor.api.oanda.oanda_api import MarketOrderRequest
from peoples_advisor.event.event import SignalEvent, OrderEvent
from peoples_advisor.signal.signal import SignalStrategy
from peoples_advisor.sizing.sizing import SizingStrategy


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
