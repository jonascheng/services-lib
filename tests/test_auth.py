import os
import uuid

from soocii_services_lib import auth

ACCESS_TOKEN_SECRET = '6ca21c5ab8a6c181f5cfb91479588e37'
REFRESH_TOKEN_SECRET = 'ea57844efdcd163c4d84b8f7bf087baf'


def test_encode_decode():
    os.environ['ACCESS_TOKEN_SECRET'] = ACCESS_TOKEN_SECRET
    os.environ['REFRESH_TOKEN_SECRET'] = REFRESH_TOKEN_SECRET

    user_uuid = uuid.uuid4()
    token = auth.generate_access_token('', '', 1, user_uuid.hex)
    decoded = auth.decode_access_token(token)

    assert decoded['uid'] == ''
    assert decoded['id'] == 1
    assert decoded['uuid'] == user_uuid.hex
