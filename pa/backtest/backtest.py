from datetime import datetime
from pathlib import Path
from queue import PriorityQueue
from threading import Event

from pa.backtest.oanda_backtest import OandaBacktestingData, OandaBacktestingGen
from pa.settings import (
    BROKER,
    INSTRUMENTS,
    ACCOUNT_CURRENCY,
)


def get_backtesting_gen(
    priority_queue: PriorityQueue, run_flag: Event, data_path: Path
):
    if BROKER == "OANDA":
        return OandaBacktestingGen(priority_queue, run_flag, data_path)
    else:
        return


def get_historical_gen(
    from_time: datetime,
    to_time: datetime,
    granularity: str = None,
    filename: str = None,
):
    if BROKER == "OANDA":
        return OandaBacktestingData(
            INSTRUMENTS, ACCOUNT_CURRENCY, from_time, to_time, granularity, filename
        )
    else:
        return
