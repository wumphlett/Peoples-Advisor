from datetime import datetime
from pathlib import Path
from queue import PriorityQueue
from threading import Event
from typing import List

from pa.backtest.oanda_backtest import OandaBacktestingData, OandaBacktestingGen
from pa.settings import broker


def get_backtesting_gen(
    priority_queue: PriorityQueue, run_flag: Event, data_path: Path
):
    if broker == "OANDA":
        return OandaBacktestingGen(priority_queue, run_flag, data_path)
    else:
        return


def get_historical_gen(
    instruments: List[str],
    from_time: datetime,
    to_time: datetime,
    granularity: str = None,
    file_name: str = None,
):
    if broker == "OANDA":
        return OandaBacktestingData(
            instruments, from_time, to_time, granularity, file_name
        )
    else:
        return
