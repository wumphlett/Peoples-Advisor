from typing import Optional

from pa.api.oanda_api import OandaApi
from pa.settings import broker


def get_api(
    auth: str,
    live: bool = False,
    account_index: Optional[int] = 0,
    datetime_format: Optional[str] = "RFC3339",
):
    if broker == "OANDA":
        return OandaApi(auth, live, account_index, datetime_format)
    else:
        return


"""
def get_pricing_stream():
    if broker == "OANDA":
        return OandaPricingGen
    else:
        return


def get_backtest_stream():
    if broker == "OANDA":
        return OandaBacktestingPricingGen
    else:
        return
"""
