from typing import List

from pa.api.api import get_api
from pa.settings import *
from pa.signal.signal import SignalStrategy
from pa.sizing.sizing import SizingStrategy


class PAError(Exception):
    def __init__(self, message):
        super().__init__(message)


def validate_settings():
    if BROKER not in ["OANDA"]:
        raise PAError("BROKER must be in ['OANDA']")
    if API_TOKEN is None or API_TOKEN == "":
        raise PAError("API_TOKEN must be non-empty")
    if type(LIVE) is not bool:
        raise PAError("LIVE must be a boolean value")
    if BROKER == "OANDA":
        if type(ACCOUNT_INDEX) is not int or ACCOUNT_INDEX < 0:
            raise PAError("ACCOUNT_INDEX must be a non-negative integer")
        if DATETIME_FORMAT not in ["RFC3339", "UNIX"]:
            raise PAError("DATETIME_FORMAT must be in ['RFC3339', 'UNIX']")
    if BROKER == "OANDA":
        api = get_api()
        instruments = [
            instrument["name"]
            for instrument in api.get_account_instruments()["instruments"]
        ]
        for instrument in INSTRUMENTS:
            if instrument not in instruments:
                raise PAError(f"Invalid instrument ({instrument}) in INSTRUMENTS")
    else:
        pass
    if LEVERAGE > 1 or LEVERAGE <= 0:
        raise PAError("LEVERAGE must be in the range (0, 1]")
    if type(LEVERAGE) != Decimal:
        raise PAError("LEVERAGE must be of type Decimal")
    if type(LIVE_STRATEGIES) is not tuple:
        raise PAError(
            "LIVE_STRATEGIES must be a tuple containing a signal and sizing strategy"
        )
    if not issubclass(type(LIVE_STRATEGIES[0]), SignalStrategy):
        raise PAError("The first entry in LIVE_STRATEGIES must subclass SignalStrategy")
    if not issubclass(type(LIVE_STRATEGIES[1]), SizingStrategy):
        raise PAError(
            "The second entry in LIVE_STRATEGIES must subclass SizingStrategy"
        )
    for strategy_pair in BACKTEST_STRATEGIES:
        if type(strategy_pair) is not tuple:
            raise PAError(
                "Each entry in BACKTEST_STRATEGIES must be a tuple containing a signal and sizing strategy"
            )
        if not issubclass(type(LIVE_STRATEGIES[0]), SignalStrategy):
            raise PAError(
                "The first entry in each tuple in BACKTEST_STRATEGIES must subclass SignalStrategy"
            )
        if not issubclass(type(LIVE_STRATEGIES[1]), SizingStrategy):
            raise PAError(
                "The second entry in each tuple in BACKTEST_STRATEGIES must subclass SizingStrategy"
            )
    if BALANCE <= 0:
        raise PAError("BALANCE must be greater than 0")
    if type(TERMINAL_COLORS) is not bool:
        raise PAError("TERMINAL_COLORS must be a boolean value")


def extend_instrument_list(instruments: List[str], account_currency: str) -> List[str]:
    if BROKER == "OANDA":
        api = get_api()
        possible_instruments = [
            instrument["name"]
            for instrument in api.get_account_instruments()["instruments"]
        ]
        final_instruments = []
        for instrument in instruments:
            if account_currency in instrument:
                pass
            else:
                for currency in instrument.split("_"):
                    if f"{currency}_{account_currency}" in possible_instruments:
                        final_instruments.append(f"{currency}_{account_currency}")
                    elif f"{account_currency}_{currency}" in possible_instruments:
                        final_instruments.append(f"{account_currency}_{currency}")
                    else:
                        raise PAError(
                            f"Impossible currency pair for {account_currency} and {currency}"
                        )
            final_instruments.append(instrument)
        return list(set(final_instruments))


def get_margins(instruments: List[str]):
    if BROKER == "OANDA":
        api = get_api()
        margins = {}
        for instrument in api.get_account_instruments()["instruments"]:
            if instrument["name"] in instruments:
                margin_rate = Decimal(instrument["marginRate"])
                if LEVERAGE > margin_rate:
                    margins[instrument["name"]] = LEVERAGE
                else:
                    margins[instrument["name"]] = margin_rate
            else:
                continue
