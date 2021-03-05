import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
import apiKey

access_key = apiKey.access_key
secret_key = apiKey.secret_key
server_url = 'https://api.upbit.com'


def GetAuth_Token():

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}
    res = requests.get(server_url + "/v1/accounts", headers=headers).json()

    return res


def getCandle(unit):
    url = 'https://api.upbit.com/v1/candles/minutes/{}'.format(unit)
    queryString = {"market": "KRW-BTC", "count": str(unit)}
    response = requests.request("GET", url, params=queryString)

    return response.text


def possibleOrder():
    query = {
        'market': 'KRW-XRP',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/orders/chance",
                       params=query, headers=headers)

    return res.json()


def makeOrder():
    query = {
        'market': 'KRW-XRP',
        'side': 'bid',
        'volume': '100',
        'price': '520',
        'ord_type': 'limit',
    }

    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/orders",
                        params=query, headers=headers).json()

    orderID = res['uuid']
    return (res, orderID)


def cancelOrder():
    query = {
        'uuid': '69387ce6-39c4-451f-a656-7a19557dba39',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.delete(server_url + "/v1/order",
                          params=query, headers=headers)

    print(res.json())


cancelOrder()
