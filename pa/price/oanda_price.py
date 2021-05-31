from decimal import Decimal
from queue import PriorityQueue
from threading import Event

from pa.api.oanda_api import OandaApi
from pa.common.common import extend_instrument_list
from pa.event.event import PriceEvent, InfoEvent
from pa.price.common import BasePricingGen
from pa.settings import (
    API_TOKEN,
    LIVE,
    ACCOUNT_INDEX,
    DATETIME_FORMAT,
    INSTRUMENTS,
    ACCOUNT_CURRENCY,
)


class OandaPricingGen(BasePricingGen):
    def __init__(
        self, priority_queue: PriorityQueue, run_flag: Event, exit_flag: Event
    ):
        super().__init__()
        self.api = OandaApi(API_TOKEN, LIVE, ACCOUNT_INDEX, DATETIME_FORMAT)
        self.queue = priority_queue
        self.run_flag = run_flag
        self.exit_flag = exit_flag

    def gen(self):
        try:
            all_instruments = extend_instrument_list(INSTRUMENTS, ACCOUNT_CURRENCY)
            pricing_stream = self.api.pricing_stream(all_instruments)
            for price in pricing_stream:
                if not self.run_flag.is_set():
                    break
                if price["instrument"] in INSTRUMENTS:
                    event = PriceEvent(
                        price["instrument"],
                        self.api.oanda_time_to_datetime(price["time"]),
                        Decimal(price["bids"][0]["price"]),
                        Decimal(price["asks"][0]["price"]),
                    )
                else:
                    event = InfoEvent(
                        price["instrument"],
                        self.api.oanda_time_to_datetime(price["time"]),
                        Decimal(price["bids"][0]["price"]),
                        Decimal(price["asks"][0]["price"]),
                    )
                self.queue.put(event)
        except Exception:
            self.exit_flag.set()
            raise
