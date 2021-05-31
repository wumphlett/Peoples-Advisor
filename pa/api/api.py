from typing import Optional

from pa.api.oanda_api import OandaApi
from pa.settings import (
    BROKER,
    API_TOKEN,
    LIVE,
    ACCOUNT_INDEX,
    DATETIME_FORMAT,
)


def get_api():
    if BROKER == "OANDA":
        return OandaApi(API_TOKEN, LIVE, ACCOUNT_INDEX, DATETIME_FORMAT)
    else:
        return
