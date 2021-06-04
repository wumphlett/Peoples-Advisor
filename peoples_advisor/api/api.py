from typing import Optional

from peoples_advisor.api.oanda_api import OandaApi
from peoples_advisor.settings import (
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
