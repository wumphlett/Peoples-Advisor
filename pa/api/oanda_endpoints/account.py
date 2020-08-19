import json
import requests
from pa.api.oanda import (
    api_version,
    practice_url,
    live_url
)


def get_accounts(live, api_token):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts'.format(url=base_url, v=api_version)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_account_details(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_account_summary(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/summary'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def get_account_instruments(live, api_token, account_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/instruments'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    return requests.get(endpoint, headers=headers).json()


def patch_account_configure(live, api_token, account_id, configure):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/configuration'.format(url=base_url, v=api_version, id=account_id)
    headers = {
        'Authorization': 'Bearer {api_token}'.format(api_token=api_token),
        'Content-Type': 'application/json'
    }
    configure = json.dumps(configure)
    return requests.patch(endpoint, headers=headers, data=configure).json()


def get_account_changes(live, api_token, account_id, transaction_id):
    base_url = live_url if live else practice_url
    endpoint = '{url}/{v}/accounts/{id}/changes'.format(url=base_url, v=api_version, id=account_id)
    headers = {'Authorization': 'Bearer {api_token}'.format(api_token=api_token)}
    params = {'sinceTransactionID': transaction_id}
    return requests.get(endpoint, headers=headers, params=params).json()
