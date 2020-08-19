import json
import requests
from pa.api.oanda import (
    api_version,
    practice_url,
    live_url
)


def get_positions(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/positions'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_open_positions(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/openPositions'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_instrument_position(live, api_token, account_id, instrument):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/positions/{i}'.format(url=base_url, v=api_version, id=account_id, i=instrument)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def put_close_position(live, api_token, account_id, instrument, close_dict):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/positions/{i}/close'.format(url=base_url, v=api_version, id=account_id, i=instrument)
    headers = {
        'Authorization': 'Bearer {api_token}'.format(api_token=api_token),
        'Content-Type': 'application/json'
    }
    close_dict = json.dumps(close_dict)
    return requests.put(endpoint, headers=headers, data=close_dict).json()
