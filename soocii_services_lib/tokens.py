import binascii
import json
import time

import jsonschema

from .crypter import AESCipher
from .exceptions import AccessTokenValidationError, RefreshTokenValidationError, TokenExpiredError, TokenSchemaError


class BaseToken(dict):

    _schema = {}

    def is_valid(self, age=None, raise_exception=False):
        try:
            jsonschema.validate(self, self._schema)

            if age and ('timestamp' not in self or self['timestamp'] + age < int(time.time())):
                msg = 'timestamp {} is expired'.format(self.get("timestamp"))
                raise TokenExpiredError(msg)
        except jsonschema.exceptions.ValidationError as e:
            if raise_exception:
                raise TokenSchemaError(str(e))
        except TokenExpiredError:
            if raise_exception:
                raise
        else:
            return True

        return False

class AccessToken(BaseToken):

    ROLE_USER = 'user'
    ROLE_BACKSTAGE = 'backstage'
    ROLE_SERVICE = 'service'

    _schema = {
        'definitions': {
            'basic': {
                'type': 'object',
                'properties': {
                    'timestamp': {
                        'type': 'integer'
                    }
                }
            },
            ROLE_USER: {
                'type': 'object',
                'properties': {
                    'role': {
                        'type': 'string',
                        'enum': [ROLE_USER]
                    },
                    'pid': {
                        'type': 'string'
                    },
                    'id': {
                        'type': 'integer'
                    },
                    'soocii_id': {
                        'type': 'string'
                    },
                    'uid': {
                        'type': 'string',
                        'pattern': '^[0-9a-fA-F]{32}$'
                    }
                },
                'required': ['pid', 'id', 'soocii_id', 'uid']
            },
            ROLE_BACKSTAGE: {
                'type': 'object',
                'properties': {
                    'role': {
                        'type': 'string',
                        'enum': [ROLE_BACKSTAGE]
                    },
                    'id': {
                        'type': 'integer'
                    }
                },
                'required': ['id']
            },
            ROLE_SERVICE: {
                'type': 'object',
                'properties': {
                    'role': {
                        'type': 'string',
                        'enum': [ROLE_SERVICE]
                    },
                    'name': {
                        'type': 'string'
                    }
                },
                'required': ['name']
            },
        },
        'allOf': [
            {
                '#ref': '#/definitions/basic'
            },
            {
                'oneOf': [
                    {
                        '$ref': '#/definitions/user'
                    }, {
                        '$ref': '#/definitions/backstage'
                    }, {
                        '$ref': '#/definitions/service'
                    }
                ]
            }
        ],
        'required': ['role', 'timestamp']
    }

    @property
    def role(self):
        return self.get('role')

    def is_role(self, role):
        return self.role == role


class RefreshToken(BaseToken):

    _schema = {
        'type': 'object',
        'properties': {
            'timestamp': {
                'type': 'integer'
            },
            'access_token': {
                'type': 'string'
            }
        },
        'required': ['timestamp', 'access_token']
    }


class AccessTokenCryper(object):
    age = 43200
    exception = AccessTokenValidationError
    _token_cls = AccessToken

    def __init__(self, key, age=None):
        key = binascii.unhexlify(key)
        self.cipher = AESCipher(key)
        if age:
            self.age = age

    def _encode(self, raw):
        if isinstance(raw, str):
            raw = raw.encode('utf-8')

        return self.cipher.encrypt(raw)

    def _decode(self, data):
        # convert the pre-defined secret from hex string.

        if isinstance(data, str):
            data = data.encode('utf-8')

        return self.cipher.decrypt(data)

    def dumps(self, data=None, **kwargs):
        """
        Generate token from encrypting the given data and keyword arguments. data should be a dict
        """
        if not isinstance(data, dict):
            data = {}

        data.update(kwargs)

        # append timestamp
        data.update(timestamp=int(time.time()))
        token = self._token_cls(data)
        token.is_valid(raise_exception=True)

        return self._encode(json.dumps(token))

    def loads(self, token, valid_age=True):
        """
        Load and decrypt token
        """
        try:
            token = self._token_cls(json.loads(self._decode(token).decode('utf-8')))
            token.is_valid(self.age if valid_age else None, raise_exception=True)
        except ValueError:
            raise self.exception('invalid token format')

        return token

    def _get_specific_token(role):

        def _wrapper(self, **kwargs):
            mandatory_keys = self._token_cls._schema['definitions'][role]['required']
            if any(k not in kwargs for k in mandatory_keys):
                msg = '{} are required'.format(', '.join(mandatory_keys))
                raise TokenSchemaError(msg)

            kwargs['role'] = role
            return self.dumps(kwargs).decode('utf-8')

        return _wrapper

    _get_user_token = _get_specific_token(_token_cls.ROLE_USER)
    get_backstage_token = _get_specific_token(_token_cls.ROLE_BACKSTAGE)
    get_service_token = _get_specific_token(_token_cls.ROLE_SERVICE)

    def get_user_token(self, **kwargs):
        if 'lang' not in kwargs:
            kwargs['lang'] = 'EN-US'
        return self._get_user_token(**kwargs)


class RefreshTokenCryper(AccessTokenCryper):
    age = 604800
    exception = RefreshTokenValidationError
    _token_cls = RefreshToken

    def get_token(self, access_token):
        return self.dumps({'access_token': access_token}).decode('utf-8')
