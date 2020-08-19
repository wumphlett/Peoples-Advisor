import requests
from pa.api.oanda import (
    api_version,
    practice_url,
    live_url
)


def get_transactions(live, api_token, account_id, params=None):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/transactions'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers, params=params).json()


def get_transaction_details(live, api_token, account_id, transaction_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/transactions/{t_id}'.format(url=base_url, v=api_version, id=account_id, t_id=transaction_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_transactions_range(live, api_token, account_id, params):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/transactions/idrange'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers, params=params).json()


def get_transactions_since(live, api_token, account_id, params):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/transactions/sinceid'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers, params=params).json()


def get_transactions_stream(live, api_token, account_id):
    pass
    # TODO
