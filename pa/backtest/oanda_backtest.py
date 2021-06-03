from decimal import Decimal
from queue import PriorityQueue
from threading import Event
from typing import List

from pa.api.oanda_api import OandaApi
from pa.api.unofficial_oanda_api import get_historical_spreads
from pa.backtest.common import *
from pa.common.common import extend_instrument_list
from pa.event.event import PriceEvent, QuoteEvent, StopEvent, event_from_repr


class OandaBacktestingData(BaseBacktestingData):
    def __init__(
        self,
        api_token: str,
        instruments: List[str],
        account_currency: str,
        from_time: datetime,
        to_time: datetime,
        granularity: str = None,
        filename: str = None,
    ):
        super().__init__()
        self.api = OandaApi(api_token, live=False, datetime_format="UNIX")
        self.instruments = instruments
        self.account_currency = account_currency
        self.from_datetime = from_time
        self.to_datetime = to_time
        self.gran = granularity
        if not filename:
            filename = standard_filename(from_time, to_time, instruments)
        self.filepath = history_filepath(filename)
        self.filename = filename

    def gen(self):
        start = self.from_datetime.timestamp()
        end = self.to_datetime.timestamp()
        all_instruments = extend_instrument_list(
            self.instruments, self.account_currency
        )
        prices, spreads, pointers = {}, {}, {}
        # Initialize the first page of prices for each instrument and initialize the pointers to walk the lists
        for instrument in all_instruments:
            candles = self.api.get_instrument_candles(
                instrument, from_time=str(start), count=5000, granularity=self.gran
            )
            candles = candles.get("candles")
            if len(candles) > 0:
                prices.update({instrument: candles})
                spreads.update(
                    {
                        instrument: get_historical_spreads(
                            instrument, since=self.from_datetime
                        )
                    }
                )
                pointers.update({instrument: {"price": 0, "spread": 0}})

        with open(self.filepath, "w") as f:
            # Begin walking the lists and adding prices in chronological order
            while len(prices.keys()) > 0:
                earliest = []
                rem_list = []
                for inst in prices:
                    if pointers[inst]["price"] < len(prices[inst]):
                        cur_price_time = float(
                            prices[inst][pointers[inst]["price"]]["time"]
                        )
                        if cur_price_time < end:
                            earliest.append((cur_price_time, inst))
                        else:  # The times for a given instrument has exceeded the end time, remove from prices dict
                            rem_list.append(inst)
                    else:  # The prices dict needs to be updated with the next page of results
                        candles = self.api.get_instrument_candles(
                            inst,
                            from_time=prices[inst][-1]["time"],
                            count=5000,
                            granularity=self.gran,
                        )
                        candles = candles.get("candles")
                        if len(candles) > 1 and float(candles[0]["time"]) < end:
                            earliest.append((float(candles[0]["time"]), inst))
                            prices[inst] = candles
                            pointers[inst]["price"] = 0
                        else:  # Next page of results is not valid, remove instrument from prices dict
                            rem_list.append(inst)
                # Remove finished instruments from their dicts
                for inst in rem_list:
                    prices.pop(inst)
                    spreads.pop(inst)
                    pointers.pop(inst)
                # Determine next chronological element
                earliest.sort(key=lambda x: x[0])  # Sort by timestamps
                if len(earliest) > 0:
                    next_time, next_inst = earliest[0][0], earliest[0][1]
                    # Advance the spread pointer to the appropriate spread
                    # Due to the nature of the api, the spreads dict contains all the spreads from start to current day
                    # Therefore, there is no need to paginate as was done with the prices
                    while (
                        pointers[next_inst]["spread"] + 1 < len(spreads[next_inst])
                        and spreads[next_inst][pointers[next_inst]["spread"]][0]
                        < next_time
                    ):
                        # Advance spread pointer to the appropriate spread value
                        pointers[next_inst]["spread"] += 1
                    # Calculate the spread in price units
                    price_str = prices[next_inst][pointers[next_inst]["price"]]["mid"][
                        "c"
                    ]
                    pip_spread = Decimal(
                        spreads[next_inst][pointers[next_inst]["spread"]][1]
                    ) / Decimal(2)
                    place = len(price_str.split(".")[1]) - 1
                    # Calculate the price
                    price = Decimal(
                        prices[next_inst][pointers[next_inst]["price"]]["mid"]["c"]
                    )
                    spread = pip_spread * (Decimal("10") ** -place)
                    # Write price to file
                    # This approximates bid and ask for a given candle using its closing price and the spread
                    if next_inst in self.instruments:
                        price_event = PriceEvent(
                            next_inst,
                            datetime.fromtimestamp(next_time),
                            (price - spread).quantize(Decimal("10") ** (-1 - place)),
                            (price + spread).quantize(Decimal("10") ** (-1 - place)),
                        )
                    else:
                        price_event = QuoteEvent(
                            next_inst,
                            datetime.fromtimestamp(next_time),
                            (price - spread).quantize(Decimal("10") ** (-1 - place)),
                            (price + spread).quantize(Decimal("10") ** (-1 - place)),
                        )
                    f.write(repr(price_event) + "\n")
                    # Advance instrument price pointer
                    pointers[next_inst]["price"] += 1
                    # yield for progress indication in cli
                    yield


class OandaBacktestingGen(BaseBacktestingGen):
    def __init__(self, priority_queue: PriorityQueue, run_flag: Event, data_path: Path):
        super().__init__()
        self.queue = priority_queue
        self.data_path = data_path
        self.run_flag = run_flag

    def gen(self):
        with open(self.data_path) as f:
            for price in f:
                if not self.run_flag.is_set():
                    break
                price_event = event_from_repr(price)
                self.queue.put(price_event)
                yield
            self.queue.put(StopEvent())
