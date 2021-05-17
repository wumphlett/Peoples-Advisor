from decimal import Decimal
from queue import PriorityQueue
from threading import Event

from pa.api.oanda_api import OandaApi
from pa.event.event import PriceEvent
from pa.price.common import BasePricingGen
from pa.settings import api_token, live, account_index, datetime_format, instruments


class OandaPricingGen(BasePricingGen):
    def __init__(self, priority_queue: PriorityQueue, run_flag: Event):
        super().__init__()
        self.api = OandaApi(api_token, live, account_index, datetime_format)
        self.queue = priority_queue
        self.run_flag = run_flag

    def gen(self):
        pricing_stream = self.api.pricing_stream(instruments)
        for price in pricing_stream:
            if not self.run_flag.is_set():
                break
            price_event = PriceEvent(
                price["instrument"],
                self.api.oanda_time_to_datetime(price["time"]),
                Decimal(price["bids"][0]["price"]),
                Decimal(price["asks"][0]["price"]),
            )
            self.queue.put(price_event)
