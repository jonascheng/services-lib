import mock
import os
import pytest
import uuid

from soocii_services_lib import auth, tokens
from soocii_services_lib.exceptions import AccessTokenValidationError, RefreshTokenValidationError, TokenExpiredError, TokenSchemaError

ACCESS_TOKEN_SECRET = '6ca21c5ab8a6c181f5cfb91479588e37'
REFRESH_TOKEN_SECRET = 'ea57844efdcd163c4d84b8f7bf087baf'


def test_encode_decode():
    os.environ['ACCESS_TOKEN_SECRET'] = ACCESS_TOKEN_SECRET
    os.environ['REFRESH_TOKEN_SECRET'] = REFRESH_TOKEN_SECRET

    device_uuid = uuid.uuid4()
    token = auth.generate_access_token('MP01', device_uuid.hex, 1, '', soocii_id='fake_soocii_id')
    decoded = auth.decode_access_token(token)

    assert decoded['uid'] == device_uuid.hex
    assert decoded['id'] == 1
    assert decoded['role'] == 'user'


@pytest.fixture
def access_token_cryper():
    return tokens.AccessTokenCryper(ACCESS_TOKEN_SECRET)


@pytest.fixture
def refresh_token_cryper():
    return tokens.RefreshTokenCryper(REFRESH_TOKEN_SECRET)


class TestAccessTokenCryper(object):

    def tests_get_user_token(self, access_token_cryper):

        uid = uuid.uuid4().hex
        cipher = access_token_cryper.get_user_token(pid='MP01', id=1, uid=uid, soocii_id='fake_soocii_id', device_type='IOS')

        data = access_token_cryper.loads(cipher)
        assert data == {
                'role': 'user',
                'id': 1,
                'pid': 'MP01',
                'uid': uid,
                'soocii_id': 'fake_soocii_id',
                'lang': 'EN-US',
                'device_type': 'IOS',
                'timestamp': mock.ANY}


    def tests_token_expired(self, access_token_cryper):

        with mock.patch('time.time', return_value=0):
            cipher = access_token_cryper.get_user_token(pid='MP01', id=1, uid=uuid.uuid4().hex, soocii_id='fake_soocii_id', device_type='IOS')

        with pytest.raises(TokenExpiredError):
            access_token_cryper.loads(cipher)

    def tests_token_mismatch_schema(self, access_token_cryper):

        with pytest.raises(TokenSchemaError):
            access_token_cryper.get_user_token(pid='MP01', id=1, uid='0000', soocii_id='fake_soocii_id', device_type='IOS')

    def tests_token_malformed(self, access_token_cryper):

        with pytest.raises(AccessTokenValidationError):
            access_token_cryper.loads('abacaada')

    def tests_get_backstage_token(self, access_token_cryper):

        cipher = access_token_cryper.get_backstage_token(id=1)

        data = access_token_cryper.loads(cipher)
        assert data == {'role': 'backstage', 'id': 1, 'timestamp': mock.ANY}

    def tests_get_service_token(self, access_token_cryper):

        cipher = access_token_cryper.get_service_token(name='streaming')

        data = access_token_cryper.loads(cipher)
        assert data == {'role': 'service', 'name': 'streaming', 'timestamp': mock.ANY}


class TestRefreshTokenCryper(object):

    def tests_refresh_token(self, refresh_token_cryper):
        refresh_token = refresh_token_cryper.get_token('fake_access_token')
        data = refresh_token_cryper.loads(refresh_token)
        assert data['access_token'] == 'fake_access_token'

    def tests_token_expired(self, access_token_cryper, refresh_token_cryper):

        with mock.patch('time.time', return_value=0):
            refresh_token = refresh_token_cryper.get_token('fake_access_token')

        with pytest.raises(TokenExpiredError):
            refresh_token_cryper.loads(refresh_token)

    def tests_token_malformed(self, refresh_token_cryper):

        with pytest.raises(RefreshTokenValidationError):
            refresh_token_cryper.loads('abacaada')

