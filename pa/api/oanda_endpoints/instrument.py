import requests
from pa.api.oanda import (
    api_version,
    practice_url,
    live_url
)


def get_instrument_candles(live, api_token, instrument, params):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/instruments/{i}/candles'.format(url=base_url, v=api_version, i=instrument)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers, params=params).json()


def get_instrument_order_book(live, api_token, instrument, params):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/instruments/{i}/orderBook'.format(url=base_url, v=api_version, i=instrument)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers, params=params).json()


def get_instrument_position_book(live, api_token, instrument, params):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/instruments/{i}/positionBook'.format(url=base_url, v=api_version, i=instrument)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers, params=params).json()
