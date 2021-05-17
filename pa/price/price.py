from queue import PriorityQueue
from threading import Event

from pa.price.oanda_price import OandaPricingGen
from pa.settings import broker


def get_pricing_gen(priority_queue: PriorityQueue, run_flag: Event):
    if broker == "OANDA":
        return OandaPricingGen(priority_queue, run_flag)
    else:
        return
