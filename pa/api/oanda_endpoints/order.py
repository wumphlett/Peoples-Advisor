import json
import requests
from pa.api.oanda import (
    api_version,
    practice_url,
    live_url
)


def get_orders(live, api_token, account_id, params):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/orders'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers, params=params).json()


def post_orders(live, api_token, account_id, order_dict):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/orders'.format(url=base_url, v=api_version, id=account_id)
    headers = {
        'Authorization': 'Bearer {api_token}'.format(api_token=api_token),
        'Content-Type': 'application/json'
    }
    order_dict = json.dumps(order_dict)
    return requests.post(endpoint, headers=headers, data=order_dict).json()


def get_pending_orders(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/pendingOrders'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_order_details(live, api_token, account_id, order_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/orders/{o_id}'.format(url=base_url, v=api_version, id=account_id, o_id=order_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def put_order_replacement(live, api_token, account_id, order_id, order_dict):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/orders/{o_id}'.format(url=base_url, v=api_version, id=account_id, o_id=order_id)
    headers = {
        'Authorization': 'Bearer {api_token}'.format(api_token=api_token),
        'Content-Type': 'application/json'
    }
    order_dict = json.dumps(order_dict)
    return requests.put(endpoint, headers=headers, data=order_dict).json()


def put_order_cancel(live, api_token, account_id, order_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/orders/{o_id}/cancel'.format(url=base_url, v=api_version, id=account_id,
                                                                     o_id=order_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.put(endpoint, headers=headers).json()
