from json import dumps, loads

import requests

import config
import ncryptify_exceptions as Exceptions


def get_account(token):
    url = config.NCRYPTIFY_URL + "/admin/account"

    args = {
        'simple': 'true',
        'proxy': url,
    }
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    r = requests.get(url, headers=headers, params=args)
    if r.status_code != 200:
        raise Exceptions.AccountNotFound("Failed to fetch account")
    return loads(r.text)


def get_link_url(callback_url, token):
    url = config.NCRYPTIFY_URL + "/admin/link"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + token}
    r = requests.post(url, headers=headers, data=dumps({"callback": callback_url}))
    if r.status_code != 200:
        raise Exceptions.ErrorFetchingLinkUrl("Failed to fetch url link")
    return loads(r.text)['linkauth_url']
