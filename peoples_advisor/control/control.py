from queue import PriorityQueue
from threading import Thread, Event

from peoples_advisor.event.event import ExitEvent, BaseEvent
from peoples_advisor.price.price import get_pricing_gen
#from peoples_advisor.portfolio.portfolio import Portfolio
from peoples_advisor.signal.signal import SignalStrategy
from peoples_advisor.sizing.sizing import SizingStrategy


class Control:
    def __init__(
        self,
        sig_strategy: SignalStrategy,
        size_strategy: SizingStrategy,
        backtesting=False,
    ):
        self.run_flag = Event()
        self.exit_flag = Event()
        self.events = PriorityQueue()
        self.backtesting = backtesting
        self.pricing_stream = Thread(
            target=get_pricing_gen(self.events, self.exit_flag).gen,
            daemon=True,
        )
        #self.portfolio = Portfolio()
        self.sig_strategy = sig_strategy
        self.size_strategy = size_strategy
        if not self.backtesting:
            self.pricing_stream.start()

    def run(self):
        while not self.exit_flag.is_set():
            event = self.events.get(block=True)
            # Event if else chain is ordered by the priority of their associated events
            if event.type == "EXIT":  # Exit the control program
                self.exit_flag.set()
            elif event.type == "START":  # Start threads
                self.run_flag.set()
            elif event.type == "STOP":
                self.run_flag.clear()
            elif self.run_flag.is_set():
                if event.type == "ORDER":  # Pass order events to portfolio monitor maybe
                    pass
                elif event.type == "SIGNAL":  # Pass signal events to order gen
                    order_event = self.size_strategy.gen_order(event)
                    self.queue_event(order_event)
                elif event.type == "PRICE":  # Pass price events to signal gen
                    print(event)
                    #self.portfolio.update_price(event)
                    signal_event = self.sig_strategy.gen_signal(event)
                    self.queue_event(signal_event)
                elif event.type == "QUOTE":
                    #self.portfolio.update_price(event)
                    pass
            else:
                pass
            self.events.task_done()

    def queue_event(self, event: BaseEvent = None):
        if not self.exit_flag.is_set() and event is not None:
            self.events.put(event)
