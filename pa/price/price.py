from queue import PriorityQueue
from threading import Event

from pa.price.oanda_price import OandaPricingGen
from pa.settings import (
    BROKER,
    API_TOKEN,
    LIVE,
    ACCOUNT_INDEX,
    DATETIME_FORMAT,
    INSTRUMENTS,
    ACCOUNT_CURRENCY,
)


def get_pricing_gen(priority_queue: PriorityQueue, run_flag: Event, exit_flag: Event):
    if BROKER == "OANDA":
        return OandaPricingGen(
            API_TOKEN,
            LIVE,
            ACCOUNT_INDEX,
            DATETIME_FORMAT,
            INSTRUMENTS,
            ACCOUNT_CURRENCY,
            priority_queue,
            run_flag,
            exit_flag,
        )
    else:
        return
