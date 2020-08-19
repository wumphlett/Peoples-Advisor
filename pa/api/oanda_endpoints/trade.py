import json
import requests
from pa.api.oanda import (
    api_version,
    practice_url,
    live_url
)


def get_trades(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/trades'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_open_trades(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/openTrades'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_trade_details(live, api_token, account_id, trade_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/trades/{t_id}'.format(url=base_url, v=api_version, id=account_id, t_id=trade_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def put_close_trade(live, api_token, account_id, trade_id, close_dict):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/trades/{t_id}'.format(url=base_url, v=api_version, id=account_id, t_id=trade_id)
    headers = {
        'Authorization': 'Bearer {api_token}'.format(api_token=api_token),
        'Content-Type': 'application/json'
    }
    close_dict = json.dumps(close_dict)
    return requests.put(endpoint, headers=headers, data=close_dict).json()


def put_modify_trade_orders(live, api_token, account_id, trade_id, params):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/trades/{t_id}/orders'.format(url=base_url, v=api_version, id=account_id, t_id=trade_id)
    headers = {
        'Authorization': 'Bearer {api_token}'.format(api_token=api_token),
        'Content-Type': 'application/json'
    }
    params = json.dumps(params)
    return requests.put(endpoint, headers=headers, data=params).json()
