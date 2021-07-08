import hmac
import hashlib
import json
from requests import Request, Session
import time
import random
from typing import Any


class CryptocomAccount:
    def __init__(self, api_key=None, api_secret=None, passphrase=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._passphrase = passphrase
        self._endpoint = 'https://api.crypto.com/v2/'

    def _sign_request(self, path, data) -> None:
        data["api_key"] = self._api_key
        data["id"] = random.randint(1000, 10000)
        data["nonce"] = int(time.time() * 1000)
        data['method'] = path
        paramString = ""
        if data["params"]:
            for key in sorted(data['params']):
                paramString += key
                paramString += str(data['params'][key])
        sigPayload = data['method'] + str(data['id']) + data['api_key'] + paramString + str(data['nonce'])

        data['sig'] = hmac.new(bytes(str(self._api_secret), 'utf-8'),
                               msg=bytes(sigPayload, 'utf-8'),
                               digestmod=hashlib.sha256).hexdigest()
        return json.dumps(data, separators=(',', ':'))

    def _request(self, method, path, data=None, sign=False) -> Any:
        original_data = data
        if sign:
            data = self._sign_request(path, original_data)
        request = Request(method, self._endpoint + path,
                          data=data, headers={'content-type': 'application/json'})
        response = self._session.send(request.prepare())
        resp_json = response.json()
        if resp_json['code'] == 0:
            result = resp_json.get('result', {})
            return result.get('data', {}) or result
        else:
            return resp_json

    def _get(self, path, data={}, sign=False):
        return self._request('GET', path, data=data, sign=sign)

    def _post(self, path, data={}, sign=True):
        return self._request('POST', path, data=data, sign=sign)

    def get_balance(self, **kwargs):
        endpoint = 'private/get-account-summary'
        data = {}
        data['params'] = {}
        if kwargs:
            for k in sorted(kwargs):
                data['params'][k] = kwargs[k]
        return self._post(endpoint, data)['accounts']

    def get_instruments(self, **kwargs):
        endpoint = 'public/get-instruments'
        return self._get(endpoint)['instruments']

    def get_open_orders(self, **kwargs):
        end_point = 'private/get-open-orders'
        data = {}
        data['params'] = {}
        if kwargs:
            for k in sorted(kwargs):
                data['params'][k] = kwargs[k]
        return self._post(end_point, data)

    def get_trades(self, instrument_id=None, after=None, before=None, page=0, page_size=200):
        endpoint = 'private/get-trades'
        data = {}
        data['params'] = {'page_size': page_size, 'page': page}
        if instrument_id:
            data['params']['instrument_name'] = instrument_id
        if after:
            data['params']['start_ts'] = after
        if after:
            data['params']['start_ts'] = after
        if before:
            data['params']['end_ts'] = before
        return self._post(endpoint, data)['trade_list']

    def get_withdraw(self, currency=None, after=None, before=None, page=0, page_size=200):
        endpoint = 'private/get-withdrawal-history'
        data = {}
        data['params'] = {'page_size': page_size, 'page': page}
        if currency:
            data['params']['currency'] = currency
        if after:
            data['params']['start_ts'] = after
        if before:
            data['params']['end_ts'] = before
        return self._post(endpoint, data)['withdrawal_list']

    def get_deposit(self, currency=None, after=None, before=None, page=0, page_size=200):
        endpoint = 'private/get-deposit-history'
        data = {}
        data['params'] = {'page_size': page_size, 'page': page}
        if currency:
            data['params']['currency'] = currency
        if after:
            data['params']['start_ts'] = after
        if before:
            data['params']['end_ts'] = before
        return self._post(endpoint, data)['deposit_list']

    def get_margin(self, **kwargs):
        end_point = 'private/margin/get-account-summary'
        data = {}
        data['params'] = {}
        if kwargs:
            for k in sorted(kwargs):
                data['params'][k] = kwargs[k]
        return self._post(end_point, data)

    def get_margin_trade(self, instrument_id=None, after=None, before=None, page=0, page_size=200):
        endpoint = 'private/margin/get-trades'
        data = {}
        data['params'] = {'page_size': page_size, 'page': page}
        if instrument_id:
            data['params']['instrument_name'] = instrument_id
        if after:
            data['params']['start_ts'] = after
        if after:
            data['params']['start_ts'] = after
        if before:
            data['params']['end_ts'] = before
        return self._post(endpoint, data)['trade_list']

    def get_interest(self, currency=None, after=None, before=None, page=0, page_size=200):
        end_point = 'private/margin/get-interest-history'
        data = {}
        data['params'] = {'page_size': page_size, 'page': page}
        if currency:
            data['params']['currency'] = currency
        if after:
            data['params']['start_ts'] = after
        if before:
            data['params']['end_ts'] = before
        return self._post(end_point, data)['list']

    def get_liquidation(self, **kwargs):
        end_point = 'private/margin/get-liquidation-orders'
        data = {}
        data['params'] = {}
        if kwargs:
            for k in sorted(kwargs):
                data['params'][k] = kwargs[k]
        return self._post(end_point, data)

    # only for master account
    def get_subaccount(self, **kwargs):
        end_point = 'private/subaccount/get-sub-accounts'
        data = {}
        data['params'] = {}
        if kwargs:
            for k in sorted(kwargs):
                data['params'][k] = kwargs[k]
        return self._post(end_point, data)['sub_account_list']

    def get_transfers(self, sub_account_uuid, direction, currency=None,
                      after=None, before=None, page=0, page_size=200):
        end_point = 'private/subaccount/get-transfer-history'
        data = {}
        data['params'] = {'sub_account_uuid': sub_account_uuid,
                          'direction': direction,
                          'page_size': page_size, 'page': page}
        if currency:
            data['params']['currency'] = currency
        if after:
            data['params']['start_ts'] = after
        if before:
            data['params']['end_ts'] = before
        return self._post(end_point, data)
