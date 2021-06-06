from decimal import Decimal
from queue import PriorityQueue
from threading import Event
from typing import List

from peoples_advisor.api.oanda.oanda_api import OandaApi
from peoples_advisor.common.common import extend_instrument_list
from peoples_advisor.event.event import PriceEvent, QuoteEvent
from peoples_advisor.price.common.common import BasePricingGen


class OandaPricingGen(BasePricingGen):
    def __init__(
        self,
        api_token: str,
        live: bool,
        account_index: int,
        datetime_format: str,
        instruments: List[str],
        account_currency: str,
        priority_queue: PriorityQueue,
        run_flag: Event,
        exit_flag: Event,
    ):
        super().__init__()
        self.instruments = instruments
        self.account_currency = account_currency
        self.api = OandaApi(api_token, live, account_index, datetime_format)
        self.queue = priority_queue
        self.run_flag = run_flag
        self.exit_flag = exit_flag

    def gen(self):
        try:
            all_instruments = extend_instrument_list(
                self.instruments, self.account_currency
            )
            pricing_stream = self.api.pricing_stream(all_instruments)
            for price in pricing_stream:
                if not self.run_flag.is_set():
                    break
                if price["instrument"] in self.instruments:
                    event = PriceEvent(
                        price["instrument"],
                        self.api.oanda_time_to_datetime(price["time"]),
                        Decimal(price["bids"][0]["price"]),
                        Decimal(price["asks"][0]["price"]),
                    )
                else:
                    event = QuoteEvent(
                        price["instrument"],
                        self.api.oanda_time_to_datetime(price["time"]),
                        Decimal(price["bids"][0]["price"]),
                        Decimal(price["asks"][0]["price"]),
                    )
                self.queue.put(event)
        except Exception:
            self.exit_flag.set()
            raise
