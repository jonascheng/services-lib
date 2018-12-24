import json
import os
import time

from .exceptions import BaseValidationError
from .tokens import AccessTokenCryper, RefreshTokenCryper


class AccessTokenValidationFail(Exception):
    pass


class RefreshTokenValidationFail(Exception):
    pass


def _get_token_info():
    return {
        'access': {
            'secret_key': os.getenv('ACCESS_TOKEN_SECRET', 'None'),
            'age': 43200,
            'exception': AccessTokenValidationFail
        },
        'refresh': {
            'secret_key': os.getenv('REFRESH_TOKEN_SECRET', 'None'),
            'age': 604800,
            'exception': RefreshTokenValidationFail
        },
    }


def decode_access_token(token, check_timestamp=True):
    if type(token) is str:
        token = token.encode('utf-8')
    key_info = _get_token_info()['access']
    cryper = AccessTokenCryper(key_info['secret_key'], key_info['age'])

    try:
        # compatible leagcy token, wihtout verify schema
        token = cryper._token_cls(json.loads(cryper._decode(token).decode('utf-8')))
    except ValueError:
        raise key_info['exception']

    if check_timestamp and token['timestamp'] + key_info['age'] < int(time.time()):
        raise key_info['exception']

    return token


def generate_access_token(pid, uid, id, uuid, lang='EN-US', tz=8, device_type='', soocii_id=''):
    key_info = _get_token_info()['access']
    cryper = AccessTokenCryper(key_info['secret_key'], key_info['age'])
    return cryper.get_user_token(pid=pid, uid=uid, id=id, lang=lang, tz=tz, device_type=device_type, soocii_id=soocii_id).encode('utf-8')


def generate_refresh_token(access_token):
    key_info = _get_token_info()['refresh']
    cryper = RefreshTokenCryper(key_info['secret_key'], key_info['age'])
    return cryper.get_token(access_token).encode('utf-8')
