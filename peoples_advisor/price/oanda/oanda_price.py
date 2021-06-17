import os
from decimal import Decimal
from datetime import datetime
from queue import PriorityQueue
from threading import Event
from typing import List

from peoples_advisor.api.oanda.oanda_api import OandaApi
from peoples_advisor.backtest.common.common import history_filepath
from peoples_advisor.common.common import extend_instrument_list
from peoples_advisor.event.event import PriceEvent, QuoteEvent
from peoples_advisor.price.common.common import BasePricingGen, standard_filename


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
        exit_flag: Event,
        save_to_file: bool = None,
    ):
        super().__init__()
        self.instruments = instruments
        self.account_currency = account_currency
        self.api = OandaApi(api_token, live, account_index, datetime_format)
        self.queue = priority_queue
        self.exit_flag = exit_flag
        self.save_to_file = save_to_file

    def gen(self):
        try:
            if self.save_to_file:
                save_file = open(history_filepath("currently_collecting.txt"), "w")
                start_time = datetime.now()
            all_instruments = extend_instrument_list(self.instruments, self.account_currency)
            pricing_stream = self.api.pricing_stream(all_instruments)
            for price in pricing_stream:
                if self.exit_flag.is_set():
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
                if self.save_to_file:
                    save_file.write(repr(event) + "\n")
                    save_file.flush()
            if self.save_to_file:
                save_file.close()
                end_time = datetime.now()
                cur_file_name = history_filepath("currently_collecting.txt", delete=False)
                save_file_name = history_filepath(standard_filename(start_time, end_time))
                cur_file_name.rename(save_file_name)
        except FileNotFoundError:
            pass
        except Exception:
            self.exit_flag.set()
            raise
